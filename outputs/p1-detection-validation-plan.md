# P1 — Detection-Layer Validation: Experiment Design

**Date:** 2026-06-10. Elaborates P1 of [`project-review-future-directions-2026-06-10.md`](project-review-future-directions-2026-06-10.md). All counts below verified against `data/schesch-dataset/results/reaper/result_adjusted.csv` (n=5,405) and current detector source.

**Sequence (decided 2026-06-10): pilot → improve → full eval.**

- **Stage A — diagnostic pilot** (~1–2 days): 30 positives + 30 controls through the current (v1) detectors, plus miss-classification of all pilot positives. Output: evidence-based detector-improvement shortlist + FA/crash reality check. Explicitly *not* the citable evaluation.
- **Stage B — evidence-guided detector improvement** (timeboxed, ~3–5 days): only items the Stage-A shortlist justifies (candidates: reset set beyond literal `.clear()`, type/flow-sensitivity, R3 cross-file, or a new category detector if misses concentrate there). Plus data-free engineering wins (shared CPG). This stage modifies `semantic_merge_driver/strategies/` + driver tests — the one exception to the no-driver-changes rule.
- **Stage C — full frozen evaluation** of v2 on the complete populations below (§2). v2 frozen at a commit before first Stage-C scoring; this run produces the thesis numbers. The pilot is disclosed as the diagnostic that informed v2 (no tuning against Stage-C results; any post-C fix → separately labeled re-run).

---

## 1. Question and claims under test

The thesis's surviving constructive claim: the driver catches **semantic conflicts in textually-clean merges** and moves them from the silent-incorrect bucket (cost ×10 in the Schesch model) to the visible-reject bucket (cost ×1). Four detectors carry it: `JoernDataFlowInterference` (#3, differential 3-way, "narrow PoC"), `JoernInfiniteLoop` + `JoernInvalidLoopBounds` (#5), `RM2RenameConflict` (#6, within-file stale callers).

Two numbers, currently unmeasured, decide whether that claim is evidence or aspiration:

- **R1 — false-alarm/block rate** on merges that are clean *and correct* (tests pass): what a developer pays per good merge. Includes fail-closed rejects from Joern/RM2 crashes — in deployment a parse failure **is** a block.
- **R2 — detection rate** on merges that are clean *and incorrect* (tests fail): how much of the real silent-failure mass the 3/7-category layer actually touches.

## 2. Populations (all from the Schesch table; ground truth already owned)

| population | definition | n available |
|---|---|---:|
| **Positives** | `mergiraf = Tests_failed` (clean merge, failing tests, all Java) | **308** |
| Positives, attribution-friendly | … with `num_intersecting_files ≤ 3` | 195 (121 at 2, 74 at 3) |
| **Controls** | `mergiraf = Tests_passed`, seeded random, repo-diversity-capped, intersect-matched | pool 3,144 |
| Optional extension | union `Tests_failed` over git/spork/mergiraf | 673 |

Mergiraf is the right backend to validate against: it is the driver's de-facto backbone post-#27/#28 (`NONE→git, else→Mergiraf`), and `gitmerge_ort`'s clean output on `NONE`-cluster merges differs little. Reproduce merges with `SEMANTIC_MERGE_BACKEND=mergiraf` explicitly; do not route through `auto` (Spork/Weave arms are DROP-decided but still wired — validating against them would measure dead arms).

## 3. Unit of analysis — per merge, any-file-flag

