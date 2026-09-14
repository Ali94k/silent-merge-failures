# Appendix (candidate): driver supplements

Status: skeleton created by the ch.4 compression session (2026-09-10, Option-B disposition with cut A; source text verbatim from merged draft-r3 except the flagged pointer edits) · Every item is marked **appendix-candidate** or **repo-cite (recommended)**; final print-appendix curation is Ali's end-of-wave ruling · Appendix letter assigned at curation · Pointer edits applied to moved text: none — every §-pointer in the moved text is carried as merged · Narrative: none

## D.1 The default strategies' documented limits — repo-cite (recommended)

Chapter home: §4.4.2, which states each strategy's shape, its partial-coverage clause, and the read forms of the category-#3 shape, and points here as the repo record. Table T4.2 carries the per-category coverage. Repo record: the strategy sources under `semantic_merge_driver/strategies/`, where each limit is a code comment.

- **`JoernInfiniteLoop`** — the matching rule is deliberately coarse, and coarseness here means fewer flags, not more: the more easily a merged loop matches something in a side, the more often the flag is suppressed. Coverage is partial, for literal conditions only. `for (;;)` and conditions that only evaluate to a constant are not matched. There is no reasoning about bounds.
- **`JoernInvalidLoopBounds`** — coverage is partial, for literal initializer-versus-bound contradictions only.
- **`JoernDataFlowInterference`** — four limits, explicit in the code.
  - *Ordering* — by line number, not by control or data flow, so conditional clears, loops, and early returns are unmodelled.
  - *Matching* — by method name only, without types, so `clear()` on a non-collection can match.
  - *Reset form* — only a literal `.clear()` counts as a reset. A reset written as a reassignment is a documented miss (for example `cache = new ArrayList<>()`).
  - *Scope* — intra-method and intra-file.
- **`RM2RenameConflict`** — qualified calls such as `this.getName()` count as use sites. Method references such as `Foo::getName` do not.

## D.2 `JoernUnresolvedReference`'s two parser quirks — repo-cite (recommended)

Chapter home: §4.4.2, which states that two parser quirks get their own handling and names the strategy sources as the record. Repo record: `semantic_merge_driver/strategies/joern_strategies/`.

- *Compiler-generated temporaries* — these names are filtered out.
- *Lambda renumbering* — the parser renumbers lambdas per file, so the suppression rule matches on the identifier name alone. Numbering drift cannot break the suppression.

## D.3 The D1 lane's five guards — appendix-candidate

Chapter home: §4.4.3 (the print text states that five guards suppress the flag, and keeps the wildcard guard in full because Chapter 8 measures its cost). Note: `detection-supplements` B.6 walks these same five guards against a worked unit, so curating both items repo-only would leave the guard set with no print carrier.

Guards suppress the flag when the name still resolves without the lost import.

- *Wildcard* — a non-static wildcard import still present in the merged file silences the lane for every type name in the file, whatever package it names. The guard is broader than the case it protects against. Its cost is measured in §8.4.8.
- *`java.lang`* — `java.lang` names never need an import.
- *Own package* — a type from the file's own package does not need an import either.
- *Shadowing* — a local declaration can shadow the name.
- *Absorption* — a side that already used the name without the import shows that the breakage, if any, is not merge-induced: either the name resolves some other way, or that side was already broken.

## D.4 The D2 lane's four guards — appendix-candidate

Chapter home: §4.4.3 (the print text states that four guards temper the flag, and keeps the same-arity documented false negative).

- *Varargs* — a varargs method accepts any argument count, so the flag is suppressed.
- *Overload* — an overload at the old arity may accept the call, so the flag is suppressed.
- *Absorption* — an unqualified call inside a subclass body may reach an inherited method, so the flag is suppressed.
- *Attribution* — the stale call must trace to the side that never saw the new signature. An old-arity call left on the changing side would mean that side was already broken before the merge.

## D.5 The lanes' worked shapes — appendix-candidate

Chapter home: §4.4.3 (the print text states each lane's shape and its partial-coverage clause).

- **D1, `ImportPruneUsage`.** Say the pruning side deletes `import java.util.Optional;` after removing its last use, and the other side adds a use of `Optional`. The merge combines the prune with the new use, and the merged file references a name whose import is gone. The imports lost relative to the two sides yield the candidate names: imports(ours) ∪ imports(theirs) − imports(merged). An unqualified use of a candidate in the merged file is flagged.
- **D2, `SignatureStaleCall`.** One side turns `send(msg)` into `send(msg, retries)`. The other side adds a call `send(msg)`. The merged file contains the new declaration and the old-shape call.
- **D3.** The reference kinds the pre-pass flags are a field use for a field, a call for a method, and a `new`, supertype, or `throws` position for a type. The same style of absorption and attribution guards as in D1 and D2 applies.

Chapter home: §4.4.3 states each lane's shape and its partial-coverage clause, and points here for the guards and worked shapes.

## D.7 The as-built flow, step by step — repo-cite (recommended)

Chapter home: §4.2 (Figure F4.1 carries all five steps, which is why the numbered walk left print). Repo record: `semantic_merge_driver/core/sq.md`, the runtime sequence diagram the figure is drawn from.

1. Git matches the `.gitattributes` rule and executes the driver with the three file paths.
2. The driver captures the contents of ours and theirs before merging. Backends overwrite the ours file in place, and the differential strategies (§4.4) later need the original two sides.
3. The selected backend performs the three-way merge. It reports `CLEAN`, `CONFLICT`, or `CRASH`.
4. A plugin loader discovers every strategy class under `strategies/` and instantiates those enabled in the shipped configuration file. Each strategy receives the merged file plus the base, ours, and theirs contents, and returns an analysis result.
5. The exit code follows the decision procedure of Figure F4.1.

## Claims used

(None — the moved text carries no ledger tags. Ch.4's single tag, `DriverTestSuite`, stays in print at §4.2.)
