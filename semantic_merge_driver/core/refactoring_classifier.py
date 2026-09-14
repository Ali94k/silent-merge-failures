"""RefactoringClusterClassifier: maps a 3-way merge to a single Cluster label.

Per `docs/plans/rm2-integration.md` Phase R4a. The classifier runs RM2 on
(base, ours) and (base, theirs), unions the detected refactoring-type sets,
maps each type to its merge-difficulty cluster (frozenset for compound types),
unions all cluster contributions, and returns the highest-precedence cluster.

The 7 clusters are grouped by *kind of 3-way merge difficulty* (what makes
each refactoring hard for a line-based merger), not by lexical type-name
similarity. Precedence (hardest-for-line-merge first):

    MIGRATE_DECL > INTRA_BODY > SYMBOL_CASCADE > CONTAINER_MOVE
    > HIERARCHY_RESHAPE > LOCAL_DECL_EDIT > NONE

Authoritative source for the 98 RefactoringType enum constants:
`org.refactoringminer.api.RefactoringType` inside
`merge-tools/refactoring-miner:2.4.0`. Keys in TYPE_TO_CLUSTERS are the
display names (RM2 JSON `type` field), not the enum identifiers.

Fail-closed: any RM2 failure (subprocess error, missing image, non-zero exit,
malformed JSON, timeout) returns Cluster.NONE — which routes to the Mergiraf
default in R4b. Never raises. Matches the β-stage fail-closed pattern
established in `core/backends/`.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from enum import Enum
from pathlib import Path


RM2_IMAGE = "merge-tools/refactoring-miner:2.4.0"
RM2_TIMEOUT_SECONDS = 120


class Cluster(str, Enum):
    """Merge-difficulty cluster. See module docstring for criterion + precedence."""

    MIGRATE_DECL = "MIGRATE_DECL"
    """Whole declaration body relocates across methods/classes/hierarchy axis."""

    INTRA_BODY = "INTRA_BODY"
    """Sub-method granular restructuring; effects don't escape one method body."""

    SYMBOL_CASCADE = "SYMBOL_CASCADE"
    """Identifier or scope change cascades to all use sites."""

    CONTAINER_MOVE = "CONTAINER_MOVE"
    """Class/package/folder relocates; cascade is to import statements."""

    HIERARCHY_RESHAPE = "HIERARCHY_RESHAPE"
    """Inheritance graph itself changes (not just movement along it)."""

    LOCAL_DECL_EDIT = "LOCAL_DECL_EDIT"
    """Decoration at the declaration site (annotations, modifiers, access)."""

    NONE = "NONE"
    """No refactoring detected, or unknown type."""


PRECEDENCE: tuple[Cluster, ...] = (
    Cluster.MIGRATE_DECL,
    Cluster.INTRA_BODY,
    Cluster.SYMBOL_CASCADE,
    Cluster.CONTAINER_MOVE,
    Cluster.HIERARCHY_RESHAPE,
    Cluster.LOCAL_DECL_EDIT,
    Cluster.NONE,
)