The driver runs per file (gitattributes); a merge is blocked if **any** file rejects. Score at merge level: hit = any intersecting Java file flags. This matches deployment semantics and sidesteps per-file attribution of the whole-merge `Tests_failed` label (the #28 lesson: 2/7 Mergiraf "FPs" were whole-merge-granularity artifacts). The `intersect ≤ 3` restriction keeps the candidate-culprit set small for adjudication.

## 4. Procedure

1. **Select** rows per §2 (seeded, capped ≤3/repo — reuse the `select_materialize.py` machinery; add a `CRITERION=semantic` mode: tool=`Tests_failed` / control mode tool=`Tests_passed`).
2. **Materialize** (base, ours, theirs, dev) per intersecting Java file → `data/scenarios_semantic/` (positives) + `data/scenarios_semantic_ctl/` (controls). Blobless clone + timeout, resumable — all existing plumbing.
3. **Reproduce the merged file** per scenario with the Mergiraf adapter. File-level CONFLICT → drop the file (a textual conflict is not a silent merge; driver would surface it anyway). Count drops; if a positive merge loses *all* its files this way, the row leaves the sample (report the count — it is itself a granularity finding).
4. **Run all four detectors** on each merged file, exactly as the driver invokes them: `taint_check.analyze(merged, base, ours, theirs)` (differential mode), loop strategies on merged only, R3 with `base_content`. **Detectors frozen at current commit** (see G2).
5. **Record per file:** per-detector verdict, issues, runtime, and `UNANALYZABLE` (joern-parse/RM2 failure → fail-closed). Aggregate per merge.
6. **Adjudicate every hit** (expected few), 3j-style written rationale per hit: (i) pattern actually present in merged output? (ii) merge-induced (absent in both parents)? (iii) plausibly linked to the test failure (code inspection; Schesch gives no per-test traces)? Label `CAUSAL` / `REAL-BUT-INCIDENTAL` / `DETECTOR-FP`.
7. **Classify a sample of misses** (~30–50 positives with no hit): which of the 7 taxonomy categories — or none — explains the failure. This yields in-the-wild category base rates (review §3.8) regardless of detector performance.

## 5. Pre-registered gates and metrics

- **G0 — Stage-A pilot (now also the improvement diagnostic).** 30 positives + 30 controls on v1. Calibrates runtime/merge and the Joern crash rate on real-world files (unknown; fixtures only so far); miss-classification of all pilot positives produces the Stage-B shortlist. Abort thresholds: >20 min/merge median or >30% UNANALYZABLE → fix harness/scope before scaling (e.g., shared-CPG optimization, §8).
- **G1 — harness sanity (positive control).** Inject the canonical clear→read fixture pattern into N=10 control merged-files → detector must fire 10/10. Distinguishes "detectors blind to real instances" from "harness broken". Run in Stage A and re-run at Stage-C start.
- **G2 — freeze applies to Stage C.** v2 detectors frozen at a named commit before the first Stage-C scoring run (the comparator-overfitting lesson, THREATS §internal). Pilot-informed improvement (Stage B) is legitimate and disclosed; tuning against Stage-C results is not. Any fix discovered mid-C → finish the frozen run, report, then a separately-labeled post-fix run. Optional extra rigor: hold out a random 50% of positives from Stage-A visibility so Stage C has an untouched split.
- **Metrics.** R1 = blocked controls / n (decomposed: detector FAs vs fail-closed crashes), R2 = hit positives / n (decomposed by adjudication label), per-detector breakdown, Wilson 95% CIs throughout. n=150 controls with 0 blocks → upper bound ≈ 2.4%; n=195 → ≈ 1.9%.
- **Pre-registered interpretation** (every cell is writable):

| R1 (controls) | R2 (positives) | thesis reading |
|---|---|---|
| low (≲5%) | >0 causal hits | detection layer adds measurable value at acceptable cost — strongest outcome |
| low | 0 hits | mechanism sound; covered categories are rare at corpus scale — honest scope statement, carried by the §4.7 base-rate table |
| high | any | layer not deployable as-is; attribute per detector to its documented limitation list (STATUS "Category #3 — honest scope") |

## 6. Optional third arm (cheap)

Run detectors over the **developer resolutions** of the same merges: an FP estimate on code that humans accepted and shipped. Reuses materialized scenarios; no extra cloning.

## 7. Phase-2b complement — labeled oracle

The Schesch TF rows say *something* broke, not *which category*. The `static-semantic-merge` (spgroup) benchmark referenced in STATUS/CLAUDE provides per-scenario labeled semantic conflicts — the only path to per-category FN rates. Concrete steps: locate the artifact, map its scenario format onto `MergeScenario`, run the four detectors per category. Keep it a separate follow-up cycle: §1–§6 needs no new external dependency and already converts "FP/FN unmeasured" into both headline numbers.

## 8. Cost model and engineering notes

Per file, driver-faithful: **5 CPG builds** (taint = merged+ours+theirs; each loop strategy rebuilds the merged CPG) + 5 Joern REPL queries + 1 RM2 Docker call ≈ 2–5 min on Apple Silicon. At ~2.4 intersecting files/merge × 300–390 merges ≈ **12–30 h compute** — overnight-able, resumable caching mandatory (cache key: scenario × detector × detector-commit).

If G0 says too slow: harness-mode optimization — one CPG per *file version*, all queries against it (cuts ~5× parse cost). That deviates from the driver's per-strategy invocation; document the deviation, and note the same change is a legitimate driver improvement (currently each loop strategy redundantly re-parses the same merged file).

Mismatch accounting: per-file re-merge may not bit-match Schesch's whole-merge run (tool version, virtual bases). Where the file-level outcome diverges from the row label expectation, count and report; don't silently keep.

## 9. Deliverables, tracking, effort

- `tools/detect_validate.py` (+ `CRITERION=semantic` in `select_materialize.py`) — implementation goes to Claude Code.
- `data/scenarios_semantic{,_ctl}/`, `reports_detection/` (`FINDINGS.md`, `summary.txt`, `scenarios.csv`, per-hit adjudications; pilot results under `reports_detection/pilot/`).
- Stage B: changes in `semantic_merge_driver/strategies/` + driver tests, scoped by the Stage-A shortlist (each improvement gets its own fixture tests, comparator-tier style).
- New ISSUES entry (#29) tracking all three stages; STATUS §category-3 + THREATS §3 updated with measured numbers after Stage C.
- Effort: Stage A ≈ 1–2 days (harness + pilot) → Stage B ≈ 3–5 days timeboxed → Stage C ≈ 1–2 days + overnight runs → **≈ 6–9 working days** across ~2 weeks calendar.

## 10. Risks

- **Low hit rate is the likely outcome** (narrow shapes, 3/7 coverage). Pre-registered as a reportable scope finding (§5 matrix) — not a failed experiment. The base-rate table (§4.7) guarantees the chapter has a result either way.
- **Flaky test labels** in Schesch TF rows → adjudication step absorbs this; spot-check any merge whose failure looks environmental.
- **Joern crash rate on real-world Java** unknown — measured by design (it is R1's fail-closed component, not noise).
- **Adjudication subjectivity** → written per-hit rationale, same protocol that made the 3j labelling defensible; optionally have the professor spot-check 5.
