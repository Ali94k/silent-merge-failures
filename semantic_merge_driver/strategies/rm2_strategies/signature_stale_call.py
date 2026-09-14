r"""SignatureStaleCall — changed-signature + stale-caller detector (detector-cycle D2).

Detector-cycle D2 (ISSUES #31, outputs/detector-cycle-plan.md §2) — category
`stale-caller-of-changed-signature` (10.2% of the #30 census).

EXPERIMENTAL: gated by SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1 (plan §2 N2).
With the flag unset, analyze() returns clean before doing any work, so the
lane cannot affect driver verdicts until the cycle validates it.

Shape (differential 3-way, merge-induced only): side X changes a method's
signature IN THIS FILE — evidenced by per-branch RM2 on (base, X) — such
that the ARITY changes (parameter added/removed); side Y adds — or keeps
from base — a call to the method with the OLD argument count. The
structural merge combines X's new declaration with Y's old-shape call: the
merged file calls a method with an argument count no surviving declaration
accepts.

Arity is the PRIMARY AND ONLY signal (plan §2 D2 row). Same-arity signature
changes (parameter/return-type changes, throws-clause changes — 4 of the 8
usable D2 derivation specs) are DOCUMENTED FNs by design: flagging them
would require typing arguments file-locally, which is the Stage-B
type-inference lane this project already built, measured, and dropped
(see unresolved_reference.py). The conservative bias (prefer FN over FP)
is the plan's, not an implementation shortcut.

Evidence chain — ALL must hold for a flag:
  1. RM2 (base, X) reports `Add Parameter` / `Remove Parameter` whose old
     and new METHOD_DECLARATION codeElements parse to the SAME name with
     DIFFERENT arities, exactly one distinct (old, new) arity pair for the
     name on side X, and no arity change for the name on side Y (concurrent
     signature edits are not the clean D2 shape).
  2. Neither signature is varargs, and no version of the file (base, ours,
     theirs, merged) textually declares or calls a varargs `name(… ...)`
     form — varargs make every arity ≥ the fixed prefix legal
     (JLS 15.12.2.4).
  3. The merged file declares the name at the NEW arity (the change landed)
     and does NOT declare it at the OLD arity (no surviving old declaration
     and no overload with matching arity — the plan's overload guard; Java
     has no default arguments, so only a same-arity declaration or varargs
     can absorb the call).
  4. The merged file has ≥1 UNQUALIFIED call of the name with argument
     count == old arity. Qualified calls (`expr.m(…)`, `this.m(…)`,
     `super.m(…)`, `X::m`) never count — the receiver's type is exactly
     what a file-local view cannot resolve (the plan's builder/chained +
     cross-file-target guards). For constructor signatures the call form
     is `new Name(…)` (constructor binding is exact — never inherited);
     for method signatures a `new`-prefixed occurrence never counts.
  5. The call site is not ABSORBABLE: an unqualified method name is
     resolved against the innermost enclosing type of which it is a MEMBER
     — and members include inherited methods (JLS 6.5.7.1 → 15.12.1) — so
     occurrences inside any type body whose header declares a supertype
     (`extends`/`implements`), inside any enum body (implicit
     `extends java.lang.Enum`), or inside any anonymous-class body are
     suppressed. Names java.lang.Object provides are suppressed everywhere
     (every class inherits them). A static import of the name (explicit or
     wildcard) suppresses the name; for constructors, a single-type import
     of the name suppresses it (it could shadow a nested class).
     Constructors themselves are exempt from inheritance absorption:
     constructor declarations are not members and are never inherited
     (JLS 8.8), so `new Name(…)` binds only declarations visible in the
     file when Name is declared here.
  6. Attribution: side X's own text has NO unqualified old-arity call of
     the name (X updated its call sites; a leftover would mean X was
     already broken — either way not merge-induced), and side Y's text HAS
     one (the stale call demonstrably came from Y, where the old
     declaration still existed and the call was legal).

Detection is per-file by construction: the driver is a git merge driver and
never sees sibling files. Cross-file shapes — the changed declaration in
another file of the same merge (enderstone), or callers-only drift against
an interface/library declaration (buddycloud, sonar-findbugs, and the five
Amendment-2 out-of-target units) — are out of reach and documented as such;
the S-D6 FINDINGS reports this ceiling.

RM2-matching dependence (probed against merge-tools/refactoring-miner:2.4.0,
2026-07-16 — see tests): RM2 pairs old/new declarations by statement-level
similarity. A replace-style edit (jcabi: `repo()` → `repos()` + new
`repo(Repos)`) resolves as Rename Method + Change Return Type, not Add
Parameter — those stale calls belong to RM2RenameConflict's lane, not this
one. Constructor changes ARE reported when bodies match cleanly (probes
B2/B3); constructor codeElements carry no ` : returnType` suffix. `Split
Parameter` / `Merge Parameter` also change arity but are deliberately NOT
accepted: their location composition is unprobed, and unprobed shapes stay
out (zero-FP bar). Multi-parameter additions emit one record per parameter,
each carrying the same full old/new declarations — deduped here by (old,
new) arity pair.

Abstentions (return clean, by design): non-.java files; missing base/ours/
theirs (no differential evidence — the experimental-lane convention from
import_prune_usage.py); conflict markers in the merged text (a textual
conflict is already surfaced; nothing here is silent); merged byte-identical
to a parent (whatever it contains pre-existed in that parent).

Known FNs beyond the design scope (accepted, FN-direction): method
references (`T::m` — arity invisible without resolving the functional
interface; Error Prone's method matchers share the gap, issue #1283);
`this.`-qualified and `Type.`-qualified calls (the qualified exclusion is
also CORRECT for `this.` — such calls reach inherited members too); enum-
constant constructor arguments (`CONST(…)` — no `new`); qualified inner-
class creation (`outer.new Inner(…)` reached only when unqualified,
`Outer.Inner` news are `.`-excluded); `\uXXXX` pre-lexing and exotic
Unicode identifiers (inherited D1 stripper limitation). Record
deconstruction patterns (`case Point(int x, int y)`) at top level are
`case`-excluded; nested patterns may be scanned as method-form sites — an
old-arity pattern against a changed record header is itself a compile
error, so the direction is still sound.

Fail-closed (CRITICAL "inconclusive" Issue) on RM2 infrastructure failure
(missing Docker/image, subprocess error, non-zero exit, malformed JSON,
timeout) and on an unreadable merged file — the β-stage pattern from
rename_conflict.py.

Machinery reuse (S-D3 "reuse, don't fork"): the RM2 Docker runner is
rename_conflict's `_run_rm2_pair` via a composed RM2RenameConflictStrategy
instance; comment/string stripping, import parsing, occurrence exclusion,
and enum-constant parsing come from import_prune_usage's `_FileView`.
Both are imported AS MODULES: importing a MergeStrategy subclass by name
into this namespace would make core.plugin_loader discover and register it
a second time (it walks module attributes; see the loader-duplication test).
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from core.interfaces import AnalysisResult, Issue, MergeStrategy
from strategies.rm2_strategies import rename_conflict as _rc
from strategies.text_strategies import import_prune_usage as _ipu

_ENV_FLAG = "SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS"

# The two probed arity-changing refactoring types (see module docstring).
ARITY_CHANGE_TYPES = frozenset({"Add Parameter", "Remove Parameter"})

_IDENT_ONLY_RE = re.compile(r"[A-Za-z_$][\w$]*\Z")
_WORD_RE = re.compile(r"[\w$]")

# Modifiers that may precede a declaration's name (constructors) or its
# return type (methods). `default` covers interface default methods.
_DECL_MODIFIERS = frozenset(
    "public private protected static final abstract synchronized native strictfp default".split()
)
# Primitive/void return types — Java keywords that ARE valid decl prefixes.
_PRIMITIVES = frozenset("int long short byte char boolean float double void".split())

# Methods every class inherits from java.lang.Object: an unqualified call of
# these names can always bind cross-file, so they are never flaggable.
_OBJECT_METHODS = frozenset(
    "equals hashCode toString clone finalize getClass notify notifyAll wait".split()
)


@dataclass(frozen=True)
class _SigChange:
    name: str
    old_arity: int
    new_arity: int
    is_ctor: bool
    varargs: bool          # '...' in either codeElement param list
    old_decl: str
    new_decl: str


@dataclass(frozen=True)
class _CallSite:
    line: int              # 1-based, in the merged file
    start: int             # offset of the name in stripped text
    arity: Optional[int]   # None = uncountable (site is dropped)


class SignatureStaleCallStrategy(MergeStrategy):
    """Detect merged files calling a changed-arity method with its old argument count."""

    @property
    def name(self) -> str:
        return "SignatureStaleCall"

    def __init__(self, image: str = _rc.RM2_IMAGE,
                 timeout_seconds: int = _rc.RM2_TIMEOUT_SECONDS):
        # Composition, not fork: the rename lane's Docker runner is the one
        # RM2 invocation stack in this repo (S-D2 guardrail: existing lanes
        # unmodified, so the runner is borrowed through an instance).
        self._rm2 = _rc.RM2RenameConflictStrategy(image=image, timeout_seconds=timeout_seconds)

    def analyze(self, file_path: str, base_content: str = None,
                ours_content: str = None, theirs_content: str = None) -> AnalysisResult:
        if os.environ.get(_ENV_FLAG) != "1":
            return _clean()
        if not file_path.lower().endswith(".java"):
            return _clean()
        if base_content is None or ours_content is None or theirs_content is None:
            return _clean()  # differential-only; abstention convention

        try:
            merged_text = Path(file_path).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            return self._inconclusive(f"could not read merged file {file_path}: {e}")

        if merged_text == ours_content or merged_text == theirs_content:
            return _clean()  # wholesale one side: nothing merge-induced here

        merged = _ipu._FileView(merged_text)
        if _ipu._CONFLICT_MARKER_RE.search(merged.stripped):
            return _clean()  # textual conflict already surfaced — not silent

        basename = Path(file_path).name
        sig_lists: Dict[str, Dict[str, List[_SigChange]]] = {"ours": {}, "theirs": {}}
        for label, content in (("ours", ours_content), ("theirs", theirs_content)):
            if content == base_content:
                continue
            refactorings = self._rm2._run_rm2_pair(base_content, content, basename)
            if refactorings is None:
                return self._inconclusive(
                    f"RM2 invocation failed on (base, {label}); see stderr for details")
            for change in _extract_arity_changes(refactorings):
                sig_lists[label].setdefault(change.name, []).append(change)

        if not (sig_lists["ours"] or sig_lists["theirs"]):
            return AnalysisResult(is_clean=True, issues=[])

        issues: List[Issue] = []
        views: Dict[str, _ipu._FileView] = {}
        arity_texts: Dict[str, str] = {}

        def view_of(label: str, text: str) -> _ipu._FileView:
            if label not in views:
                views[label] = _ipu._FileView(text)
            return views[label]

        def arity_text_of(label: str, text: str) -> str:
            if label not in arity_texts:
                arity_texts[label] = _strip_for_arity(text)
            return arity_texts[label]

        absorbable = _absorbable_spans(merged.stripped)
        base_stripped = _ipu._strip_comments_and_strings(base_content)
        merged_arity_text = _strip_for_arity(merged_text)

        for x_label, y_label, x_text, y_text in (
                ("ours", "theirs", ours_content, theirs_content),
                ("theirs", "ours", theirs_content, ours_content)):
            for name, records in sig_lists[x_label].items():
                if name in sig_lists[y_label]:
                    continue  # concurrent signature edits — not the clean shape
                pairs = {(c.old_arity, c.new_arity) for c in records}
                if len(pairs) != 1:
                    continue  # ambiguous multi-change evolution for one name
                change = records[0]
                if change.varargs:
                    continue
                if not change.is_ctor and name in _OBJECT_METHODS:
                    continue  # Object provides the name everywhere
                x_view = view_of(x_label, x_text)
                y_view = view_of(y_label, y_text)
                if _any_varargs_form(name, (base_stripped, x_view.stripped,
                                            y_view.stripped, merged.stripped)):
                    continue
                declared = _declared_arities(merged.stripped, name)
                if change.old_arity in declared or change.new_arity not in declared:
                    continue  # old decl/overload survives, or change didn't land
                if name in merged.enum_constants:
                    continue
                if _import_absorbs(merged, name, change.is_ctor):
                    continue
                stale = [
                    s for s in _call_sites(merged, name, change.is_ctor,
                                           merged_arity_text)
                    if s.arity == change.old_arity
                    and (change.is_ctor or not _within(absorbable, s.start))
                ]
                if not stale:
                    continue
                if any(s.arity == change.old_arity
                       for s in _call_sites(x_view, name, change.is_ctor,
                                            arity_text_of(x_label, x_text))):
                    continue  # X not self-consistent — breakage pre-exists X
                if not any(s.arity == change.old_arity
                           for s in _call_sites(y_view, name, change.is_ctor,
                                                arity_text_of(y_label, y_text))):
                    continue  # cannot attribute the stale call to Y
                for site in stale:
                    issues.append(Issue(
                        line_number=site.line,
                        severity="CRITICAL",
                        message=(
                            f"Stale call to '{name}' with pre-change argument count "
                            f"{change.old_arity}: {x_label} changed the signature "
                            f"'{change.old_decl}' -> '{change.new_decl}', and the merged "
                            f"file retains no declaration of '{name}' taking "
                            f"{change.old_arity} argument(s); this call came from "
                            f"{y_label}, where the old signature still existed."
                        ),
                        strategy_name=self.name,
                    ))

        return AnalysisResult(is_clean=(not issues), issues=issues)

    def _inconclusive(self, reason: str) -> AnalysisResult:
        return AnalysisResult(
            is_clean=False,
            issues=[Issue(
                line_number=0,
                severity="CRITICAL",
                message=f"SignatureStaleCall analysis inconclusive: {reason}",
                strategy_name=self.name,
            )],
        )


# --------------------------------------------------------------------------- #
# RM2 payload parsing
# --------------------------------------------------------------------------- #
def _extract_arity_changes(refactorings: list) -> List[_SigChange]:
    """Parse Add/Remove Parameter records into per-name signature changes.

    Probed composition (merge-tools/refactoring-miner:2.4.0, 2026-07-16):
    each record carries the FULL old declaration among leftSideLocations and
    the FULL new declaration among rightSideLocations as codeElementType
    METHOD_DECLARATION entries (the changed parameter rides along as
    SINGLE_VARIABLE_DECLARATION — which is why selection is by element type,
    not position). Records where either declaration is missing/unparseable,
    the names differ (rename+arity composites belong to the rename lane), or
    the parsed arities are equal are dropped.
    """
    out: List[_SigChange] = []
    for r in refactorings:
        if r.get("type") not in ARITY_CHANGE_TYPES:
            continue
        old = _method_decl_element(r.get("leftSideLocations"))
        new = _method_decl_element(r.get("rightSideLocations"))
        if old is None or new is None:
            continue
        parsed_old = _parse_method_decl(old)
        parsed_new = _parse_method_decl(new)
        if parsed_old is None or parsed_new is None:
            continue
        (name_old, arity_old, ctor_old, va_old) = parsed_old
        (name_new, arity_new, ctor_new, va_new) = parsed_new
        if name_old != name_new or arity_old == arity_new:
            continue
        out.append(_SigChange(
            name=name_old,
            old_arity=arity_old,
            new_arity=arity_new,
            is_ctor=ctor_old or ctor_new,
            varargs=va_old or va_new,
            old_decl=old,
            new_decl=new,
        ))
    return out


def _method_decl_element(locations: Optional[list]) -> Optional[str]:
    for loc in locations or []:
        if loc.get("codeElementType") == "METHOD_DECLARATION":
            return loc.get("codeElement") or None
    return None


def _parse_method_decl(code_element: str) -> Optional[Tuple[str, int, bool, bool]]:
    """(name, arity, is_ctor, varargs) from an RM2 METHOD_DECLARATION codeElement.

    Probed shapes: `public send(host String, port int) : int` (method),
    `public Foo(id int, amount int)` (constructor — no ` : ret` suffix),
    varargs rendered as `args Object...`, generics unspaced
    (`m Map<String,List<Integer>>`). Returns None on anything unexpected.
    """
    if "(" not in code_element:
        return None
    head, rest = code_element.split("(", 1)
    tokens = head.split()
    if not tokens or not _IDENT_ONLY_RE.match(tokens[-1]):
        return None
    name = tokens[-1]
    params, close = _match_group(rest, type_context=True)
    if params is None:
        return None
    tail = rest[close + 1:].lstrip()
    is_ctor = not tail.startswith(":")
    varargs = "..." in params
    arity = _count_type_list(params)
    if arity is None:
        return None
    return name, arity, is_ctor, varargs


def _match_group(s: str, type_context: bool) -> Tuple[Optional[str], int]:
    """Content up to the `)` matching an already-consumed `(`, and its index.

    type_context=True additionally tracks `<>` as nesting (RM2 param lists
    and file declaration parameter lists are type contexts — `<`/`>` there
    are always generics, never comparison operators).
    """
    depth = 1
    angle = 0
    for i, c in enumerate(s):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                if angle != 0:
                    return None, -1
                return s[:i], i
        elif type_context and c == "<":
            angle += 1
        elif type_context and c == ">":
            angle -= 1
            if angle < 0:
                return None, -1
    return None, -1


def _count_type_list(params: str) -> Optional[int]:
    """Arity of a TYPE-context parameter list (commas at nesting depth 0)."""
    if not params.strip():
        return 0
    count = 1
    depth = 0
    for c in params:
        if c in "(<[":
            depth += 1
        elif c in ")>]":
            depth -= 1
            if depth < 0:
                return None
        elif c == "," and depth == 0:
            count += 1
    if depth != 0:
        return None
    return count


# --------------------------------------------------------------------------- #
# merged/parent text analysis (all on comment/string-stripped text)
# --------------------------------------------------------------------------- #
def _prev_token(s: str, pos: int) -> Tuple[str, str, int]:
    """(kind, text, index) of what directly precedes offset `pos`, skipping
    whitespace. kind: "word", "char", or "start" (index of its first char)."""
    i = pos - 1
    while i >= 0 and s[i] in " \t\r\n":
        i -= 1
    if i < 0:
        return "start", "", 0
    if _WORD_RE.match(s[i]):
        j = i
        while j >= 0 and _WORD_RE.match(s[j]):
            j -= 1
        return "word", s[j + 1:i + 1], j + 1
    return "char", s[i], i


def _next_word(s: str, pos: int) -> str:
    """The word starting at the first non-whitespace position ≥ pos ('' if none)."""
    i = pos
    while i < len(s) and s[i] in " \t\r\n":
        i += 1
    j = i
    while j < len(s) and _WORD_RE.match(s[j]):
        j += 1
    return s[i:j]


def _type_ish_before(s: str, name_off: int) -> bool:
    """True when the token before offset name_off can end a method
    declaration's return type / modifier chain: a declaration modifier, a
    primitive, a non-keyword identifier, `]` (array type), or a `>` that is
    NOT part of `->` (switch-rule / lambda arrows precede expressions)."""
    kind, tok, idx = _prev_token(s, name_off)
    if kind == "word":
        if tok in _DECL_MODIFIERS or tok in _PRIMITIVES:
            return True
        if tok == "record":
            return True  # `record Name(…)` header declares the canonical ctor
        return tok not in _ipu._KEYWORDS
    if kind == "char":
        if tok == "]":
            return True
        if tok == ">":
            return idx == 0 or s[idx - 1] != "-"
    return False


def _name_paren_sites(stripped: str, name: str):
    """Yield (name_offset, after_open_paren_offset) for each `name (` site."""
    for m in re.finditer(rf"(?<![\w$]){re.escape(name)}\s*\(", stripped):
        yield m.start(), m.end()


def _after_params(stripped: str, after_paren: int, close: int) -> Tuple[str, str]:
    """(first-char, first-word) following the params' closing paren."""
    pos = after_paren + close + 1
    n = len(stripped)
    while pos < n and stripped[pos] in " \t\r\n":
        pos += 1
    ch = stripped[pos] if pos < n else ""
    return ch, _next_word(stripped, pos)


