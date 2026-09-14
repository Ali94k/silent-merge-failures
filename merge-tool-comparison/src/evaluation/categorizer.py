"""Scenario → merge-difficulty cluster categorizer (Phase R2).

Turns the RM2 refactoring tags written by `tools/rm2_tag.py` (Phase R1) into a
single merge-difficulty cluster label per scenario, so `compute_metrics` can
pivot tool performance by cluster (resolves ISSUES.md #3).

The cluster is computed from the **union of the `ours` and `theirs` file-level
refactoring sets** — exactly what the runtime dispatcher
(`semantic_merge_driver` `AutoBackend` → `RefactoringClusterClassifier.cluster`)
computes. This is a deliberate deviation from rm2-integration.md §R1, which
named the `resolution` axis: the dispatcher never sees the resolution, and
bucketing by the artifact that *defines* TP/FP would be quasi-circular. Pivoting
on `ours∪theirs` is what makes the R2 evidence able to justify/refute the
deferred W5/S2 routing elifs.

PARITY-TESTED COPY. `Cluster`, `PRECEDENCE`, and `TYPE_TO_CLUSTERS` are a
verbatim copy of the single source of truth,
`semantic_merge_driver/core/refactoring_classifier.py` (Phase R4a). The two
projects do not share a package, so this is a copy rather than a cross-project
import; `tests/test_categorizer.py::test_taxonomy_parity` imports the driver
module by file path and fails loudly if the two ever drift. Do not edit the
taxonomy here without updating the source and re-running that test.
"""
from __future__ import annotations

from enum import Enum


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


def cluster_of(types_ours: list[str], types_theirs: list[str]) -> str:
    """Merge-difficulty cluster for a scenario, from its RM2 tags.

    Unions the `ours` and `theirs` file-level refactoring-type names, maps each
    to its cluster contributions (unknown / unmapped type → NONE), and resolves
    precedence over the union. Empty union → "NONE". Returns the cluster's
    string value (suitable as the `category` passed to `compute_metrics`).

    Mirrors `RefactoringClusterClassifier.cluster()` semantics on pre-extracted
    tags rather than invoking RM2, so the empirical cluster equals the cluster
    the runtime dispatcher would assign for the same inputs.
    """
    types = set(types_ours) | set(types_theirs)
    if not types:
        return Cluster.NONE.value

    contributions: set[Cluster] = set()
    for rtype in types:
        contributions |= TYPE_TO_CLUSTERS.get(rtype, frozenset({Cluster.NONE}))

    return _resolve_precedence(contributions).value
