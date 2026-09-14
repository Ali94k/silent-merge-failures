# S-D4 §12-Amendment-3 review pass (c) — open-source practice comparison

**Scope:** the D3 widening (textual removed/renamed-declaration differential in
`JoernUnresolvedReference`) checked against how established analyzers handle
unresolved/dangling references and rename propagation. Consult-don't-port;
no new runtime dependencies. Compiled 2026-07-16 (ISSUES #31 S-D4).

## 1. Error Prone (google/error-prone)

Consulted: errorprone.info/docs/criteria; check_api `ErrorProneAnalyzer.java`;
errorprone.info/docs/plugins.

Runs inside javac on the ANALYZE task event — only after attribution has
produced a fully resolved AST; checks are written against resolved symbols.
An unresolved name is a javac error before any check fires, and the analyzer
bails per-unit on new errors and catches `CompletionFailure` for off-classpath
symbols — incomplete resolution is an environment fault to survive, not a bug
pattern to report. No dangling-reference check exists.
**Implication:** non-applicable at mechanism level (it presupposes exactly the
resolution a merge-time lane lacks). Its default-on ERROR-check bar — "should
have no false positives" — is the citable precedent for the zero-FP criterion.

## 2. SpotBugs

Consulted: spotbugs.readthedocs.io introduction + FAQ (aux classpath).

Bytecode-only: input has by construction passed javac resolution — a stale
reference to a removed declaration cannot reach its analysis stage. Facing its
own incompleteness (missing aux-classpath classes) it reports-and-degrades,
with the documented fix being to restore resolution.
**Implication:** corroborates that this defect class is inherently
merge-time/pre-compile — bytecode tools structurally cannot own it. Divergence:
SpotBugs accepts precision loss under incomplete information; the zero-FP lane
suppresses instead.

## 3. IntelliJ IDEA

Consulted: jetbrains.com/help/idea/rename-refactorings.html; Maven dependency
docs; JetBrains support thread on red-code-despite-compiling.

The unresolved-reference ("red code") inspection is the resolution-based
analogue of the lane's target, but JetBrains' own guidance treats red code
under an incomplete project model as an environment false alarm (re-sync, fix
roots, invalidate caches — don't trust the highlight). Rename refactoring
updates *resolved* references automatically and demotes everything else to
opt-in textual search ("Search in comments and strings" / "Search for text
occurrences") gated behind a human-reviewed Preview.
**Implication:** agreement on the epistemics — a name-match without resolution
is only a candidate. IntelliJ resolves residual uncertainty with a human
preview; the lane replaces that gate with conservative suppression
(survives-declaration / inheritance spans / imports / remover-side-still-uses).
Rename residue in unresolvable positions is a tool-acknowledged failure mode.

## 4. Checkstyle

Consulted: checkstyle.sourceforge.io/writingchecks.html#Limitations;
checks/imports/unusedimports.html.

The closest architectural relative: single-file token/AST analysis, no type or
inheritance resolution; the docs explicitly enumerate checks it refuses to
implement for that reason — notably "unused public methods," a near-mirror of
stale-reference detection. `UnusedImports` documents its heuristic ceiling
candidly (wildcards "too dynamic"; same-name field confusion; Javadoc
heuristics), erring toward false negatives on ambiguity.
**Implication:** the resolution-free single-file regime is viable only with
documented shape restrictions and suppress-on-ambiguity — the lane's guard
list is the same design pattern, plus a capability Checkstyle lacks: three-way
differential evidence substituting for resolution (the base+exactly-one-parent
declaration trigger).

## Prior art for the three-way differential

- **SafeMerge** (Sousa/Dillig/Lahiri, OOPSLA 2018): verified three-way merge
  via 4-way differencing — the paradigm of judging the merge relative to base
  and both parents.
- **IntelliMerge** (OOPSLA 2019) / **RefMerge** (EMSE 2022): refactoring-aware
  mergers matching renamed elements across base/ours/theirs — prior art for
  treating a rename on one parent as the explanation for a "missing"
  declaration (the lane's remover-side evidence).
- **Barbosa et al. 2023** + **RefFilter 2025**: differential static analyses
  over merge quadruples from the spgroup mergedataset (this project's Phase-2b
  corpus); refactoring-awareness used explicitly as an FP filter.
- **Towqir et al., ASE 2022** (build-conflict detection for Java merges):
  the nearest neighbor — predicts compile-breaking merge outcomes (including
  removed/renamed declarations still referenced) statically over the three
  versions without building.

## Dispositions

- **Adopted from comparators: nothing ported** (no new runtime dependencies —
  Amendment-3 bound). Error Prone's zero-FP ERROR-check policy cited as
  precedent; Checkstyle's documented-limitation practice mirrored in the lane
  header's deliberate-non-cover list.
- **Deliberately divergent:** (i) no symbol resolution at all — IntelliJ shows
  resolution-based unresolved-reference flagging is untrustworthy exactly when
  the world model is incomplete, and a merged-but-unbuilt tree is the extreme
  case (also the Stage-B javasrc2cpg lesson); (ii) suppression replaces
  IntelliJ's human preview gate; (iii) three-way differential evidence
  (base + exactly-one-parent declaration + remover/keeper usage attribution)
  substitutes for resolution — established in the merge-tooling literature
  (SafeMerge, IntelliMerge, Towqir) though absent from all four linters.