def _is_decl_tail(ch: str, word: str) -> bool:
    """Declaration continuations after `name(…)`: a body, an abstract-method
    `;`, a throws clause, or a record header's extends/implements."""
    return ch in "{;" or word in ("throws", "extends", "implements")


def _declared_arities(stripped: str, name: str) -> Set[int]:
    """Arities at which `name` is DECLARED (method or constructor) in the file.

    A `name(…)` site is a declaration iff its tail continues as a
    declaration (see _decl_tail) and either
      * the token before the name is type-ish (_type_ish_before) — the
        method form — or
      * the site is constructor-shaped: preceded by `{` / `}` / `;` /
        start-of-file AND followed by `{` or `throws` (a call statement can
        be preceded by those chars but is never followed by a block or a
        throws clause; `new Name(…) {` is excluded because its preceding
        token is the word `new`).

    Overbroad on purpose: a false extra declared arity can only SUPPRESS a
    flag (FN direction). Varargs declarations contribute their fixed-prefix
    arity too, but _any_varargs_form() independently suppresses the name.
    """
    out: Set[int] = set()
    for name_off, after_paren in _name_paren_sites(stripped, name):
        params, close = _match_group(stripped[after_paren:], type_context=True)
        if params is None:
            continue
        after_char, after_word = _after_params(stripped, after_paren, close)
        if not _is_decl_tail(after_char, after_word):
            continue
        kind, tok, _idx = _prev_token(stripped, name_off)
        method_form = _type_ish_before(stripped, name_off)
        ctor_form = (
            ((kind == "char" and tok in "{};") or kind == "start")
            and (after_char == "{" or after_word == "throws"))
        if method_form or ctor_form:
            arity = _count_type_list(params)
            if arity is not None:
                out.add(arity)
    return out


