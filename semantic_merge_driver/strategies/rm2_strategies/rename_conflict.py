r"""RM2RenameConflict — rename + stale-reference detector (R3, v2).

Per `docs/plans/rm2-integration.md` Phase R3; v2 widened 2026-06-11 by the
Stage-B evidence (ISSUES #29 pilot: 8/13 attributable real-world silent
failures were rename/declaration-change interference, none of them the v1
within-file Method/Class shape).

Pipeline:
    1. RM2 file-level on (base, merged) — and, when the driver supplies the
       parents (Phase-2a widened `analyze`), also on (base, ours) and
       (base, theirs): a rename intended by ONE branch is invisible to
       (base, merged) when the merge kept the other branch's declaration.
    2. Filter detected refactorings to renames:
         call-lane: {Rename Method, Rename Class}
              codeElement shape "public oldName(a int, b int) : int" / FQN
         var-lane:  {Rename Variable, Rename Parameter, Rename Attribute}
              codeElement shape "name : type"   (probed against the
              merge-tools/refactoring-miner:2.4.0 image, 2026-06-11; note the
              image does NOT report Rename Attribute for static-final
              constants — that shape is covered by JoernUnresolvedReference)
    3. For each rename (old → new), require the MERGED file to show a mixed
       state: `new` must appear at all (rename at least partly applied —
       guards against flagging merges that wholly dropped one branch's
       rename, which are name-consistent), and then:
         call-lane: flag merged lines matching `\b<old>\s*\(` (v1 rule).
         var-lane:  flag merged lines matching `\b<old>\b` (comments/strings
              stripped first), ONLY when the merged file no longer declares
              `old` — if a declaration survives, scope-correct analysis is
              needed and that case belongs to JoernUnresolvedReference.
    4. Each match → Issue. Any match → is_clean=False.

Scope: file-level only. Cross-file stale callers and renames of EXTERNAL
APIs (callers-only changes — RM2 sees no declaration) remain out of scope;
both occurred in the pilot (nysenate, cloudfoundry) and are documented misses.

Fail-closed on any RM2 failure (missing Docker, missing image, subprocess
error, non-zero exit, malformed JSON, timeout) AND on a missing `base_content`
input. Matches the β-stage pattern from `core/backends/` and
`core/refactoring_classifier.py`.
"""
from __future__ import annotations

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, List, Optional

from core.interfaces import AnalysisResult, Issue, MergeStrategy


RM2_IMAGE = "merge-tools/refactoring-miner:2.4.0"
RM2_TIMEOUT_SECONDS = 120
RENAME_TYPES = frozenset({"Rename Method", "Rename Class"})
VAR_RENAME_TYPES = frozenset({"Rename Variable", "Rename Parameter", "Rename Attribute"})


