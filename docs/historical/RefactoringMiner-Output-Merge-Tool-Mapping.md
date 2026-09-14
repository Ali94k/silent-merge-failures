# RefactoringMiner Output Merge Tool Mapping — archive note

Archived 2026-09-09 on Ali's ruling (thesis housekeeping-02, item A31), closing the ch.9 `[VERIFY: mapping-document archiving]` marker.

- **File:** `RefactoringMiner Output Merge Tool Mapping.pdf` in this directory. 8 pages, Google Docs export. The plans that cite it date the document 2026-04-23; the PDF export itself is stamped 2026-04-24.
- **Authorship:** written by Ali in April 2026, before the integration plans existed, using a separate AI analysis tool. It was not produced by the project's coding assistant. Thesis ch.6 §6.1, ch.9 §9.1 and Table T9.1 record it as one of the four design-phase AI uses outside the assistant.
- **Role in the record:** the source of the merge-tool pairing conjecture. It maps RefactoringMiner 2 output types onto merge tools by algorithmic paradigm, and the two routing arms S2 (`INTRA_BODY` → Spork) and W5 (`MIGRATE_DECL` → Weave) were derived from it as hypotheses. It is cited by `docs/plans/spork-driver-integration.md` (line 54) and `docs/plans/weave-integration.md` (line 48) at its original path under `~/Downloads/`; those plans are frozen and keep that path.
- **Status:** historical. Both pairings were refuted at the Chapter 6 gates (ISSUES #27 and #28; the default route map flipped 2026-06-27). The document records a design-phase hypothesis, not a result. Its pairings were never motivated by a measurement: the `MIGRATE_DECL` comparator slice postdates the W5 plan (see the ch.6 record), so the document must not be cited as evidence-driven.