def _any_varargs_form(name: str, stripped_texts) -> bool:
    """True if any version's stripped text has a `name(… ...)` parenthesized
    form — an overbroad varargs net across base/ours/theirs/merged
    (JLS 15.12.2.4: a varargs method accepts every arity ≥ its fixed
    prefix, so arity matching is meaningless for the name)."""
    for stripped in stripped_texts:
        for _, after_paren in _name_paren_sites(stripped, name):
            params, _close = _match_group(stripped[after_paren:], type_context=True)
            if params is not None and "..." in params:
                return True
    return False


def _strip_for_arity(text: str) -> str:
    """Comment/string stripping specialized for ARGUMENT COUNTING.

    Same walk (and therefore byte-identical geometry — offsets and line
    numbers align with _ipu._strip_comments_and_strings' output) but a
    different projection: comments blank to spaces, while each string/char/
    text-block literal keeps ONE placeholder byte at its opening quote.
    Rationale: a call like `send("boom")` must count as arity 1, and a
    stale X-side leftover `send("legacy")` must trip the self-consistency
    guard — under a blank-to-space projection a literal-only argument list
    is indistinguishable from `send()`, which both misses genuine stale
    calls AND false-flags legal calls when the old arity was 0. A comment-
    only interior (`send(/* x */)`)  stays arity 0 under both projections.
    Deliberate lane-local fork of the D1 stripper: the projections differ
    semantically; D1's is still used for every structural scan.
    """
    out = list(text)
    i, n = 0, len(text)

    def blank(a: int, b: int, keep_first: bool) -> None:
        for k in range(a, min(b, n)):
            if out[k] == "\n":
                continue
            out[k] = "\x00" if (keep_first and k == a) else " "

    while i < n:
        c = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if c == "/" and nxt == "/":
            j = text.find("\n", i)
            j = n if j == -1 else j
            blank(i, j, keep_first=False)
            i = j
        elif c == "/" and nxt == "*":
            j = text.find("*/", i + 2)
            j = n if j == -1 else j + 2
            blank(i, j, keep_first=False)
            i = j
        elif text.startswith('"""', i):
            j = i + 3
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text.startswith('"""', j):
                    j += 3
                    break
                j += 1
            blank(i, j, keep_first=True)
            i = j
        elif c == '"' or c == "'":
            quote = c
            j = i + 1
            while j < n:
                if text[j] == "\\":
                    j += 2
                    continue
                if text[j] == quote or text[j] == "\n":
                    j += 1
                    break
                j += 1
            blank(i, j, keep_first=True)
            i = j
        else:
            i += 1
    return "".join(out)


