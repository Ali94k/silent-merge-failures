# Phase-2b — Per-category recall against the spgroup labeled benchmark

**Date:** 2026-07-05 (run 2026-07-04/05, AWS c7i.2xlarge, native x86_64).
**Detectors:** all five, at driver commit `f964354` (`DRIVER_COMMIT` pinned; git-archive deployment).
**A NEW labeled evaluation — separate from and never blended with the frozen Stage-C numbers**
(`reports_detection/full/FINDINGS.md`). Design pre-registered in
`research/outputs/phase2b-recon.md`; category mapping frozen BEFORE the run in
`category_mapping_draft.md` (+ machine-readable `category_mapping.csv`).
**G1 inject-sanity: 10/10 PASS in BOTH arms** (developer-merge splice and Mergiraf-reproduced
splice) minutes before scoring — the pipeline provably fires on the canonical #3 shape on this
machine; the zeros below are detector-scope findings, not harness failures.

## Benchmark and populations

`spgroup/mergedataset` @ `04a18017` (UFPE / Borba group; GPL-3.0; the ground-truth family behind
their SMAT/OA/ICSE'24/pointer-analysis papers). Unit = (merge commit, class); label =
`Locally Observable Interference` (manual, behavioral). Source `{base,left,right,merge}.java`
quadruples ship in-dataset; `merge.java` is the developer's merge commit content.

| | labeled Yes (positives) | labeled No (controls) |
|---|---|---|
| CSV rows → unique file units | 17 | 69 |
| materializable (all 4 files) | **17** | 66 (3 quadruples absent upstream) |
| scored, developer arm | **17** | **66** |
| scored, Mergiraf re-merge arm | 15 (2 CONFLICT → surfaced, leave sample) | 56 (10 CONFLICT) |

4 rows labeled "-" (never manually analyzed) excluded up front.

## Headline numbers

**Primary arm — detectors on the developer's shipped merge (oracle-faithful):**

- **Recall on labeled interference: 0/17 = 0.0% [0.0%, 18.4%]** (0 FLAG, 0 fail-closed).
- **FP/block rate on labeled interference-free units: 0/66 = 0.0% [0.0%, 5.5%]**.
- Analyzability: **0/83 UNANALYZABLE**; Joern 0 failures; median 80 s/merge (G0 margin 15×).

**Per-category recall (positives; mapping RULED by Ali 2026-07-27 — all 17 rulings confirm the
draft, 0 overrides, incl. the VERIFY-flagged storm→#6 row. Table is citable as final. Rulings:
`category_mapping_adjudicated.csv`):**

| category | n | recall | Wilson 95% |
|---|---|---|---|
| 1 atomic updates | 6 | 0/6 | [0, 39.0%] |
| 2 control-flow interference | 6 | 0/6 | [0, 39.0%] |
| **3 data-flow / stale read** | **1** | **0/1** | [0, 79.3%] |
| 6 rename family | 1 | 0/1 | [0, 79.3%] |
| none-of-7 | 3 | 0/3 | [0, 56.2%] |
| 4, 5, 7 | 0 | — | no instances in the benchmark |

**Secondary arm — Mergiraf re-merge (deployment view):** scored zeros match (0/15 pos, 0/56 ctl);
the informative delta is divergence: **2/17 positives textually CONFLICT under the driver's
default backend** — storm/KafkaSpoutConfig (the only #6-family positive) and
swagger-maven-plugin/AbstractReader (#1) — i.e. under the deployed driver these two are
*surfaced to the user, not silent*. The silent-failure exposure the recall claim concerns is
the remaining 15.

## Findings

1. **The zero-FP record extends to a second, independently constructed labeled corpus.**
   0/66 here + 0/193 Stage-C post-fix controls = 0 false blocks across two corpora. Context on
   the same dataset: spgroup's purpose-built OA static analysis reports recall 0.28 at
   precision 0.47 (≈9 FPs; arXiv 2507.20081). The layer's differentiator is confirmed to be
   its FP cost, not its coverage.
2. **The predicted #3 false negative is confirmed — the shape limit is now a measured miss.**
   The benchmark's single stale-read-family positive (elasticsearch-river-mongodb `Slurper`:
   one parent *reassigns* `oplogDb`, the other adds a read) was drafted pre-run as "outside the
   literal-`.clear()` scope → expected FN" and was indeed missed. STATUS limit (3) graduates
   from caveat to measurement.
3. **The category base-rate finding is corroborated from a second direction.** Stage C: #3/#5
   fired 0 times in 443 real files. Phase-2b: a benchmark *curated for semantic conflicts*
   puts 12/17 of its interference in uncovered categories #1/#2 (state-overlap / control-flow
   shapes needing behavioral or SDG-class analyses) and contains zero #4/#5/#7 instances.
   The taxonomy's covered categories are rare in real interference regardless of corpus.
4. **Pre-registered interpretation cell (plan §5): "low R1 + 0 hits — mechanism sound; covered
   categories rare at corpus scale."** G1 10/10 both arms rules out the harness; recall is
   bounded, not merely unknown: ≤18.4% overall, ≤79.3% for #3 (n=1 — the honest admission that
   this benchmark cannot tightly bound per-category recall for the covered categories).

## Threats specific to this run

- **Mapping was Claude-drafted, frozen pre-run, and ruled post-hoc** (Ali, 2026-07-27:
  17/17 confirm the draft, 0 overrides — `category_mapping_adjudicated.csv`). Row 14
  (storm → #6) was marked VERIFY and confirmed; note that unit left the deployment arm via
  textual conflict anyway. Residual threat: rulings were recorded after the detector outcomes
  were known (the pre-run freeze + zero overrides mitigate this). Deviation from the D-237
  plan: the rulings carry no per-row written rationales — each confirmation adopts the frozen
  draft's own per-row reasoning as its rationale.
- **Definitional gap:** their label is behaviorally observable interference; our detectors are
  structural per-file shapes. A structural detector can be correct-by-scope and still score 0
  here; the claim this run supports is about *shape coverage of real interference*, not
  detector defects.
- **Small n:** 17 positives; per-category cells n ≤ 6. CIs carried everywhere.
- **Selection bias of the benchmark:** units were mined where both parents changed the *same
  method* — enriching OA/both-write shapes (#1) relative to, e.g., rename interference (#6),
  which arises from cross-method edits by construction.

## Artifacts

`dev/` and `remerge/` — `summary.txt`, `scenarios.csv`, `raw_results.json` (resumable caches,
committed as with prior runs), `sanity.json`, logs, `misses_to_classify.csv`.
`category_mapping_adjudicated.csv` — Ali's per-unit rulings (2026-07-27, via `mapping_ui.html`).
Scenario JSONs regenerable: `tools/materialize_phase2b.py` over the pinned dataset clone
(+ `--category-map reports_detection/phase2b/category_mapping.csv`).
Cycle record (instance, cost, teardown-verified): `deploy/aws/CLI-DEPLOY.md` fourth cycle.
