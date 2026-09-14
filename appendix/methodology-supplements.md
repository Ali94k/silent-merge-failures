# Appendix (candidate): measurement-program supplements

Status: skeleton created by the ch.5 compression session (2026-09-09; ch.5 subsection pointers updated to their parent sections after the flatten ruling — the tables are otherwise verbatim from draft-r8) · Every item below is an **appendix-candidate**; final print-appendix curation is Ali's end-of-wave ruling · Appendix letter assigned at curation; tables keep their Chapter-5 identifiers (T5.1, T5.2, T5.3) so inbound references stay valid · Narrative: none

## A.1 Populations derived from the primary dataset (T5.1)

| Population | How drawn | Size | Used by |
|---|---|---|---|
| Fixed evaluation sample | deterministic first-N of the comparison framework's sorted scenario order (convenience draw) | 50 scenarios | six-tool table (Ch. 3); classifier blind-spot run (§5.3) |
| Routing corpora | tool-outcome selection, seeded, capped per repo | 60 + 60 + 240 scenarios | method-body arm gate (Ch. 6) |
| Synthetic battery | hand-built to favor Spork | 16 cases | adversarial check on the same gate (Ch. 6) |
| Declaration-migration pool | all materialized scenarios of that cluster, pooled | 38 scenarios | declaration-migration arm gate (Ch. 6) |
| Stage-C positives | all Mergiraf-clean, test-failing merges with ≤ 3 intersecting files (files edited by both sides); complete population, no sampling | 195 drawn → 164 scored | detection baseline (Ch. 8); whole-driver runs (Ch. 6) |
| Stage-C controls | test-passing merges; seeded; per-repo and file caps | 195 → 193 scored | same |
| Full-count population | every silent failure with a Java diff; two file-count strata (the Stage-C stratum plus larger merges) | 308 → 275 scored [FullCountScored] | full-population count (Ch. 7) |
| Derivation / held-out split | seeded, stratified 60/40 split of the full-count population, committed before any labeling; drawn over corpus rows, so fork twins of one merge fell on both sides (§8.2) | 165 / 110 units (107 held-out citable) | detector design vs. held-out recall (Ch. 8) |
| Fresh control draws | seeded walks over the untouched test-passing pool | 100 tune + 200 eval units | detector-cycle zero-FP gates (Ch. 8) |
| Pilot draws | seeded | 30 + 30 units | feasibility pilots — not citable |

*Table T5.1 — populations derived from the primary dataset. Selection vocabulary: "convenience draw" = a sample taken because it was easy to take, not drawn at random; "seeded" = drawn by a committed script with a fixed random seed, so the draw is reproducible (§5.4); "tool-outcome selection" = merges picked by how the tools fared on them, so deliberately hard cases; "materialized" = successfully rebuilt on disk as a complete scenario; "stratified" = divided so that each subgroup keeps its share in both splits; "fork twin" = the same merge commit under two repository names, so one merge occurs twice in the corpus.* [PopulationCounts]

## A.2 Instrument inventory (T5.2)