def _call_sites(view: "_ipu._FileView", name: str, is_ctor: bool,
                arity_text: str) -> List[_CallSite]:
    """Unqualified call-form occurrences of `name` in a _FileView.

    Reuses the view's exclusion machinery: import/package statements,
    `.`/`::`-qualified positions, and `case` labels never count. Constructor
    signatures require the `new`-prefixed form `new Name(…)`; method
    signatures reject it (a `new`-prefixed occurrence is a constructor of a
    same-named class). Declaration-shaped sites are excluded. Argument
    counting runs over `arity_text` (_strip_for_arity of the same original —
    identical geometry, literal placeholders preserved); sites whose list
    cannot be counted unambiguously get arity None and are dropped by the
    caller (FN direction).
    """
    s = view.stripped
    out: List[_CallSite] = []
    for name_off, after_paren in _name_paren_sites(s, name):
        if view._in_excluded(name_off):
            continue
        if view._qualified_or_case(name_off):
            continue
        kind, tok, _idx = _prev_token(s, name_off)
        new_prefixed = (kind == "word" and tok == "new")
        if is_ctor != new_prefixed:
            continue
        if not is_ctor and _looks_like_decl(s, name_off, after_paren):
            continue
        arity = _call_arity(arity_text, after_paren)
        line = s.count("\n", 0, name_off) + 1
        out.append(_CallSite(line=line, start=name_off, arity=arity))
    return out