# RM2 2.4.0 RefactoringType.getDisplayName() → cluster contributions.
# Compound types (e.g., "Move And Rename Method") map to a frozenset; the
# precedence rule resolves the union of all contributions across both branches.
TYPE_TO_CLUSTERS: dict[str, frozenset[Cluster]] = {
    # --- MIGRATE_DECL: whole-declaration mobility ---
    "Extract Method": frozenset({Cluster.MIGRATE_DECL}),
    "Inline Method": frozenset({Cluster.MIGRATE_DECL}),
    "Move Method": frozenset({Cluster.MIGRATE_DECL}),
    "Move And Rename Method": frozenset({Cluster.MIGRATE_DECL, Cluster.SYMBOL_CASCADE}),
    "Pull Up Method": frozenset({Cluster.MIGRATE_DECL}),
    "Push Down Method": frozenset({Cluster.MIGRATE_DECL}),
    "Extract And Move Method": frozenset({Cluster.MIGRATE_DECL}),
    "Move And Inline Method": frozenset({Cluster.MIGRATE_DECL}),
    "Merge Method": frozenset({Cluster.MIGRATE_DECL}),
    "Split Method": frozenset({Cluster.MIGRATE_DECL}),
    "Move Attribute": frozenset({Cluster.MIGRATE_DECL}),
    "Move And Rename Attribute": frozenset({Cluster.MIGRATE_DECL, Cluster.SYMBOL_CASCADE}),
    "Pull Up Attribute": frozenset({Cluster.MIGRATE_DECL}),
    "Push Down Attribute": frozenset({Cluster.MIGRATE_DECL}),
    "Replace Attribute": frozenset({Cluster.MIGRATE_DECL}),
    "Extract Attribute": frozenset({Cluster.MIGRATE_DECL}),
    "Inline Attribute": frozenset({Cluster.MIGRATE_DECL}),
    "Extract Class": frozenset({Cluster.MIGRATE_DECL}),
    "Extract Subclass": frozenset({Cluster.MIGRATE_DECL, Cluster.HIERARCHY_RESHAPE}),
    "Extract Superclass": frozenset({Cluster.MIGRATE_DECL, Cluster.HIERARCHY_RESHAPE}),
    "Extract Interface": frozenset({Cluster.MIGRATE_DECL, Cluster.HIERARCHY_RESHAPE}),
    "Convert Anonymous Class to Type": frozenset({Cluster.MIGRATE_DECL, Cluster.HIERARCHY_RESHAPE}),
    "Merge Class": frozenset({Cluster.MIGRATE_DECL, Cluster.CONTAINER_MOVE}),
    "Split Class": frozenset({Cluster.MIGRATE_DECL, Cluster.CONTAINER_MOVE}),

    # --- INTRA_BODY: sub-method restructuring ---
    "Extract Variable": frozenset({Cluster.INTRA_BODY}),
    "Inline Variable": frozenset({Cluster.INTRA_BODY}),
    "Rename Variable": frozenset({Cluster.INTRA_BODY}),
    "Rename Parameter": frozenset({Cluster.INTRA_BODY}),
    "Merge Variable": frozenset({Cluster.INTRA_BODY}),
    "Split Variable": frozenset({Cluster.INTRA_BODY}),
    "Change Variable Type": frozenset({Cluster.INTRA_BODY}),
    "Split Conditional": frozenset({Cluster.INTRA_BODY}),
    "Invert Condition": frozenset({Cluster.INTRA_BODY}),
    "Merge Conditional": frozenset({Cluster.INTRA_BODY}),
    "Merge Catch": frozenset({Cluster.INTRA_BODY}),
    "Replace Loop With Pipeline": frozenset({Cluster.INTRA_BODY}),
    "Replace Pipeline With Loop": frozenset({Cluster.INTRA_BODY}),
    "Replace Anonymous With Lambda": frozenset({Cluster.INTRA_BODY}),

    # --- SYMBOL_CASCADE: identifier/scope/signature change cascading to use sites ---
    "Rename Class": frozenset({Cluster.SYMBOL_CASCADE}),
    "Rename Method": frozenset({Cluster.SYMBOL_CASCADE}),
    "Rename Attribute": frozenset({Cluster.SYMBOL_CASCADE}),
    "Add Parameter": frozenset({Cluster.SYMBOL_CASCADE}),
    "Remove Parameter": frozenset({Cluster.SYMBOL_CASCADE}),
    "Reorder Parameter": frozenset({Cluster.SYMBOL_CASCADE}),
    "Change Return Type": frozenset({Cluster.SYMBOL_CASCADE}),
    "Change Parameter Type": frozenset({Cluster.SYMBOL_CASCADE}),
    "Change Attribute Type": frozenset({Cluster.SYMBOL_CASCADE}),
    "Merge Parameter": frozenset({Cluster.SYMBOL_CASCADE}),
    "Merge Attribute": frozenset({Cluster.SYMBOL_CASCADE}),
    "Split Parameter": frozenset({Cluster.SYMBOL_CASCADE}),
    "Split Attribute": frozenset({Cluster.SYMBOL_CASCADE}),
    "Replace Variable With Attribute": frozenset({Cluster.SYMBOL_CASCADE}),
    "Replace Attribute With Variable": frozenset({Cluster.SYMBOL_CASCADE}),
    "Parameterize Variable": frozenset({Cluster.SYMBOL_CASCADE}),
    "Localize Parameter": frozenset({Cluster.SYMBOL_CASCADE}),
    "Parameterize Attribute": frozenset({Cluster.SYMBOL_CASCADE}),
    "Encapsulate Attribute": frozenset({Cluster.SYMBOL_CASCADE}),
    "Add Thrown Exception Type": frozenset({Cluster.SYMBOL_CASCADE}),
    "Remove Thrown Exception Type": frozenset({Cluster.SYMBOL_CASCADE}),
    "Change Thrown Exception Type": frozenset({Cluster.SYMBOL_CASCADE}),

    # --- CONTAINER_MOVE: class/package/folder relocation (import cascade) ---
    "Move Class": frozenset({Cluster.CONTAINER_MOVE}),
    "Move And Rename Class": frozenset({Cluster.CONTAINER_MOVE, Cluster.SYMBOL_CASCADE}),
    "Move Source Folder": frozenset({Cluster.CONTAINER_MOVE}),
    "Move Package": frozenset({Cluster.CONTAINER_MOVE}),
    "Rename Package": frozenset({Cluster.CONTAINER_MOVE, Cluster.SYMBOL_CASCADE}),
    "Split Package": frozenset({Cluster.CONTAINER_MOVE}),
    "Merge Package": frozenset({Cluster.CONTAINER_MOVE}),

    # --- HIERARCHY_RESHAPE: inheritance graph change (not movement along it) ---
    "Collapse Hierarchy": frozenset({Cluster.HIERARCHY_RESHAPE}),
    "Introduce Polymorphism": frozenset({Cluster.HIERARCHY_RESHAPE}),
    "Change Type Declaration Kind": frozenset({Cluster.HIERARCHY_RESHAPE}),

    # --- LOCAL_DECL_EDIT: localised declaration-site decoration ---
    "Add Method Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Remove Method Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Modify Method Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Add Attribute Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Remove Attribute Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Modify Attribute Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Add Class Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Remove Class Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Modify Class Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Add Parameter Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Remove Parameter Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Modify Parameter Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Add Variable Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Remove Variable Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Modify Variable Annotation": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Change Method Access Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Change Attribute Access Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Change Class Access Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Add Method Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Remove Method Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Add Attribute Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Remove Attribute Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Add Variable Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Remove Variable Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Add Parameter Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Remove Parameter Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Add Class Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
    "Remove Class Modifier": frozenset({Cluster.LOCAL_DECL_EDIT}),
}


