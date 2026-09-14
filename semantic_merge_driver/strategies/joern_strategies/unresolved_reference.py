import os
import re
import subprocess
from bisect import bisect_right
from pathlib import Path
from typing import Callable, List, Set, Tuple

from core.interfaces import MergeStrategy, AnalysisResult, Issue
# Machinery reuse across lanes is the detector-cycle idiom (D2 precedent):
# MODULES are imported, never strategy classes — importing a MergeStrategy
# subclass by name into this namespace would make core.plugin_loader discover
# and register it a second time (see test_loader_registers_each_strategy_once).
from strategies.rm2_strategies import signature_stale_call as _ssc
from strategies.text_strategies import import_prune_usage as _ipu

# Conflict category #6 (family) — merge-broken name/type resolution.
#
# Stage-B detector (ISSUES #29 pilot, 2026-06-11): 5 of the 13 attributable
# real-world silent failures were MERGED FILES THAT DO NOT COMPILE — a rename
# or import-deletion applied by one branch collided with references kept from
# the other (declares `method`, still calls `m`; references `baseURL` 5x with
# only `BASE_URL` declared; uses `Struct` after the import was merged away).
#
# Detection is DIFFERENTIAL-ONLY (the parents make it precise):
# Detection: Joern javasrc2cpg builds REF edges for resolved locals/params/
# fields; `cpg.identifier.whereNot(_.refsTo)` yields exactly the identifiers
# with no in-file declaration (probed 2026-06-11: no phantom locals).
# Single-file parsing cannot see inherited fields or same-package/star-import
# names, so those are unresolved in EVERY version — flagging only names
# unresolved in the merged file but in NEITHER parent's unresolved set
# cancels that noise.
#
# Real-world hardening (two stopped v2 pilot attempts, 2026-06-11 — each FP
# shape below is a per-version PARSER artifact, not merge semantics):
#   * `$objN` / `$`-prefixed names are javasrc2cpg lowering temporaries whose
#     numbering shifts between file versions — skipped.
#   * Lambda methods are auto-numbered (`<lambda>20`) per file, so
#     (method, name) differential keys never match across versions — the
#     suppression key is the NAME ONLY (coarser, immune to numbering drift).
#   * A "lost type resolution" lane (param typeFullName degrading to
#     <unresolvedNamespace>/ANY vs a resolved parent — the jnr import-loss
#     shape) was BUILT AND DROPPED: javasrc2cpg's type inference gives up
#     nondeterministically with file context (camsys: flagged "import merged
#     away" on a merged file identical to the dev resolution that compiled),
#     and method-level keys collide across nested classes (Compiler.java:
#     many `parse`/`<init>` methods). Import-deletion breakage is therefore
#     NOT covered by v2 — needs a compile-check oracle, future work.
#
# When parents are not supplied the strategy returns clean BY DESIGN: a
# single-file unresolved scan would flag every inherited field in the
# codebase. This is an explicit no-evidence abstention, not fail-open — any
# Joern failure once analysis has started still fails closed.
#
# SCOPE: intra-file. Cross-file renames, external-API migrations, and type
# mismatches that resolve textually (e.g. a changed return type with a stale
# bare return) are out of scope — see the pilot FINDINGS for the miss list.
#
# ---------------------------------------------------------------------------
# Detector-cycle D3 widening (ISSUES #31 S-D4, outputs/detector-cycle-plan.md
# §2 D3 row) — TEXTUAL removed/renamed-declaration differential.
#
# EXPERIMENTAL: the widened pre-pass below is gated by
# SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1 (plan §2 N2). With the flag unset,
# analyze() behaves byte-identically to the pre-widening lane — the Joern
# differential above stays the lane's default-on behavior (§3 regression
# floor).
#
# The S-D1 gap inventory (reports_detectors/specs/gap_inventory.md) lists the
# shapes this lane misses on real derivation units. S-D4 probes against real
# Joern (2026-07-16, minimal reconstructions of the units) refined the
# mechanism claims:
#   * BARE receiver uses of a one-side-removed/renamed field (datastax
#     `isShutdown.get()`, jline `nonBlockingInput.peek(…)`) DO surface as
#     unresolved identifiers, and a name that is ABSENT from the
#     removing parent is not in that parent's unresolved set — so the
#     existing differential already fires on the minimal shapes. (The
#     inventory's "both-parents guard self-defeats" reading conflated
#     "absent" with "unresolved"; recorded in the S-D4 close-out.)
#   * `this.`-qualified field references (yandex `this.processReady = true`)
#     are lowered to fieldIdentifier nodes — INVISIBLE to cpg.identifier
#     under any differential rule.
#   * Method CALLS (javaparser/jcabi, inventory S2) and TYPE/constructor
#     references (gwtbootstrap3, inventory S3) never surface as identifier
#     nodes at all.
# The widening therefore does not touch the Joern query or its suppression
# rule; it adds a deterministic TEXTUAL differential (the import_prune_usage
# design lesson: exact-text evidence instead of the dropped javasrc2cpg type
# lane) covering all three kinds uniformly:
#
#   candidate: name N of kind K (variable/field, method, type) whose
#              K-declaration exists in BASE, survives in EXACTLY ONE parent
#              (the keeper), is gone from the other (the remover), and is
#              gone from MERGED. Var-kind candidates come from the FIELD
#              tier only (declarators directly inside a named type body):
#              locals, parameters, and lambda parameters are scoped
#              declarations whose removal does not un-declare the name
#              file-wide — treating them as removable fabricates candidates
#              (S-D4 review, verified FP). Suppression tiers stay overbroad.
#   signal:    merged still has a kind-K reference to N
#                var:    bare unqualified or `this.`-qualified, non-call
#                        occurrence (never a `case` label — incl. non-first
#                        multi-labels `case A, N:` — a statement label after
#                        any statement boundary, an annotation-element name,
#                        or import/package text)
#                method: unqualified call `N(…)` (never `new`-prefixed,
#                        `.`/`::`-qualified, or declaration-shaped; the site
#                        classifier is signature_stale_call's, by adapter)
#                type:   `new N(…)` or first-position `extends/implements/
#                        throws N`
#   guards:    * remover-side ABSORPTION — if the remover's own text still
#                references N without declaring it, N resolves some other
#                way (inherited, same-package, static import) or the
#                remover was already broken; either way not merge-induced
#                (this kills the pull-up/move refactor FP class: the
#                refactoring side keeps legal unqualified uses). Being
#                suppression-only, the remover matcher is BROADER than the
#                merged-site matcher: any bare-position mention for types,
#                method references (`::N`) for methods.
#              * keeper-side ATTRIBUTION — the keeper's text must show a
#                kind-K reference (the stale site demonstrably comes from
#                the side where the declaration still existed); evidence-
#                positive, so this matcher stays precise.
#              * merged import coverage (kind-matched, D1 semantics), local
#                shadowing of the matching kind, enum-constant names,
#                Object method names + inherited-member absorbable spans +
#                static-import absorption (method kind, signature_stale_call
#                semantics), java.lang types (type kind), and — var kind —
#                surviving TYPE imports / java.lang type names: a receiver-
#                position `N.method()` legally re-binds to a same-named type
#                once the obscuring variable is gone (JLS 6.5.2).
#
# DELIBERATE ASYMMETRY (unit-evidence-driven, S-D4 close-out records it):
# method-kind sites inside extends/implements/enum/anonymous bodies are
# suppressed (JLS 15.12.1 resolves unqualified calls through inherited
# members — D2's probed guard), but var- and type-kind sites are NOT span-
# suppressed: the yandex unit's class extends AbstractPGProcess and the
# gwtbootstrap3 unit's extends FormElementContainer — span suppression would
# zero both, and the differential evidence (declared here in base + keeper,
# deliberately removed by the remover, remover keeps no uses) outweighs the
# inherited-shadow residual. Registered residual FP classes (GD3 watch):
# a removed field/type whose surviving use re-binds to an identical
# inherited field / inherited nested type / same-package type when the
# remover also dropped every use it had.
#
# Deliberately NOT covered (FN direction, close-out records why): same-side
# removal by BOTH parents; mergiraf-dropped declarations kept by both
# parents (no side attribution); bare type positions in MERGED-site matching
# (locals/params/casts/generics/annotations — only new/extends/implements/
# throws anchor precisely; the remover-side broad matcher does see them);
# `this.`-qualified method calls; multi-item throws/implements tails;
# type-parameter shadowing; anonymous-class fields (the field tier covers
# named type bodies only); partial overload removals (name-level method
# granularity); casts before a ternary colon (read as a label position).

