# Appendix (candidate): attribution supplements

Status: skeleton created by the ch.9 compression session (2026-09-10, Option C disposition ruled by Ali the same day; source text verbatim from merged draft-r6 except the flagged pointer edits) · Every item is marked **appendix-candidate** or **repo-cite (recommended)**; final print-appendix curation is Ali's end-of-wave ruling · **An appendix item does not shrink the printed thesis — only a repo-cite item does.** Both totals are quoted below · Appendix letter assigned at curation · Pointer edits applied to moved text: the ch.5 flatten retargets (§5.3.4/§5.3.5 → §5.3, §5.4.x → §5.4, §5.5.x → §5.5) — each flagged per item; no other wording changed · Narrative: none

**Totals.** Eleven items, 405 words of quoted source text. Eight are marked repo-cite (recommended), 335 words. Three are marked appendix-candidate, 70 words: keeping those in a print appendix moves them without shrinking the thesis. If Ali rules every item repo-cite, the print saving is 405.

C.10 and C.11 differ from the rest: Ali ruled both out of the printed chapter on 2026-09-10, so they are already gone from ch.9 rather than awaiting a curation ruling. Their 40 words are counted above and are already banked in the chapter's total.

## C.1 The draft-ruling audit's verification procedure — repo-cite (recommended)

Chapter home: §9.6 (the audit's actor, its severity flag and its outcome all stay in print). Repo record: `merge-tool-comparison/reports_taxonomy/phase3/adjudication/adjudication_record.md`; FINDINGS.md §3.2.

> That audit validates the draft rulings programmatically and re-verifies at code level every session-discussed case and every ruling that asserts a positive, not-yet-verified mechanism. For this case the verification searched for the decisive quote in the unit's actual input and found zero occurrences, and the case was flagged at the audit's hardest severity.

## C.2 The exported adjudication record — repo-cite (recommended)

Chapter home: §9.6 (the four flags and the three revisions stay in print, tagged `[DraftRulingAudit]`). Repo record: the same file; the ledger row carries the path and the 2 HARD / 1 MEDIUM / 1 SOFT breakdown.

> The exported record keeps all four flags and their resolutions (`adjudication_record.md`, original spelling).

## C.3 The two held-out population defects, itemized — appendix-candidate

Chapter home: §9.6 keeps "two population defects" and my ruling on both. Ch.8 §8.4.5 states the counting ruling they produced.

> One defect was two merges each counted twice under two repository names, one of them flagged in both copies. The other was a held-out unit that is a fork twin of a unit the D1 lane was specified from.

## C.4 The decision record's extraction-protocol detail — repo-cite (recommended)

Chapter home: §9.2 keeps the protocol's existence, the entry fields, and the live counts behind their `[VERIFY:]` marker. Repo record: the `docs/DECISIONS.md` header and the committed extraction protocol.

> A decision log rebuilt on 2026-07-25 under a frozen extraction protocol, from the distilled session transcripts plus the plan documents and commit log of the pre-transcript period. […] Each entry carries a status, a provenance tag, an actor field, and verbatim quotes that are machine-verified against their sources.
>
> […] the record was rebuilt under a protocol whose coverage is structural: every extraction request contains the whole source file, and completeness is machine-checked per file.

## C.5 What the pre-transcript commits cover — appendix-candidate

Chapter home: §9.2 keeps the window (2026-04-15 to 2026-05-18), the 59-commit count, and the reconstructed marking.

> Those commits cover the initial import, the first comparator tiers, and the first integrations.

## C.6 §9.3's ruling-groups breakdown — repo-cite (recommended)

Chapter home: §9.3 keeps the claim that I ruled every label Table T5.3 counts. T5.3 itself (methodology-supplements A.3) is the per-group record, and ch.11 §11.5 cites it directly rather than ch.9's list. Pointer edits flagged: §5.4.6 → §5.4 per the ch.5 flatten rows.

> The ruling groups are:
> - the two routing refutations and the flip approval of Chapter 6;
> - every detection flag on positives and controls, including the four session-stopping control flags `[RulingRounds]`;
> - the full count's codebook, category by category, plus its 47 disagreements and the 12-unit audit `[RulingRounds]`;
> - the external benchmark's category mapping, row by row;
> - the pilot drafts, which are ruled but never cited.

## C.7 The reading discipline for this chapter — repo-cite (recommended)

Chapter home: §9.2 keeps the re-derivation-marker rule, which is the only part with a consequence for the reader. The claims-ledger convention is stated in `00-spine.md` and holds in every chapter.

> The reading discipline for this chapter follows from the sources. Empirical numbers from the measurement instruments keep their claims-ledger tags, as in every chapter. Process facts are stated with a source pointer. […] The decision totals, the transcript coverage, and the review-round counts above and below are the cases in point.

## C.8 The review flow's branch mechanics and the ruled-text rule — repo-cite (recommended)

Chapter home: §9.2 keeps the pull-request flow, the directive status of inline comments, the no-silent-application rule, the 🤖 marker, the citation-placeholder rule and the multi-agent review. Repo record: `thesis/WORKFLOW.md` R1–R13, which §9.2 already names as the contract.

> Each chapter is drafted by the assistant from the frozen record, on its own branch, and submitted as a pull request. […] Text I have approved is ruled text and is not rewritten without a new ruling.

## C.9 The full-count labeling pass's own name — appendix-candidate

Chapter home: §9.6 keeps the episode and its actors. Ch.7 §7.3 is the print home for the *pass b* naming, and ch.7's own retarget map records that.

> One pass had labeled the unit an interleaving artifact. That pass is the record's pass b (§7.3).

## C.10 The mis-scored run's second error — repo-cite (recommended)

Chapter home: §9.6 keeps the wrong cost tables, the assistant's own cross-environment audit (D-172) and my superseding ruling. **Ruled out of print by Ali, 2026-09-10.** This fact is stated nowhere else in the thesis, so the repo record is now its only home. Repo record: `merge-tool-comparison/reports_whole_driver/FINDINGS.md` (the v1 findings document and its superseding v2); D-172.

> The first findings document had also named the wrong environment as the degraded one.

Note: §9.6's closing sentence read "corrects the tables and the misattribution in the open". With this item out of print it reads "corrects the tables in the open" — the count was corrected with the cut, not left dangling.

## C.11 The ruling audit's scope bound — repo-cite (recommended)

Chapter home: **none in §9.6 any more.** Ruled out of ch.9 by Ali, 2026-09-10. The claim itself stays in print at **ch.7 §7.4.4**, which states it in full, so nothing is orphaned. Repo record: `merge-tool-comparison/reports_taxonomy/phase3/adjudication/adjudication_record.md`.

> The audit covers only units that entered the ruling set, so a fabricated quote inside an agreed, unsampled pair of labels would not have faced it.

**Housekeeping action required** — see `thesis/audits/ch9-retarget-map.md`, required row Q1: ch.11 §11.6 cites the pair `(§7.4.4, §9.6)` for this claim, and the `§9.6` half is now stale.

## Claims used

- DraftRulingAudit
- RulingRounds
