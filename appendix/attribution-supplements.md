# Attribution supplements

Appendix items of the thesis that are published here rather than printed (end-game step 3, applying the classification ruled 2026-09-13). Each item opens with its printed home, or states that it has none. `§n.m` names a section of the printed thesis and `Table Tn.m` one of its tables; `D-nnn` is an entry of `docs/DECISIONS.md`; a bracketed tag such as `[TierTrajectories]` is a row of `thesis/claims-ledger.md`, listed under *Claims used* at the end of the file. Item identifiers are the ones the working files carried, so an identifier is unambiguous only together with its file name; the printed appendices number their own items (A.1–A.3, B.1–B.2, C.1–C.2), and every printed pointer to this repository names the file.

## C.1 The draft-ruling audit's verification procedure

Printed home: §9.6, which keeps the audit's actor and its outcome; the record is `merge-tool-comparison/reports_taxonomy/phase3/adjudication/adjudication_record.md` and `reports_taxonomy/FINDINGS.md` §3.2.

> That audit validates the draft rulings programmatically and re-verifies at code level every session-discussed case and every ruling that asserts a positive, not-yet-verified mechanism. For this case the verification searched for the decisive quote in the unit's actual input and found zero occurrences, and the case was flagged at the audit's hardest severity.

## C.2 The exported adjudication record

Printed home: §9.6, which keeps the four flags and the three revisions; the record is the same file, and the ledger row carries the path and the 2 HARD / 1 MEDIUM / 1 SOFT breakdown.

> The exported record keeps all four flags and their resolutions (`adjudication_record.md`, original spelling).

## C.3 The two held-out population defects, itemized

Printed home: §8.4.5, which keeps the two defects and the re-read; §8.2 states the counting ruling they produced.

> One defect was two merges each counted twice under two repository names, one of them flagged in both copies. The other was a held-out unit that is a fork twin of a unit the D1 lane was specified from.

## C.4 The decision record's extraction-protocol detail

Printed home: §9.2, which keeps the live counts, and §9.3, which names the frozen extraction protocol; the record is the `docs/DECISIONS.md` header and `docs/decision-record/PROTOCOL.md`.

> A decision log rebuilt on 2026-07-25 under a frozen extraction protocol, from the distilled session transcripts plus the plan documents and commit log of the pre-transcript period. […] Each entry carries a status, a provenance tag, an actor field, and verbatim quotes that are machine-verified against their sources.
>
> […] the record was rebuilt under a protocol whose coverage is structural: every extraction request contains the whole source file, and completeness is machine-checked per file.

## C.5 What the pre-transcript commits cover

Printed home: §9.2, which keeps the window (2026-04-15 to 2026-05-18), the 59-commit count.

> Those commits cover the initial import, the first comparator tiers, and the first integrations.

## C.6 §9.3's ruling-groups breakdown

Printed home: §11.5, which states that I ruled every label Table T5.3 counts; §9.3's Table T9.1 lists the rulings per artifact, and Table T5.3 (printed Appendix A) is the per-group record.

> The ruling groups are:
> - the two routing refutations and the flip approval of Chapter 6;
> - every detection flag on positives and controls, including the four session-stopping control flags `[RulingRounds]`;
> - the full count's codebook, category by category, plus its 47 disagreements and the 12-unit audit `[RulingRounds]`;
> - the external benchmark's category mapping, row by row;
> - the pilot drafts, which are ruled but never cited.

## C.7 The reading discipline for this chapter

Printed home: §9.2, which carries the re-derivation markers; the claims-ledger convention is stated in `thesis/00-spine.md` and holds in every chapter.

> The reading discipline for this chapter follows from the sources. Empirical numbers from the measurement instruments keep their claims-ledger tags, as in every chapter. Process facts are stated with a source pointer. […] The decision totals, the transcript coverage, and the review-round counts above and below are the cases in point.

## C.8 The review flow's branch mechanics and the ruled-text rule

Printed home: §9.1, which keeps the pull-request review flow and names the contract; the rest survives only here and in `thesis/WORKFLOW.md` R1–R13.

> Each chapter is drafted by the assistant from the frozen record, on its own branch, and submitted as a pull request. […] Text I have approved is ruled text and is not rewritten without a new ruling.

## C.9 The full-count labeling pass's own name

Printed home: §9.6, which keeps the episode and its actors; §7.3 names pass b.

> One pass had labeled the unit an interleaving artifact. That pass is the record's pass b (§7.3).

## C.10 The mis-scored run's second error

Printed home: none, by Ali's ruling of 2026-09-10; §9.6 keeps the wrong cost tables, the assistant's supersession (D-172) and my later ratification, and this record (`merge-tool-comparison/reports_whole_driver/FINDINGS.md`, v1 and its superseding v2; D-172) is the fact's only home.

> The first findings document had also named the wrong environment as the degraded one.

## C.11 The ruling audit's scope bound

Printed home: §7.4.4, which states the claim in full; §9.6 no longer carries it, by Ali's ruling of 2026-09-10. The record is `merge-tool-comparison/reports_taxonomy/phase3/adjudication/adjudication_record.md`.

> The audit covers only units that entered the ruling set, so a fabricated quote inside an agreed, unsampled pair of labels would not have faced it.

## Claims used

- RulingRounds