_QUERY = r"""
import io.shiftleft.semanticcpg.language._
{
  cpg.identifier.whereNot(_.refsTo).filterNot(_.name.startsWith("$")).foreach { i =>
    val m = i.method.name
    val ln = i.lineNumber.map(_.toString.toInt).getOrElse(-1)
    println(s"UNRES_ID:$m||${i.name}||$ln")
  }
}
"""


class _JoernError(Exception):
    """Raised when a Joern parse/query is inconclusive (drives fail-closed)."""


class JoernUnresolvedReferenceStrategy(MergeStrategy):
    @property
    def name(self) -> str:
        return "JoernUnresolvedReference"

    def analyze(self, file_path: str, base_content: str = None,
                ours_content: str = None, theirs_content: str = None) -> AnalysisResult:
        # Differential-only: without both parents there is no way to separate
        # merge-broken resolution from ordinary single-file unresolvables
        # (inherited fields, same-package types). Abstain cleanly.
        if ours_content is None or theirs_content is None:
            return AnalysisResult(is_clean=True, issues=[])

        # D3 widening: textual removed/renamed-declaration differential (see
        # module header). Flag-gated; needs base for the three-version decl
        # sets (without it the widened pass abstains, the Joern flow below is
        # untouched either way).
        widened: List[Issue] = []
        widened_names: Set[str] = set()
        if (os.environ.get(_ENV_FLAG) == "1" and base_content is not None
                and file_path.lower().endswith(".java")):
            try:
                merged_text = Path(file_path).read_text(encoding="utf-8", errors="replace")
            except OSError as e:
                return self._fail_closed(f"widened pre-pass could not read merged file: {e}")
            widened, widened_names = _widened_issues(
                self.name, merged_text, base_content, ours_content, theirs_content)

        try:
            merged_ids = self._run_query(file_path)
        except _JoernError as e:
            return self._fail_closed(f"merged analysis inconclusive: {e}", widened)

        # NAME-ONLY differential keys: method names are version-unstable
        # (auto-numbered lambdas, renamed methods), so suppression is by
        # identifier name across the whole parent file — coarser but immune
        # to parser numbering drift.
        parent_unresolved = set()
        for label, content in (("ours", ours_content), ("theirs", theirs_content)):
            tmp = f"{file_path}.{label}.java"
            try:
                with open(tmp, "w") as f:
                    f.write(content)
                parent_unresolved |= {n for (_, n, _) in self._run_query(tmp)}
            except _JoernError as e:
                return self._fail_closed(f"{label} analysis inconclusive: {e}", widened)
            finally:
                if os.path.exists(tmp):
                    os.remove(tmp)

        issues = list(widened)
        seen = set(widened_names)  # one flag per name: widened sites win ties
        for (m, n, ln) in merged_ids:
            if n in parent_unresolved or n in seen:
                continue
            seen.add(n)
            issues.append(Issue(
                line_number=ln,
                severity="CRITICAL",
                message=(
                    f"Unresolved identifier '{n}' in method '{m}': referenced in "
                    f"the merged file but resolvable in neither parent — likely a "
                    f"rename/declaration applied by one branch colliding with a "
                    f"reference kept from the other."
                ),
                strategy_name=self.name,
            ))
        return AnalysisResult(is_clean=(len(issues) == 0), issues=issues)

    def _run_query(self, file_path: str):
        """Parse one file and collect unresolved identifiers.

        Returns [(method, name, line)]. Raises _JoernError on any parse/query
        failure so the caller can fail closed.
        """
        cpg_out = f"{file_path}.cpg.bin"
        query_file = f"{file_path}.query.sc"
        try:
            try:
                subprocess.run(["joern-parse", file_path, "--output", cpg_out],
                               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                raise _JoernError(f"joern-parse failed: {e}")

            with open(query_file, "w") as f:
                f.write(_QUERY)

            process = subprocess.run(
                f"cat {query_file} | joern --cpg {cpg_out} --nocolors",
                shell=True, capture_output=True, text=True,
            )
            if process.returncode != 0:
                raise _JoernError(
                    f"joern query rc={process.returncode}: {process.stderr.strip() or '(empty)'}"
                )

            ids = []
            for line in process.stdout.splitlines():
                if "UNRES_ID:" in line:
                    parts = line.split("UNRES_ID:", 1)[1].strip().split("||")
                    if len(parts) == 3:
                        ids.append((parts[0], parts[1], _to_int(parts[2])))
            return ids
        finally:
            if os.path.exists(cpg_out):
                os.remove(cpg_out)
            if os.path.exists(query_file):
                os.remove(query_file)

    def _fail_closed(self, msg: str, widened: List[Issue] = ()) -> AnalysisResult:
        # Widened textual findings ride along after the inconclusive Issue:
        # they are evidence in their own right (genuine issues win in the
        # Stage-C verdict classifier), and dropping them because Joern broke
        # would silently discard a real flag. Empty when the flag is off, so
        # the pre-widening result shape is unchanged.
        return AnalysisResult(
            is_clean=False,
            issues=[Issue(line_number=0, severity="CRITICAL",
                          message=f"Joern analysis inconclusive: {msg}",
                          strategy_name=self.name)] + list(widened),
        )


def _to_int(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        return -1


# --------------------------------------------------------------------------- #
# D3 widening — textual removed/renamed-declaration differential (flag-gated;
# see the module header for shape, guards, and the probe record).
# All scanning runs on comment/string-stripped text via _ipu._FileView.
# --------------------------------------------------------------------------- #

_ENV_FLAG = "SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS"

_KIND_VAR = "variable/field"
_KIND_METHOD = "method"
_KIND_TYPE = "type"

_TYPE_DECL_RE = re.compile(
    r"(?:\b(?:class|interface|enum|record)|@\s*interface)\s+([A-Za-z_$][\w$]*)")
_CALLABLE_HEAD_RE = re.compile(r"(?<![\w$])([A-Za-z_$][\w$]*)\s*\(")
# Lambda parameters declare a name with no type prefix: `x ->`, `(x) ->`,
# `(x, y) ->` (the rename lane's post-fix-round-2 alternation, as an
# enumerator — lookahead so `(a, b) ->` yields BOTH names, not just the
# first). Switch-rule case labels (`case MODE ->`, `case A, B ->`) also
# match the textual shape but are REFERENCES, not declarations — recording
# them as declarations would let a deleted switch fabricate a
# removed-declaration candidate (S-D4 review, verified FP) — so matches
# whose comma-chain head sits after `case` are rejected in _scan_var_decls.
_ARROW_DECL_RE = re.compile(
    r"(?<![\w$])([A-Za-z_$][\w$]*)(?=\s*(?:(?:,[\w\s,]*)?\)\s*)?->)")
# Type-usage anchors: keyword-anchored positions are the only bare type
# positions precise enough for the zero-FP bar (module header, S3 rationale).
_TYPE_USE_KEYWORDS = frozenset(("new", "extends", "implements", "throws"))
# Words after which a bare identifier is NOT a variable reference: label
# references (`break retry;`), and type positions where only a same-named
# TYPE could legally stand (`new`/`instanceof`/clause operands).
_NON_VAR_PREV_WORDS = frozenset(
    ("break", "continue", "new", "instanceof", "extends", "implements", "throws"))


def _annotation_arg_spans(stripped: str) -> List[Tuple[int, int]]:
    """Spans of annotation argument lists `@Name( … )`.

    Variable-kind occurrences inside them are excluded: `timeout` in
    `@Test(timeout = 500)` is an annotation ELEMENT name resolved against
    the annotation type, not a reference to a field named timeout.
    (`@interface` declarations never match — the regex requires `(` directly
    after the annotation name.)"""
    spans = []
    for m in re.finditer(r"@\s*[A-Za-z_$][\w$.]*\s*\(", stripped):
        spans.append((m.end() - 1, _ipu._skip_group(stripped, m.end() - 1, "(", ")")))
    return spans


def _declared_type_names(stripped: str) -> Set[str]:
    """Names declared as class/interface/enum/record/@interface anywhere in
    the file (nested and inner types included). Type PARAMETERS (`<T>`) are
    not declarations here — documented shadowing FN."""
    return {m.group(1) for m in _TYPE_DECL_RE.finditer(stripped)}


def _declared_method_names(stripped: str) -> Set[str]:
    """Names with a METHOD-form declaration: `name(…)` whose tail continues
    as a declaration and whose preceding token can end a return type
    (signature_stale_call's probed classification). Constructor-form
    declarations are deliberately not collected — constructor names are type
    names and belong to the type kind."""
    out: Set[str] = set()
    for m in _CALLABLE_HEAD_RE.finditer(stripped):
        name = m.group(1)
        if name in out or name in _ipu._KEYWORDS:
            continue
        after_paren = m.end()
        params, close = _ssc._match_group(stripped[after_paren:], type_context=True)
        if params is None:
            continue
        if not _ssc._is_decl_tail(*_ssc._after_params(stripped, after_paren, close)):
            continue
        if _ssc._type_ish_before(stripped, m.start(1)):
            out.add(name)
    return out


def _type_body_spans(stripped: str) -> List[Tuple[int, int]]:
    """(open-brace offset, body end) for every NAMED type declaration —
    _ssc._absorbable_spans' header walk, minus the supertype filter. Used to
    tell FIELD declarators (directly inside a type body) from scoped
    locals/parameters (inside a deeper brace level)."""
    n = len(stripped)
    spans: List[Tuple[int, int]] = []
    try:
        for m in _ssc._TYPE_HEADER_RE.finditer(stripped):
            i = m.end()
            while i < n:
                c = stripped[i]
                if c == "<":
                    i = _ssc._skip_angles(stripped, i)
                    continue
                if c == "(":
                    i = _ipu._skip_group(stripped, i, "(", ")")
                    continue
                if c == "{" or c == ";":
                    break
                i += 1
            if i >= n or stripped[i] != "{":
                continue
            spans.append((i, _ipu._skip_group(stripped, i, "{", "}")))
    except Exception:  # noqa: BLE001 — parser anomaly: no field tier at all
        return []      # (candidates vanish — suppression is the safe direction)
    return spans


def _brace_positions(stripped: str) -> Tuple[List[int], List[int]]:
    opens = [i for i, c in enumerate(stripped) if c == "{"]
    closes = [i for i, c in enumerate(stripped) if c == "}"]
    return opens, closes


def _depth_at(braces: Tuple[List[int], List[int]], off: int) -> int:
    opens, closes = braces
    return bisect_right(opens, off - 1) - bisect_right(closes, off - 1)


def _scan_var_decls(view: "_ipu._FileView") -> Tuple[Set[str], Set[str], Set[int]]:
    """(field_names, all_names, offsets) of VARIABLE-form declarators.

    field_names — declarators sitting DIRECTLY inside a named type body
    (depth == body depth + 1): the only tier that can seed a candidate. A
    lambda parameter or method local is a SCOPED declaration — deleting its
    enclosing expression does not un-declare the name file-wide, so treating
    it as removable fabricates candidates (S-D4 review, verified FP).
    all_names — every declarator incl. locals/params/lambdas: the merged-side
    suppression tier (overbroad, FN direction).
    offsets — every declarator offset: a declaration is not a reference, so
    the usage scanner excludes these (a keeper's own `int f = 1;` must not
    satisfy attribution).

    Kind-strict on purpose: a method declaration `boolean isShutdown()` must
    NOT count — the datastax unit's stale FIELD reference coexists with a
    same-named method in the merged file. `==`/`::` follow-ups are excluded
    (comparisons and method references, not declarators). After a recognized
    typed declarator, the comma chain is walked at bracket depth 0 so second
    declarators (`int a, b;`) register too — leaving them invisible let the
    usage scanner read them as stale sites (S-D4 review, verified FP).
    C-style array declarators (`int b[];`) are recognized via the `[`
    follower (a `[` after a non-declarator identifier never has a type-ish
    token before it: `return arr[i]` / `x = arr[i]` fail _type_ish_before)."""
    s = view.stripped
    n = len(s)
    field_names: Set[str] = set()
    all_names: Set[str] = set()
    offsets: Set[int] = set()
    spans = _type_body_spans(s)
    braces = _brace_positions(s)

    def field_tier(off: int) -> bool:
        inner = None
        for brace, end in spans:
            if brace < off < end and (inner is None or brace > inner[0]):
                inner = (brace, end)
        if inner is None:
            return False
        return _depth_at(braces, off) == _depth_at(braces, inner[0]) + 1

    def record(name: str, off: int) -> None:
        all_names.add(name)
        offsets.add(off)
        if field_tier(off):
            field_names.add(name)

    def chain_walk(pos: int) -> None:
        """From just after a recognized declarator's name: register the
        remaining `, name [= init]` declarators of the same statement.
        Depth-0 commas only (initializer internals nest); a comma item that
        is not a bare `ident <=,;[>` shape (e.g. a parameter's `Type name`)
        ends the walk."""
        depth = 0
        i = pos
        while i < n:
            c = s[i]
            if c in "([<{":
                depth += 1
            elif c in ")]>}":
                if depth == 0:
                    return  # left the statement (param list / for header)
                depth -= 1
            elif c == ";" and depth == 0:
                return
            elif c == "," and depth == 0:
                j = i + 1
                while j < n and s[j] in " \t\r\n":
                    j += 1
                m2 = _ipu._IDENT_RE.match(s, j)
                if not m2 or m2.group(0) in _ipu._KEYWORDS:
                    return
                k = m2.end()
                while k < n and s[k] in " \t\r\n":
                    k += 1
                follower = s[k] if k < n else ""
                if follower not in "=,;[" or (
                        follower == "=" and k + 1 < n and s[k + 1] == "="):
                    return  # not a bare declarator item — stop the chain
                record(m2.group(0), m2.start())
                i = m2.end()
                continue
            i += 1

    for m in _ipu._IDENT_RE.finditer(s):
        name = m.group(0)
        if name in _ipu._KEYWORDS:
            continue
        if view._in_excluded(m.start()) or view._qualified_or_case(m.start()):
            continue
        j = m.end()
        while j < n and s[j] in " \t\r\n":
            j += 1
        nxt = s[j] if j < n else ""
        if not nxt or nxt not in "=;,):[":
            continue
        if nxt == "=" and j + 1 < n and s[j + 1] == "=":
            continue
        if nxt == ":" and j + 1 < n and s[j + 1] == ":":
            continue
        if _ssc._type_ish_before(s, m.start()):
            record(name, m.start())
            chain_walk(m.end())

    for m in _ARROW_DECL_RE.finditer(s):
        name = m.group(1)
        if name in _ipu._KEYWORDS:
            continue
        # `case MODE ->` / `case A, B ->` are references, not declarations:
        # _qualified_or_case walks the comma chain back to the `case` head.
        if view._qualified_or_case(m.start(1)):
            continue
        # lambda params are scoped — suppression tier only, never candidates
        all_names.add(name)
        offsets.add(m.start(1))
    return field_names, all_names, offsets


def _var_usage_sites(view: "_ipu._FileView", name: str,
                     ann_spans: List[Tuple[int, int]],
                     decl_offsets: Set[int]) -> List[Tuple[int, int]]:
    """(line, offset) of variable-form references to `name`: bare unqualified
    or `this.`-qualified, never call-form. Excluded positions: import/package
    statements, `case` labels, non-`this` qualifiers, method-reference
    receivers keep counting (a field used as `name::method` is a real read),
    annotation argument lists, statement labels (`name: while (…)`), and the
    file's own declarator offsets (a declaration is not a reference)."""
    s = view.stripped
    n = len(s)
    out: List[Tuple[int, int]] = []
    for m in re.finditer(rf"(?<![\w$]){re.escape(name)}(?![\w$])", s):
        start = m.start()
        if start in decl_offsets:
            continue
        if view._in_excluded(start) or _ssc._within(ann_spans, start):
            continue
        kind, tok, tok_idx = _ssc._prev_token(s, start)
        if kind == "word" and tok in _NON_VAR_PREV_WORDS:
            continue  # label reference or type position, not a variable read
        if kind == "char" and tok == "@":
            continue  # annotation type usage
        this_qualified = False
        if view._qualified_or_case(start):
            # `this.name` stays in scope: it references a field of the
            # enclosing class — exactly the yandex stale-write shape. Any
            # other qualifier means a receiver this file cannot type.
            if kind == "char" and tok == ".":
                kind2, tok2, _idx2 = _ssc._prev_token(s, tok_idx)
                if kind2 == "word" and tok2 == "this":
                    this_qualified = True
            if not this_qualified:
                continue
        j = m.end()
        while j < n and s[j] in " \t\r\n":
            j += 1
        nxt = s[j] if j < n else ""
        if nxt == "(":
            continue  # call-form: a same-named METHOD, not this variable
        if (nxt == ":" and not (j + 1 < n and s[j + 1] == ":")
                and not this_qualified
                and (kind == "start"
                     or (kind == "char" and tok in "{};)")
                     or (kind == "word" and tok in ("else", "do", "try", "finally")))):
            # statement-label position (`retry: while…` after any statement
            # boundary incl. `)` / `else` — S-D4 review fix); a ternary's
            # middle operand or an assert message keeps its `?`/`assert`
            # predecessor and stays a genuine read
            continue
        out.append((s.count("\n", 0, start) + 1, start))
    return out


def _method_call_sites(view: "_ipu._FileView", name: str) -> List[Tuple[int, int]]:
    """(line, offset) of unqualified call-form references `name(…)`.

    Adapter over signature_stale_call's probed site classifier (S-D4 review:
    a private near-copy would drift from the one battle-tested definition):
    `.`/`::`-qualified and `case`-label positions never count, `new`-prefixed
    occurrences are constructors of a same-named class (type kind),
    declaration-shaped sites are excluded. The arity channel is unused here —
    view.stripped stands in for the arity text and the (possibly None)
    counts are ignored: this lane's method matching is name-level."""
    return [(cs.line, cs.start)
            for cs in _ssc._call_sites(view, name, False, view.stripped)]


def _method_mentions(view: "_ipu._FileView", name: str) -> bool:
    """Suppression-only broad matcher for the REMOVER side (method kind):
    an unqualified call OR a method-reference use (`Type::name`, `this::name`)
    in the remover's own text proves the name still resolves there without
    the deleted declaration (inherited/static-imported) — FN-safe to widen."""
    if _method_call_sites(view, name):
        return True
    s = view.stripped
    for m in re.finditer(rf"::\s*{re.escape(name)}(?![\w$])", s):
        if not view._in_excluded(m.start()):
            return True
    return False


def _type_usage_sites(view: "_ipu._FileView", name: str) -> List[Tuple[int, int]]:
    """(line, offset) of keyword-anchored type references: `new name(…)`
    (constructor/anonymous-class creation) and first-position
    `extends/implements/throws name`. Bare type positions (locals, params,
    casts, generics, annotations) are deliberately not matched for MERGED
    sites — identifier pairs are too common for the zero-FP bar (module
    header); the remover-side absorption check uses _type_mentions instead."""
    s = view.stripped
    out: List[Tuple[int, int]] = []
    for m in re.finditer(rf"(?<![\w$]){re.escape(name)}(?![\w$])", s):
        start = m.start()
        if view._in_excluded(start) or view._qualified_or_case(start):
            continue
        kind, tok, _idx = _ssc._prev_token(s, start)
        if kind == "word" and tok in _TYPE_USE_KEYWORDS:
            out.append((s.count("\n", 0, start) + 1, start))
    return out


def _type_mentions(view: "_ipu._FileView", name: str) -> bool:
    """Suppression-only broad matcher for the REMOVER side (type kind): ANY
    unqualified non-call occurrence (a bare type position — `Ev cached;`,
    a cast, a generic argument, `Ev.class`) counts. A remover that deleted
    the declaration but kept such a use proves the name resolves without it
    (same-package/inherited nested type) — the anchor-limited merged-site
    matcher must not blind the absorption guard (S-D4 review, verified FP).
    Call-form occurrences stay excluded: a same-named METHOD on the remover
    side says nothing about the TYPE."""
    s = view.stripped
    n = len(s)
    for m in re.finditer(rf"(?<![\w$]){re.escape(name)}(?![\w$])", s):
        start = m.start()
        if view._in_excluded(start) or view._qualified_or_case(start):
            continue
        j = m.end()
        while j < n and s[j] in " \t\r\n":
            j += 1
        if j < n and s[j] == "(":
            continue
        return True
    return False


def _widened_issues(strategy_name: str, merged_text: str, base_content: str,
                    ours_content: str, theirs_content: str
                    ) -> Tuple[List[Issue], Set[str]]:
    """The D3 textual differential. Returns (issues, flagged names) — the
    names seed the Joern loop's dedupe so one stale name yields one flag set.

    Pure text, no subprocess: deterministic on every input (the Stage-B
    lesson that retired the javasrc2cpg type lane)."""
    merged = _ipu._FileView(merged_text)
    if _ipu._CONFLICT_MARKER_RE.search(merged.stripped):
        return [], set()  # textual conflict already surfaced — not silent
    if merged_text == ours_content or merged_text == theirs_content:
        return [], set()  # wholesale one side: nothing merge-induced here

    views = {"base": _ipu._FileView(base_content),
             "ours": _ipu._FileView(ours_content),
             "theirs": _ipu._FileView(theirs_content)}
    type_names = {k: _declared_type_names(v.stripped) for k, v in views.items()}
    method_names = {k: _declared_method_names(v.stripped) for k, v in views.items()}
    var_scans = {k: _scan_var_decls(v) for k, v in views.items()}
    var_fields = {k: scan[0] for k, scan in var_scans.items()}
    var_decl_offsets = {k: scan[2] for k, scan in var_scans.items()}

    merged_types = _declared_type_names(merged.stripped)
    _merged_fields, merged_vars, merged_var_offsets = _scan_var_decls(merged)
    ann_spans = {label: _annotation_arg_spans(v.stripped)
                 for label, v in views.items()}
    merged_ann_spans = _annotation_arg_spans(merged.stripped)
    absorb_spans = _ssc._absorbable_spans(merged.stripped)

    issues: List[Issue] = []
    flagged: Set[str] = set()

    def emit(kind: str, name: str, keeper: str, remover: str,
             sites: List[Tuple[int, int]]) -> None:
        flagged.add(name)
        for line, _off in sites:
            issues.append(Issue(
                line_number=line,
                severity="CRITICAL",
                message=(
                    f"Stale reference to a removed/renamed declaration: {kind} "
                    f"'{name}' is referenced at this line, but its declaration — "
                    f"present in base and kept by {keeper} — was removed on "
                    f"{remover}, and the merged file no longer declares '{name}' "
                    f"nor retains an import covering it."
                ),
                strategy_name=strategy_name,
            ))

    def split_sides(in_ours: bool, in_theirs: bool):
        """(keeper, remover) when exactly one side kept the declaration."""
        if in_ours == in_theirs:
            return None
        return ("ours", "theirs") if in_ours else ("theirs", "ours")

    def finish(kind: str, name: str, keeper: str, remover: str,
               merged_sites: List[Tuple[int, int]],
               parent_usage: Callable[[str], bool],
               remover_mentions: Callable[[str], bool]) -> None:
        """The FP-critical shared tail, structural for every kind:
        merged sites exist → remover-side ABSORPTION (a remover that still
        references the name resolves it without the declaration, or was
        already broken — not merge-induced; suppression-only, so the matcher
        may be broader than the merged-site one) → keeper-side ATTRIBUTION
        (the stale site must be traceable to the side that still declared
        the name; evidence-positive, so the matcher stays precise)."""
        if not merged_sites:
            return
        if remover_mentions(remover):
            return
        if not parent_usage(keeper):
            return
        emit(kind, name, keeper, remover, merged_sites)

    # ---- variable/field kind --------------------------------------------- #
    # Candidates come from the FIELD tier only: locals/params/lambda params
    # are scoped declarations whose removal does not un-declare the name
    # file-wide (S-D4 review, verified FP). Suppression uses the ALL tier.
    for name in sorted(var_fields["base"]):
        sides = split_sides(name in var_fields["ours"], name in var_fields["theirs"])
        if sides is None or name in merged_vars:
            continue
        keeper, remover = sides
        if name in merged.enum_constants or name in merged_types:
            continue  # an enum constant / type of that name survives
        if merged.covers(name, "member"):
            continue  # a static import can still provide the bare name
        if name in _ipu._JAVA_LANG or merged.covers(name, "type"):
            # receiver-position occurrences (`Name.method()`) legally re-bind
            # to a same-named TYPE once the obscuring variable is gone
            # (JLS 6.5.2) — a surviving type import / java.lang name means
            # the merged file may still compile (S-D4 review, verified FP)
            continue
        var_usage = lambda label: bool(_var_usage_sites(  # noqa: E731
            views[label], name, ann_spans[label], var_decl_offsets[label]))
        finish(_KIND_VAR, name, keeper, remover,
               _var_usage_sites(merged, name, merged_ann_spans, merged_var_offsets),
               parent_usage=var_usage, remover_mentions=var_usage)

    # ---- method kind ------------------------------------------------------ #
    for name in sorted(method_names["base"]):
        sides = split_sides(name in method_names["ours"], name in method_names["theirs"])
        if sides is None:
            continue
        keeper, remover = sides
        if name in _ssc._OBJECT_METHODS:
            continue  # every class inherits these — never flaggable
        if name in type_names["base"] or name in merged_types:
            continue  # constructor-name ambiguity: type kind's territory
        if _ssc._declared_arities(merged.stripped, name):
            continue  # any surviving declaration (or overload) absorbs
        if name in merged.enum_constants:
            continue
        if _ssc._import_absorbs(merged, name, is_ctor=False):
            continue  # a static import can provide the unqualified call
        finish(_KIND_METHOD, name, keeper, remover,
               [site for site in _method_call_sites(merged, name)
                if not _ssc._within(absorb_spans, site[1])],
               parent_usage=lambda label: bool(_method_call_sites(views[label], name)),
               remover_mentions=lambda label: _method_mentions(views[label], name))

    # ---- type kind --------------------------------------------------------- #
    for name in sorted(type_names["base"]):
        sides = split_sides(name in type_names["ours"], name in type_names["theirs"])
        if sides is None or name in merged_types:
            continue
        keeper, remover = sides
        if name in _ipu._JAVA_LANG:
            continue  # java.lang provides the type with no import at all
        if merged.covers(name, "type"):
            continue  # an import (explicit or wildcard) can still provide it
        finish(_KIND_TYPE, name, keeper, remover,
               _type_usage_sites(merged, name),
               parent_usage=lambda label: bool(_type_usage_sites(views[label], name)),
               remover_mentions=lambda label: _type_mentions(views[label], name))

    return issues, flagged