def _looks_like_decl(s: str, name_off: int, after_paren: int) -> bool:
    if not _type_ish_before(s, name_off):
        return False
    params, close = _match_group(s[after_paren:], type_context=True)
    if params is None:
        return True  # unparseable after a type-ish prefix: treat as decl (FN)
    return _is_decl_tail(*_after_params(s, after_paren, close))


def _call_arity(s: str, after_paren: int) -> Optional[int]:
    """Argument count of the call whose `(` ends at after_paren-1.

    Expression context: `(`/`)`, `[`/`]`, `{`/`}` nest; `<…>` spans hide
    their commas ONLY when they positively look like a generic argument
    list (follow an identifier, contain only type-shaped comma-pieces whose
    head is uppercase / a primitive / `?`, and are followed by a character
    a generic type can legally precede in an expression: `(`, `)`, `,`,
    `>`, `::`, `[`). Everything else leaves `<`/`>` as comparison
    operators. A site where a candidate generic span cannot be classified
    is reported as None — the caller drops it (never guesses toward FLAG).
    """
    depth = 1
    count: Optional[int] = 0
    i = after_paren
    n = len(s)
    any_content = False
    while i < n:
        c = s[i]
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                if count is None:
                    return None
                return count + 1 if any_content else 0
        elif depth == 1 and c == ",":
            if count is not None:
                count += 1
        elif depth == 1 and c == "<":
            span = _generic_span(s, i)
            if span == -2:
                count = None  # ambiguous — poison the site
            elif span >= 0:
                i = span + 1  # generic argument list — hide its content
                any_content = True
                continue
            # span == -1: comparison operator — commas stay visible
        if c not in " \t\r\n":
            any_content = True
        i += 1
    return None  # unbalanced (merge artifact)


