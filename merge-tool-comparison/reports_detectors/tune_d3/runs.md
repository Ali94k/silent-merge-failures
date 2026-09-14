# GD2(iii) tune-control runs — S-D4 D3 widening (ISSUES #31)

Gate: 0 flags on the 100 tune-controls, FULL suite (the S-D5
experimental-arm composition: JoernDataFlowInterference,
JoernUnresolvedReference, JoernInfiniteLoop, JoernInvalidLoopBounds,
RM2RenameConflict + experimental ImportPruneUsage, SignatureStaleCall),
`SEMANTIC_MERGE_EXPERIMENTAL_DETECTORS=1`. First time the full composition
runs together on controls ("interactions count" — S-D4 kickoff prompt);
prior sessions' tune runs covered single lanes (tune_d1 = D1, tune_d2 = D2).

## Run 1 — preliminary (pre-review lane state), ABORTED/SUPERSEDED

- Working-tree lane code before the Amendment-3 review fixes; cache keys
  under the explicit override `DRIVER_COMMIT=wip-s-d4-prelim` (chosen
  precisely because the tree was uncommitted).
- Merge reproductions seeded from `tune_d2/raw_results.json`
  (lane-independent `::__merge__::` keys, 243/243 hits).
- Progress at stop: ~29/243 files × 7 lanes scored, **0 non-CLEAN rows**.
- Stopped when the review landed 8 FP-vector fixes (3 lanes' code changed:
  unresolved_reference, import_prune_usage via the shared
  `_qualified_or_case`, signature_stale_call transitively through the same
  helper) — pre-fix verdicts for those lanes are not gate evidence.
- Harvest: the 117 scored rows of the four lanes whose code is
  byte-identical at the gate commit (JoernDataFlowInterference,
  JoernInfiniteLoop, JoernInvalidLoopBounds, RM2RenameConflict — none
  touched by `732d8ff`) were re-keyed to the definitive scheme and seeded
  into run 2 (`tune_d3/seed_from_prelim.json`), together with all 243 merge
  reproductions. Recorded here because GD2 evidence must say where every
  verdict came from: those rows were computed on identical lane code over
  identical inputs by the same harness, one process earlier.

## Run 2 — definitive, at lane commit `732d8ff` (cache keys `732d8ff::exp1`)

- Executed as 4 parallel shards over a round-robin split of the 243
  scenario files (`data/scenarios_detector_tune_shard{0..3}`, symlinks;
  61/61/61/60 files) — wall-clock relief for the ~10-Joern-invocations-per-
  file cost of the full composition on this Mac (the plan's documented
  local-tuning exception; the ~6.5 h serial estimate exceeded the plan's
  1–2 h guess). Every shard ran the per-lane vacuous-run smoke guard
  (7 lanes × 4 shards, all FLAG) before scoring.
- Shard caches merged into `tune_d3/raw_results.json`; the recorded verdict
  comes from a final single-process FULL run over the complete
  `data/scenarios_detector_tune/` with that cache (100% hits — a pure
  re-scoring pass that regenerates the unified summary at the same commit
  and key scheme).
- Result: see `summary.txt` (this file is written before the shards
  finish; the summary and the verdict line below are appended after).

## Verdict

**Run 2 (definitive, `732d8ff`, cache keys `732d8ff::exp1`): GD2(iii) PASS.**

- 100 merges / 243 files / 1701 file×lane rows: **1673 CLEAN / 28 DIVERGED**
  (the same 4 mergiraf-CONFLICT files as tune_d1/tune_d2 × 7 lanes —
  textual conflicts are surfaced, not silent, and are excluded by design).
- **0 flags, 0 UNANALYZABLE.** Every lane clean on every analyzable file:
  the first run of the complete 7-lane S-D5 experimental-arm composition
  (interactions included — D1/D2 rerun on these controls at the post-review
  shared-helper state, and the four default lanes got their first-ever
  tune-control pass).
- Zero tuning iterations after the Amendment-3 review fixes: the review's 8
  execution-verified FP-vector fixes (review_record.md) landed BEFORE the
  definitive run; run 1 (pre-review, superseded) had also shown 0 flags on
  the ~29 files it covered.
- Shard PASS summaries: 61+61+61+60 files, each shard 0 flags /
  0 UNANALYZABLE; unified re-scoring pass regenerated this directory's
  summary.txt from the merged cache (100% hits at the same commit + key
  scheme). Shard caches were byte-subsumed by the merged
  raw_results.json and deleted; the aborted run-1 cache is kept at
  tune_d3_prelim/ as harvest provenance.
- Smoke positive-controls: all 7 lanes FLAGged their embedded micro-fixtures
  in every shard and in the unified pass (vacuous-run guard).