def _resolve_precedence(clusters: set[Cluster]) -> Cluster:
    """Pick the highest-priority cluster from a non-empty set."""
    for c in PRECEDENCE:
        if c in clusters:
            return c
    return Cluster.NONE  # defensive; PRECEDENCE covers all enum values


class RefactoringClusterClassifier:
    """Classify a 3-way merge by RM2-detected refactoring cluster.

    Stateless after construction. Safe to instantiate per merge or hold a
    long-lived instance; both are fine.
    """

    def __init__(self, image: str = RM2_IMAGE, timeout_seconds: int = RM2_TIMEOUT_SECONDS):
        self.image = image
        self.timeout_seconds = timeout_seconds

    def cluster(self, base_path: str, ours_path: str, theirs_path: str) -> Cluster:
        """Return the merge-difficulty cluster for a 3-way merge.

        Runs RM2 on (base, ours) and (base, theirs), unions detected types,
        maps each to its cluster contributions, returns the highest-precedence
        cluster across the union.

        On any RM2 failure (missing Docker, missing image, subprocess error,
        non-zero exit, malformed JSON, timeout) returns Cluster.NONE rather
        than raising. NONE routes to the Mergiraf default in R4b.
        """
        types_ours = self._detect_pair(base_path, ours_path)
        types_theirs = self._detect_pair(base_path, theirs_path)
        types = types_ours | types_theirs

        if not types:
            return Cluster.NONE

        contributions: set[Cluster] = set()
        for rtype in types:
            contributions |= TYPE_TO_CLUSTERS.get(rtype, frozenset({Cluster.NONE}))

        return _resolve_precedence(contributions)

    def _detect_pair(self, left_path: str, right_path: str) -> set[str]:
        """Run RM2 on a two-file pair, return the set of detected type display names.

        Stages each file at its basename inside two single-file temp dirs
        (file-level mode per docs/plans/rm2-integration-recon.md §5). Returns
        an empty set on any failure — the caller treats empty as "no signal"
        and (if both pairs return empty) returns Cluster.NONE.
        """
        with tempfile.TemporaryDirectory() as tmp:
            left_dir = Path(tmp) / "left"
            right_dir = Path(tmp) / "right"
            left_dir.mkdir()
            right_dir.mkdir()
            basename = Path(left_path).name
            try:
                shutil.copyfile(left_path, left_dir / basename)
                shutil.copyfile(right_path, right_dir / basename)
            except OSError as e:
                print(f"RefactoringClusterClassifier: staging failed: {e}", file=sys.stderr)
                return set()

            try:
                proc = subprocess.run(
                    [
                        "docker", "run", "--rm", "--platform", "linux/amd64",
                        "-v", f"{left_dir}:/data/left:ro",
                        "-v", f"{right_dir}:/data/right:ro",
                        self.image,
                        "/data/left", "/data/right",
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=self.timeout_seconds,
                )
            except (FileNotFoundError, OSError, subprocess.SubprocessError) as e:
                print(
                    f"RefactoringClusterClassifier: subprocess error: {e}\n"
                    f"  Hint: ensure Docker is running and the image exists:\n"
                    f"    docker image inspect {self.image}",
                    file=sys.stderr,
                )
                return set()

            if proc.returncode != 0:
                print(
                    f"RefactoringClusterClassifier: docker run exited rc={proc.returncode}.\n"
                    f"  stderr: {proc.stderr.strip() or '(empty)'}",
                    file=sys.stderr,
                )
                return set()

            try:
                payload = json.loads(proc.stdout)
            except json.JSONDecodeError as e:
                print(
                    f"RefactoringClusterClassifier: malformed RM2 JSON: {e}\n"
                    f"  stdout head: {proc.stdout[:200]!r}",
                    file=sys.stderr,
                )
                return set()

            return {r["type"] for r in payload.get("refactorings", []) if "type" in r}
