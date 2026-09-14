# Thesis spine

Title (ruled 2026-08-17): **Textually Clean, Semantically Wrong: An Anatomy and Detection of Silent Merge Failures**

**Thesis statement.** Silent semantic merge failures in real Java histories are dominated by mundane name-binding staleness rather than the behavioral interference the literature emphasizes. A fail-closed static verification layer can block a causally-confirmed share of them at zero measured false-block cost. The intuitive alternative is specialist per-case tool routing, but it was refuted at pre-registered gates.

## Research questions

- **RQ1 (Ch. 3)** How should merge-tool output be judged against developer resolutions, and how much do naive textual oracles distort tool assessment?
  - RQ1.1 how much was artifact; RQ1.2 does the repaired oracle agree with the tests; RQ1.3 which backends qualify
- **RQ2 (Ch. 6)** Does classifier-based per-case dispatch to specialist merge tools improve merge outcomes over a single structured backbone, end-to-end?
  - RQ2.1 cluster predictability; RQ2.2 specialist against backbone; RQ2.3 measured-best routing configuration
- **RQ3 (Ch. 7)** What mechanisms cause textually clean merges to fail semantically in real Java histories, and how is that mass distributed?
  - RQ3.1 attributable fraction; RQ3.2 dominant mechanisms; RQ3.3 benchmark representativeness
- **RQ4 (Ch. 8)** To what extent can a static, fail-closed verification layer surface silent semantic failures, at what false-positive cost?
  - RQ4.1 causal catch rate; RQ4.2 false-block cost across corpora; RQ4.3 payoff of retargeting at the RQ3 mass

## Chapter budget (~60 pp)

| Ch. | File | Title | pp |
|---|---|---|---|
| 1 | 01-introduction.md | Introduction | 5 |
| 2 | 02-background-related-work.md | Background & related work | 6 |
| 3 | 03-measuring-merge-tools-fairly.md | Measuring merge tools fairly | 7 |
| 4 | 04-semantics-aware-merge-driver.md | A semantics-aware merge driver | 6 |
| 5 | 05-methodology-infrastructure.md | Experimental methodology & infrastructure | 4 |
| 6 | 06-does-specialist-routing-pay.md | Does specialist routing pay? | 6 |
| 7 | 07-anatomy-of-silent-merge-failures.md | The anatomy of silent merge failures | 8 |
| 8 | 08-detecting-silent-failures.md | Detecting silent failures | 7 |
| 9 | 09-ai-and-author-contributions.md | AI and author contributions | 3 |
| 10 | 10-discussion.md | Discussion | 2 |
| 11 | 11-threats-to-validity.md | Threats to validity | 4 |
| 12 | 12-conclusion-future-work.md | Conclusion & future work | 2 |

Page counts are nominal. Over-budget chapters were accepted as drafted (rulings 2026-08-02 to 2026-08-29).

Appendices (uncounted): full tables, normalization-tier catalogue, human-annotation protocol + review-interface screenshot, fixture batteries, AWS reproduction guide, per-cycle cloud log (D-316).

## RQ → answer map (defense cheat-sheet; sources in claims-ledger.md)

| RQ | One-line answer |
|---|---|
| RQ1 | Naive oracles inflate AST-reforming tools' FPs (Spork 42 → 11 after canonicalization); canonicalization discriminates artifact from defect, and in the one cluster where the oracles can be compared the test labels clear its residual mismatches; Mergiraf qualifies, JDime doesn't |
| RQ2 | No — both specialist arms refuted at their gates (Spork on precision, 0.49 vs 0.78; Weave 0 wins of 38); the pre-flip router broke 21/239 good control files end-to-end on real merges; the trivial NONE→git fast-path over Mergiraf is the measured-best routing configuration (1779 vs 1994) |
| RQ3 | 43.3% attributable; name-binding = 71.4% of attributed mass; the taxonomy's behavioral categories have no standalone counterpart in this population; the external benchmark concentrates its interference in two categories with no standalone counterpart in these histories; 56.7% escape stratum |
| RQ4 | Baseline: flagged 6.7% [3.8, 11.6] of the real silent failures; 9 of the 11 flags ruled causal, a causal catch of 5.5% [2.9, 10.1]; the repaired suite keeps those 9 catches at 0/193 false blocks on the primary corpus and flags 0/66 labeled-clean units on the external benchmark; retargeted suite: family recall 5.7%→40.0% (14 of 35 held-out family units), blocked share on the detection baseline 6.7%→22.0%, whole-driver cost −11.5%, 0 ruled FPs |

## Writing conventions

- Narrative device (try–fail cycles): narrative voice in Ch. 10 only (PR #45 deleted the bridges and the mini-abstracts of Chs. 2–12, PR #53 the Ch. 1 arc, and end-game step 4 the Ch. 1 mini-abstract); structure (hypothesis → gate → verdict) everywhere; results sections and headings stay flat. Vocabulary: *hypothesis / gate / refuted / retained* — never "failure". First-person agency (R12): the author's own actions are first person wherever they appear — body prose, table cells, figure boxes ("I rule", never "the author" as an actor).
- Every number comes from a claims-ledger macro; no inline numbers.
- One claim, one home: stated fully once, referenced elsewhere.
- No chapter carries a mini-abstract. PR #45 deleted those of Chs. 2–12, and end-game step 4 (Ali, 2026-09-14) deleted Ch. 1's, which duplicated the front-matter abstract (`thesis/latex/templates/frontmatter/abstract.tex`).
- Register: the calm register R13 for all prose (adopted 2026-08-11; reference example ch. 6 §6.5 as merged in PR #11); the light direct register for ch. 10 from r7, ch. 11 and ch. 12 (ruled 2026-09-02). Rules R1–R13 and the marker conventions live in WORKFLOW.md.