class RM2RenameConflictStrategy(MergeStrategy):
    """Detect renamed declarations whose old name still has callers in the merged file."""

    @property
    def name(self) -> str:
        return "RM2RenameConflict"

    def __init__(self, image: str = RM2_IMAGE, timeout_seconds: int = RM2_TIMEOUT_SECONDS):
        self.image = image
        self.timeout_seconds = timeout_seconds

    def analyze(self, file_path: str, base_content: Optional[str] = None,
                ours_content: Optional[str] = None, theirs_content: Optional[str] = None) -> AnalysisResult:
        """Flag stale references to renamed identifiers in the merged file.

        Runs RM2 on (base, merged) always, plus (base, ours) / (base, theirs)
        when the parents are supplied (per-branch renames — visible even when
        the merge kept the other branch's declaration). See module docstring
        for the v2 flag rules.

        Returns:
            is_clean=True if no renames or no stale references; is_clean=False
            with one Issue per stale site. Fail-closed (is_clean=False with a
            CRITICAL "inconclusive" Issue) on any RM2 failure or missing
            base_content.
        """
        if base_content is None:
            return self._inconclusive("base_content not provided; cannot run (base, merged) RM2")

        try:
            merged_text = Path(file_path).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            return self._inconclusive(f"could not read merged file {file_path}: {e}")

        basename = Path(file_path).name
        renames: dict[tuple[str, str, str], bool] = {}  # key -> seen in (base, merged)
        comparisons = [("merged", merged_text)]
        for label, content in (("ours", ours_content), ("theirs", theirs_content)):
            if content is not None:
                comparisons.append((label, content))
        for label, right_text in comparisons:
            extracted = self._rm2_renames(base_content, right_text, basename)
            if extracted is None:
                return self._inconclusive(f"RM2 invocation failed on (base, {label}); see stderr for details")
            for key in extracted:
                renames[key] = renames.get(key, False) or (label == "merged")

        if not renames:
            return AnalysisResult(is_clean=True, issues=[])

        stripped = _strip_comments_and_strings(merged_text)
        issues: List[Issue] = []
        for (old_name, new_name, lane), from_merged in renames.items():
            # Mixed-state guard for PARENT-ONLY renames: a merge that wholly
            # dropped one branch's rename is name-consistent — only flag when
            # the new name made it into the merged file. Renames detected on
            # (base, merged) carry that proof by construction.
            if not from_merged and not re.search(rf"\b{re.escape(new_name)}\b", stripped):
                continue
            if lane == "call":
                issues.extend(self._scan_stale_callers(merged_text, old_name, new_name))
            else:
                issues.extend(self._scan_stale_var_refs(stripped, old_name, new_name))

        return AnalysisResult(is_clean=(not issues), issues=issues)

    # --- internals ---

    def _rm2_renames(self, left_content: str, right_text: str, basename: str) -> Optional[list]:
        """Run RM2 file-level on (left, right); extract rename tuples.

        Returns a list of (old_name, new_name, lane) with lane in
        {"call", "var"}, or None on any failure (caller fail-closes).
        """
        refactorings = self._run_rm2_pair(left_content, right_text, basename)
        if refactorings is None:
            return None
        out: List[tuple[str, str, str]] = []
        for r in refactorings:
            rtype = r.get("type")
            if rtype in RENAME_TYPES:
                lane = "call"
            elif rtype in VAR_RENAME_TYPES:
                lane = "var"
            else:
                continue
            old_name = _extract_identifier(r, side="leftSideLocations")
            new_name = _extract_identifier(r, side="rightSideLocations")
            if old_name and new_name and old_name != new_name:
                out.append((old_name, new_name, lane))
        return out

    def _run_rm2_pair(self, left_content: str, right_content: str, basename: str) -> Optional[list]:
        """Run RM2 file-level on a (left, right) content pair. Returns the
        refactorings list, or None on any failure (caller fail-closes)."""
        with tempfile.TemporaryDirectory() as tmp:
            left_dir = Path(tmp) / "left"
            right_dir = Path(tmp) / "right"
            left_dir.mkdir()
            right_dir.mkdir()
            try:
                (left_dir / basename).write_text(left_content, encoding="utf-8")
                (right_dir / basename).write_text(right_content, encoding="utf-8")
            except OSError as e:
                _eprint(f"RM2RenameConflict: staging failed: {e}")
                return None

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
                _eprint(
                    f"RM2RenameConflict: subprocess error: {e}\n"
                    f"  Hint: ensure Docker is running and the image exists:\n"
                    f"    docker image inspect {self.image}"
                )
                return None

            if proc.returncode != 0:
                _eprint(
                    f"RM2RenameConflict: docker run exited rc={proc.returncode}.\n"
                    f"  stderr: {proc.stderr.strip() or '(empty)'}"
                )
                return None

            try:
                payload = json.loads(proc.stdout)
            except json.JSONDecodeError as e:
                _eprint(
                    f"RM2RenameConflict: malformed RM2 JSON: {e}\n"
                    f"  stdout head: {proc.stdout[:200]!r}"
                )
                return None

            return payload.get("refactorings", [])

    def _scan_stale_callers(self, merged_text: str, old_name: str, new_name: str) -> Iterable[Issue]:
        """Yield one Issue per line containing `\\b<old_name>\\s*\\(`."""
        pattern = re.compile(rf"\b{re.escape(old_name)}\s*\(")
        for line_idx, line in enumerate(merged_text.split("\n"), 1):
            if pattern.search(line):
                yield Issue(
                    line_number=line_idx,
                    severity="CRITICAL",
                    message=(
                        f"Stale caller of renamed identifier: '{old_name}' "
                        f"(renamed to '{new_name}') still referenced at this line."
                    ),
                    strategy_name=self.name,
                )

    def _scan_stale_var_refs(self, stripped_text: str, old_name: str, new_name: str) -> Iterable[Issue]:
        """Yield one Issue per line referencing renamed variable/field `old_name`.

        Only fires when the merged file no longer DECLARES `old_name` — a
        surviving declaration means name resolution needs real scope analysis
        (that case belongs to JoernUnresolvedReference). `stripped_text` must
        have comments/strings removed so prose mentions can't false-positive.
        """
        if _DECL_GUARD(old_name).search(stripped_text):
            return
        # `(?!\s*\()` — skip call sites: variables are never callable in Java,
        # so `old(...)` is a same-named METHOD, not the renamed variable.
        # (Post-fix defect 1, Stage C R1: 3 control FPs — aerospike,
        # cloudfoundry ×2 — from a renamed variable sharing a method's name.)
        pattern = re.compile(rf"\b{re.escape(old_name)}\b(?!\s*\()")
        for line_idx, line in enumerate(stripped_text.split("\n"), 1):
            if pattern.search(line):
                yield Issue(
                    line_number=line_idx,
                    severity="CRITICAL",
                    message=(
                        f"Stale reference to renamed variable/field: '{old_name}' "
                        f"(renamed to '{new_name}') still referenced at this line "
                        f"but no longer declared in this file."
                    ),
                    strategy_name=self.name,
                )

    def _inconclusive(self, reason: str) -> AnalysisResult:
        return AnalysisResult(
            is_clean=False,
            issues=[Issue(
                line_number=0,
                severity="CRITICAL",
                message=f"RM2RenameConflict analysis inconclusive: {reason}",
                strategy_name=self.name,
            )],
        )