def _generic_span(s: str, lt: int) -> int:
    """Classify `<` at offset lt: matching `>` offset if it is a generic
    argument list, -1 if it reads as a comparison, -2 if ambiguous.

    The follower decides (given type-shaped uppercase/`?`/primitive pieces):
      * `(`  — a generic before an argument list occurs in call arguments
        only as `new Type<…>(…)`; it is trusted ONLY when the type is
        `new`-rooted. A bare `A < B, C > (d)` is two PascalCase comparisons
        (legal Java) whose hidden comma would undercount the arity, and a
        `CONST < LIMIT, X > (y)` chain is the same trap — both fall here
        and poison the site (-2) instead. This rule also lets single-letter
        type arguments (`new Box<T>()`) count normally — no case-shape
        veto needed.
      * `,` / `)` / `>` / `[` / `::` — structurally generic-only: a
        comparison chain `a < b, c >` would need a right operand after the
        `>`, so these follower characters cannot close a comparison.
      * an identifier or `.` — `Foo<A> x` shapes don't occur in call
        arguments; ambiguous (-2).
    """
    kind, _tok, tok_idx = _prev_token(s, lt)
    if kind != "word":
        return -1
    depth = 0
    i = lt
    n = len(s)
    while i < n:
        c = s[i]
        if c == "<":
            depth += 1
        elif c == ">":
            depth -= 1
            if depth == 0:
                break
        elif c in ");{}=+-|&!":
            return -1  # expression characters — not a type argument list
        i += 1
    else:
        return -1
    content = s[lt + 1:i]
    if content.strip():
        pieces = _split_type_pieces(content)
        if pieces is None:
            return -1
        for piece in pieces:
            piece = piece.strip()
            head = re.match(r"[?\w$]+", piece)
            if not head:
                return -1
            word = head.group(0)
            if not (word == "?" or word in _PRIMITIVES or word[0].isupper()):
                return -1  # lowercase head: reads as a value expression
    j = i + 1
    while j < n and s[j] in " \t\r\n":
        j += 1
    nxt = s[j] if j < n else ""
    if nxt == "(":
        return i if _new_rooted(s, tok_idx) else -2
    if nxt in "),>[":
        return i
    if nxt == ":" and j + 1 < n and s[j + 1] == ":":
        return i
    return -2 if (nxt == "." or (nxt and _WORD_RE.match(nxt))) else -1