| Instrument | Question (how it is asked) | Population (T5.1) | Freeze | Env | Oracle / human ruling | Evidence |
|---|---|---|---|---|---|---|
| Six-tool comparison table | which backends qualify; comparator-gap vehicle — never a ranking (D-419) | fixed evaluation sample | oracle as of Tier E (§3.3); promoted 2026-07-03 | AWS (validated §5.5) | canonicalized dev-match (§3.3) | `reports/results.csv` |
| Method-body arm gate | does routing that cluster to Spork pay? | routing corpora + synthetic battery + fixed-sample re-run | runs 2026-05; no freeze SHA — disclosed | local | canonicalized dev-match, cross-tabulated against test labels | `reports_ci/`, ISSUES #27 |
| Declaration-migration arm gate | does routing that cluster to Weave pay? | declaration-migration pool | run 2026-06-01; no freeze SHA — disclosed | local | canonicalized and raw dev-match; test labels for cross-checks; exact paired test (§5.4) | `reports_migrate_decl/FINDINGS.md` |
| Whole-driver runs | assembled-driver cost, before and after the flip of the default route map (Ch. 6) | Stage-C positives + controls | pre-flip and post-flip driver commits | AWS | hybrid oracle¹; deltas-only | `reports_whole_driver/FINDINGS.md` |
| Detection baseline ("Stage C") | what the frozen layer catches, and falsely flags, on real merges | Stage-C positives + controls | frozen commit; two labeled post-fix runs | frozen run local (pre-dates cloud-first); post-fix runs AWS | dataset test labels; my flag rulings | `reports_detection/full/`, `postfix{,2}/` |
| External-benchmark run ("Phase 2b") | per-category recall and false positives against an independent oracle | external-benchmark units (§5.2) | detector commit; mapping frozen pre-run | AWS | the benchmark's behavioral labels; mapping ruled row-by-row | `reports_detection/phase2b/FINDINGS.md` |
| Full-population count | how the silent-failure mass distributes over mechanisms | full-count population | protocol + codebook commits | Batch API | double LLM closed coding under a frozen codebook; my gates | `reports_taxonomy/FINDINGS.md` |
| Detector cycle | zero-FP gates for the experimental lanes; held-out added recall | held-out split + fresh controls | plan + suite commits | AWS | two-arm runs (§8.1); my rulings over accepted draft rationales (§5.3) | `reports_detectors/FINDINGS.md` |
| Detector-cycle follow-up: baseline rerun (frozen name *S-D7*) | does the frozen detection baseline move when the new lanes are on? — a before/after comparison only, never fresh validation (D-433) | Stage-C positives + controls | suite commit | AWS | detection-baseline protocol | `reports_detectors/` §10 |
| Detector-cycle follow-up: whole-driver run pair (frozen name *S-D8*) | what enabling the lanes costs the assembled driver, in merge quality and in time | Stage-C positives + controls | suite commit + the derived gate (§5.4) | AWS | hybrid oracle¹; deltas-only | `reports_detectors/` §11 |
| Classifier blind-spot run | what file-level classification cannot see (§5.3) | fixed evaluation sample (unit: one type occurrence — Ch. 6) | RefactoringMiner 2.4.0 | AWS | project-level same-file evidence as reference | `reports_rm2_recall/FINDINGS.md` |
| Feasibility pilots | do the gates and costs permit the full runs? | pilot draws | pilot commits | local | plan gates; my miss rulings | `reports_detection/pilot{,_v2}/` — **not citable** |

*Table T5.2 — instrument inventory. ¹Hybrid oracle: the dataset's test label was measured on Mergiraf's merge output. A driver output that matches Mergiraf's output under the comparator's canonicalized equality inherits that label. Divergent outputs are scored by canonicalized dev-match.* [FreezeCommits]

## A.3 The human-annotation rounds (T5.3)

[Deviation flag: the ruled disposition sent T5.3 to the repo record only. It is held here as an appendix-candidate because ch.11 §11.5 cites it as the in-print statement of ruling workload; Ali's curation ruling decides. Dropping it to repo-only is a one-line change plus two retarget rows.]

| Group | What I rule | Ruled share | Why this share |
|---|---|---|---|
| Detection-baseline flags | every detector flag, on positives and controls | all 15 flags (on 357 scored units) | a flag is a claim about one specific merge; only a human can judge whether the flagged defect caused the failure |
| Detector-cycle held-out flags | every flag, over accepted draft rationales | all 20 flags | the same judgment, on data held out by unit id — these rulings decide the headline recall |
| Control flags that halt the session (the *stop rule*) | every one, immediately | all 4 raised since the rule was adopted (the baseline's four control flags predate it and sit in the first row) | a control flag threatens a zero-false-positive record; the session halts until I rule (§5.3) |
| Gate and freeze decisions | every approval, dated amendment, and scoping ruling | all of them (§5.4) | a frozen protocol may not change, pass, or fail without my dated ruling |
| Full-count labels | every pass-disagreement, plus a sampled audit of the agreements | 47 disagreements + a seeded, stratified 12-unit audit of the agreements, 12/12 accepted [CensusReliability]; 59 of 275 units examined one by one | two independent passes agreeing is itself a check; ruling effort goes where the passes conflict |
| External-benchmark mapping | every positive's category row | all 17 rows | the mapping decides per-category recall, so no row may rest on a machine draft |
| Pilot miss drafts — draft causes for the failures the pilot detectors did not flag | every draft label | all 23 | feasibility calibration only — ruled, but never cited |

*Table T5.3 — the human-annotation rounds, grouped. "Ruled share" counts labels I examined one by one.* [RulingRounds]

## A.4 Annotation review interface (screenshot placeholder)

Each annotation round ran through a self-contained offline review page: side-by-side line-aligned diffs, on-page tables answering "was this merge-induced?", persistent state, and export of the rulings (§5.3).

[IMAGE PLACEHOLDER: annotation-UI screenshot (`adjudication_ui.html`) — image lands in the LaTeX round]

## Claims used

- FullCountScored
- PopulationCounts
- FreezeCommits
- RulingRounds
- CensusReliability
