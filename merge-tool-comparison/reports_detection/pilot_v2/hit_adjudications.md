# v2 Hit Adjudications — plan §4.6 (DRAFT for Ali's confirmation)

Two hits, both on pilot positives. Protocol per plan §4.6: (i) pattern actually present in merged output? (ii) merge-induced (absent in both parents)? (iii) plausibly linked to the test failure? Label: CAUSAL / REAL-BUT-INCIDENTAL / DETECTOR-FP.

## Hit 1 — erudika_para__a9e67cc8b3 (`IndexAndCacheAspect.java`) — proposed: **CAUSAL**

- **(i) Present:** yes — merged file declares `Method method = mi.getMethod()` and still calls `detectNestedInvocations(m)` at L109 (verified by inspection at Stage A AND independently by Joern scope analysis: `m` has no `refsTo` declaration).
- **(ii) Merge-induced:** yes — ours renamed `m→method` throughout; theirs added `detectNestedInvocations(m)`. Neither parent contains the mixed state; both detectors' differential lanes confirm (unresolved in merged only; rename per-branch with stale ref).
- **(iii) Linked to test failure:** yes — undeclared variable ⇒ the file does not compile ⇒ `Tests_failed` for the whole merge is fully explained (compilation is a precondition of the suite).
- Flagged by BOTH `JoernUnresolvedReference` and `RM2RenameConflict` v2 — independent lanes, same root cause.

## Hit 2 — jacquesberger_jsonparsingexample__ac521954c2 (`JSON.java`) — proposed: **CAUSAL**

- **(i) Present:** yes — `saveToFiles` declares `outputList` but calls `saveAsRawJsonFile(bookTitleList)`; `initializeBookList` declares `bookTitleList` but returns `outputList`. Both halves of the half-applied rename are out of scope at their use sites (Joern: both unresolved in merged).
- **(ii) Merge-induced:** yes — the rename `bookTitleList→outputList` came from one branch, the conflicting uses from the other; both parents are internally consistent (detector found neither identifier unresolved in either parent).
- **(iii) Linked to test failure:** yes — two undeclared-variable compile errors ⇒ `Tests_failed` explained.

## Control side

0/30 controls blocked — no FP adjudications required.