def _extract_identifier(refactoring: dict, side: str) -> Optional[str]:
    """Pull the bare identifier from `refactoring[side][0].codeElement`.

    Verified shapes (via image-gated probes against
    `merge-tools/refactoring-miner:2.4.0`, see tests; var-lane probed
    2026-06-11):
        Rename Method: codeElement is the method declaration, e.g.
            "public oldName(a int, b int) : int"
        Rename Class: codeElement is the fully-qualified class name, e.g.
            "com.example.OldName"
        Rename Variable / Parameter / Attribute: "name : type", e.g.
            "count : int"

    Extraction rule (handles all shapes):
        1. Take everything before the first `(` (no-op for Class/var-likes).
        2. If a ` : ` remains, take everything before it (strips the var-like
           type; no-op for Method, whose colon sits after the paren part).
        3. Take the last whitespace-separated token (drops modifiers for Method).
        4. Take the last `.`-separated component (strips FQN package for Class).

    Returns None if the structure is unexpected — caller skips the rename.
    """
    locations = refactoring.get(side) or []
    if not locations:
        return None
    code_element = locations[0].get("codeElement", "")
    if not code_element:
        return None
    before_paren = code_element.split("(", 1)[0]
    before_colon = before_paren.split(" : ", 1)[0]
    tokens = before_colon.split()
    if not tokens:
        return None
    return tokens[-1].rsplit(".", 1)[-1]


def _DECL_GUARD(name: str) -> re.Pattern:
    """Declaration-of-`name` heuristic: a type-ish token directly before the
    identifier, followed by `=`/`;`/`,`/`)`/`:` (covers locals, fields,
    params, enhanced-for) — or `name` as a lambda parameter.

    Post-fix round 2 (both shapes measured by the #29 post-fix run):
    - `?` added to the type charclass — generics wildcards
      (`Class<? extends Map<?, ?>> mapType = ...`) blinded the guard (podam).
    - lambda-parameter alternation — `request ->`, `request) ->`,
      `(request, conn) ->` declare the name with no type prefix
      (cloudfoundry). A lambda-param occurrence means the name IS declared
      in the file; scope questions stay JoernUnresolvedReference territory.
    """
    n = re.escape(name)
    return re.compile(
        rf"[A-Za-z_$][\w$<>\[\],.?\s]*?\s+{n}\s*[=;,):]"
        rf"|\b{n}\s*(?:(?:,[\w\s,]*)?\)\s*)?->"
    )


def _strip_comments_and_strings(text: str) -> str:
    """Crude removal of string/char literals and comments (newline-preserving)
    so var-lane reference scans can't fire on prose mentions."""
    text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
    # `\n` excluded from the char-literal class: a real char literal never
    # spans lines, and without this an apostrophe inside not-yet-stripped
    # Javadoc pairs with a later apostrophe and swallows the code between.
    # (Post-fix defect 2, Stage C R1: 1 control FP — podam — where this
    # blinded the declaration guard and misattributed match lines.)
    text = re.sub(r"'(?:\\.|[^'\\\n])*'", "''", text)
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def _eprint(msg: str) -> None:
    import sys
    print(msg, file=sys.stderr)