def _new_rooted(s: str, type_start: int) -> bool:
    """True when the (possibly dot-qualified) type name starting at
    type_start is the operand of a `new` expression: `new Foo<…>(`,
    `new a.b.Foo<…>(`."""
    pos = type_start
    while True:
        kind, tok, idx = _prev_token(s, pos)
        if kind == "char" and tok == ".":
            kind2, _tok2, idx2 = _prev_token(s, idx)
            if kind2 != "word":
                return False
            pos = idx2
            continue
        return kind == "word" and tok == "new"


def _split_type_pieces(content: str) -> Optional[List[str]]:
    pieces: List[str] = []
    depth = 0
    cur: List[str] = []
    for c in content:
        if c == "<":
            depth += 1
        elif c == ">":
            depth -= 1
            if depth < 0:
                return None
        elif c == "," and depth == 0:
            pieces.append("".join(cur))
            cur = []
            continue
        cur.append(c)
    if depth != 0:
        return None
    pieces.append("".join(cur))
    return pieces


# --------------------------------------------------------------------------- #
# absorbability: spans where an unqualified call may bind an inherited member
# --------------------------------------------------------------------------- #
_TYPE_HEADER_RE = re.compile(r"\b(class|interface|enum|record)\s+([A-Za-z_$][\w$]*)")
# Optional type-use annotations (with simple argument lists) may sit between
# `new` and the type: `new @NonNull Foo() { … }` is an anonymous class too.
_ANON_NEW_RE = re.compile(
    r"\bnew\s+(?:@[\w$.]+(?:\s*\([^()]*\))?\s+)*[\w$.]+")


