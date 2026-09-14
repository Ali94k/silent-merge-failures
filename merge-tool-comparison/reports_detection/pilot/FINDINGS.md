# Stage-A Pilot Findings — Detection-Layer Validation (G0 diagnostic)

**Date:** 2026-06-11. **Detectors:** v1, frozen at driver commit `2eed882`. **Spec:** [`outputs/p1-detection-validation-plan.md`](../../../outputs/p1-detection-validation-plan.md) §4–§5; harness `tools/detect_validate.py`. **This is the diagnostic pilot, not the citable evaluation (that is Stage C).**

## Sample

30 positive merges (`mergiraf == Tests_failed`, `num_intersecting_files ≤ 3`, seed 42, ≤3/repo) → 36 file scenarios; 30 control merges (`Tests_passed`, same knobs) → 35 file scenarios. Merged files reproduced with the comparator's Mergiraf adapter (`merge-tools/mergiraf:0.17.0`, the driver's backbone post-#27/#28).

## Gates

| gate | threshold | observed | result |
|---|---|---|---|
| G1 inject-sanity | 10/10 fire | **10/10 fired** (differential DFI on spliced clear→read in real control files) | **PASS** |
| G0 runtime | median ≤ 20 min/merge | **median 34 s/merge** (DFI ≈ 19 s/file — 3 CPG builds; loops ≈ 6 s; RM2 ≈ 2 s) | **PASS** (~35× headroom) |
| G0 analyzability | ≤ 30% UNANALYZABLE | **0/64 files (0%)** — zero Joern/RM2 failures on real-world Java, incl. a 7,400-line `Compiler.java` | **PASS** |

Runtime implication for Stage C: 195 positives + matched controls extrapolate to **≈ 3–4 h total**, not the 12–30 h the plan budgeted. The shared-CPG optimization (§8) is *unnecessary for feasibility* (still a legitimate driver improvement).

## Headline numbers (pilot-grade, n small, CIs wide — do not cite as Stage C)

| metric | value | Wilson 95% |
|---|---|---|
| **R1** — controls blocked | **1/30 = 3.3%** (1 detector FLAG, 0 fail-closed) | [0.6%, 16.7%] |
| **R2** — positives blocked | **2/25 = 8.0%** (2 detector FLAG, 0 fail-closed) | [2.2%, 25.0%] |

Per-detector (64 clean-merged files): `JoernInfiniteLoop` 4 FLAGs; `JoernDataFlowInterference`, `JoernInvalidLoopBounds`, `RM2RenameConflict` **0 FLAGs, 0 UNANALYZABLE** each.

## Hit evidence (provisional — final 3j-style labels are Ali's adjudication)

All 4 FLAGged files (5 sites) come from `JoernInfiniteLoop`, and **every flagged line is present verbatim in base, ours, AND theirs** — none is merge-induced:

| file | line | code | in base/ours/theirs |
|---|---|---|---|
| [pos] `clojure…Compiler.java` | 6599 | `while(true){` — deliberate idiom, comment says "return breaks" | ✓/✓/✓ |
| [pos] `clojure…Compiler.java` | 7397 | `if(true)//!LOADER.isBound())` — an **`if`, not a loop** | ✓/✓/✓ |
| [pos] `urbanairship…DataCubeIo.java` | 217 | `while(true) {` with internal control flow | ✓/✓/✓ |
| [pos] `urbanairship…HBaseDbHarness.java` | 355 | `while(true) {` wait-loop | ✓/✓/✓ |
| [ctl] `farin…Engine.java` | 207 | `while (true) {` REPL read loop | ✓/✓/✓ |

Provisional label for all five: **DETECTOR-FP** (pre-existing deliberate idiom; not merge-induced; not plausibly linked to the positives' test failures). Under that labeling the pilot's *causal* hit count is **0** — the §5 interpretation matrix row "R1 low / 0 causal hits": mechanism sound (G1 proves the pipeline detects real instances), covered categories rare at corpus scale, honest-scope outcome. The miss-classification of the 23 unblocked positives (`misses_to_classify.csv`, **manual**, plan §4.7) decides whether Stage B should add coverage where misses concentrate.

## Granularity finding (plan §8 mismatch accounting)

7/36 positive files (19%) came back **CONFLICT** from the file-level Mergiraf re-merge despite the whole-merge `Tests_failed` (i.e. clean) row label; **5/30 positive merges (17%) lost all their files** this way and leave the sample (scored n=25). Controls: 0/35 files diverged. Likely cause: file-level re-merge vs whole-merge run (tool version, virtual bases). Carry this number into Stage C reporting; it is itself evidence that whole-merge labels are a noisy per-file oracle (the #28 lesson again).

## Stage-B shortlist (evidence-based, in priority order)

1. **Make `JoernInfiniteLoop` differential (merge-induced only)** — the DFI pattern: flag only loops absent from both parents. Would have produced **0 FPs in this pilot** (all 5 sites pre-existing). Highest measured-impact change.
2. **Restrict its query to loop control structures** — `controlStructureType("WHILE","DO","FOR")`; today `condition.isLiteral.code("1|true")` matches any control structure: the `if(true)` hit at `Compiler.java:7397` is a category error, not an infinite loop.
3. **Break/return awareness** — every flagged `while(true)` has an obvious internal exit; without exit-path analysis the detector flags a ubiquitous deliberate idiom (4 distinct repos in a 60-merge sample).
4. **No evidence for harness fixes** — 0 UNANALYZABLE, G1 10/10: shared-CPG (§8) is optional perf work, not a correctness need.
5. **Coverage gaps**: DFI/loop-bounds/RM2 produced zero hits on 25 real silent-failure merges — whether to widen them (reset-set beyond `.clear()`, cross-file R3) or add a new category detector should wait for the manual miss-classification (§4.7), per the plan.

## Miss classification (ADJUDICATED 2026-06-11)

**Ali reviewed all 23 misses via `review_ui.html` (side-by-side dev-vs-Mergiraf, intraline highlights) and accepted every draft label — 23/23.** Adjudicated labels are in [`misses_to_classify.csv`](misses_to_classify.csv); rationale + evidence in [`misses_classification_draft.md`](misses_classification_draft.md) and `misses_evidence.md`. **Final base rates (n=23): #6-family rename/declaration-change interference 8 (35%; 62% of the 13 attributable — 5 confirmed compile errors), none-of-7 breakage 5 (22%), none-identified (scored files ≡ dev) 9 (39%), indeterminate 1 (4%); categories #1, #2, #3, #4, #5, #7: zero.** Consequence for Stage B: the priority is R3 widening — RM2 rename types beyond Method/Class (Variable/Attribute/signature changes), per-branch RM2 (base→ours, base→theirs — the existing `rm2_tag` machinery) + a merged-consistency scan for the inverse shape, and a cheap single-file unresolved-identifier check — ahead of the InfiniteLoop FP fixes above (which remain justified for R1).

## Artifacts

`summary.txt` (R1/R2 + CIs + per-detector + G0), `scenarios.csv` (71 per-file rows), `misses_to_classify.csv` (23 unblocked positives, label columns empty by design), `raw_results.json` (resumable cache: every Mergiraf merge + detector verdict, keyed on driver commit), `sanity.json` (G1 details).