def _absorbable_spans(stripped: str) -> List[Tuple[int, int]]:
    """Spans of type bodies that may inherit unseeable members.

    * A named type whose header (outside its type-parameter `<…>` group and
      a record's component `(…)` group) contains `extends`/`implements` —
      the supertype may declare the method. JLS 6.5.7.1 resolves an
      unqualified method name through the inherited members of EVERY
      enclosing class, so containment in ANY supertyped span suppresses —
      no ancestor propagation needed.
    * Every enum body (enums implicitly extend java.lang.Enum).
    * Every anonymous-class body `new T(…) { … }` (it inherits T wholesale).

    On any parse anomaly the whole file is returned as one absorbable span —
    suppression is the safe direction.
    """
    n = len(stripped)
    spans: List[Tuple[int, int]] = []
    try:
        for m in _TYPE_HEADER_RE.finditer(stripped):
            keyword = m.group(1)
            i = m.end()
            clause_words: List[str] = []
            word: List[str] = []
            while i < n:
                c = stripped[i]
                if c == "<":
                    i = _skip_angles(stripped, i)
                    continue
                if c == "(":
                    i = _ipu._skip_group(stripped, i, "(", ")")
                    continue
                if c == "{" or c == ";":
                    break
                if _WORD_RE.match(c):
                    word.append(c)
                else:
                    if word:
                        clause_words.append("".join(word))
                        word = []
                i += 1
            if word:
                clause_words.append("".join(word))
            if i >= n or stripped[i] != "{":
                continue
            body_end = _ipu._skip_group(stripped, i, "{", "}")
            if (keyword == "enum" or "extends" in clause_words
                    or "implements" in clause_words):
                spans.append((i, body_end))
        for m in _ANON_NEW_RE.finditer(stripped):
            i = m.end()
            while i < n and stripped[i] in " \t\r\n":
                i += 1
            if i < n and stripped[i] == "<":
                i = _skip_angles(stripped, i)
                while i < n and stripped[i] in " \t\r\n":
                    i += 1
            if i < n and stripped[i] == "(":
                i = _ipu._skip_group(stripped, i, "(", ")")
                while i < n and stripped[i] in " \t\r\n":
                    i += 1
                if i < n and stripped[i] == "{":
                    spans.append((i, _ipu._skip_group(stripped, i, "{", "}")))
    except Exception:  # noqa: BLE001 — parser anomaly: suppress everything
        return [(0, n)]
    return spans


def _skip_angles(s: str, i: int) -> int:
    depth = 0
    n = len(s)
    while i < n:
        if s[i] == "<":
            depth += 1
        elif s[i] == ">":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def _within(spans: List[Tuple[int, int]], pos: int) -> bool:
    return any(a <= pos < b for a, b in spans)


def _import_absorbs(view: "_ipu._FileView", name: str, is_ctor: bool) -> bool:
    """Static import (explicit-of-name or any static wildcard) can provide an
    unqualified METHOD `name`; a single-type import of `name` can shadow a
    nested class for CONSTRUCTOR calls."""
    for im in view.imports:
        if is_ctor:
            if not im.is_wildcard and im.simple == name:
                return True
        else:
            if im.is_static and (im.is_wildcard or im.simple == name):
                return True
    return False


def _clean() -> AnalysisResult:
    return AnalysisResult(is_clean=True, issues=[])
