# GD2(iii) run log — D2 `SignatureStaleCall` on the 100 tune-controls (S-D3)

Committed list: `controls/tune_controls.csv`; scenarios materialized at
`data/scenarios_detector_tune/` (gitignored, regenerable); runner
`tools/detector_tune_run.py` (per-lane embedded positive smoke gate — S-D3
extension; the D2 smoke exercises the real RM2 image, so a vacuous pass is
impossible). Mergiraf `merge-tools/mergiraf:0.17.0`; RM2
`merge-tools/refactoring-miner:2.4.0`. Merge reproductions were seeded from
`tune_d1/raw_results.json` (`::__merge__::` entries are keyed by scenario +
mergiraf image, lane-independent — same sanctioned §3 tune materializations,
no re-merge); detector verdicts cached per driver commit.

## Run 1 — pre-commit working tree (cache key `bed3638`) — PASS

- merges 100 | files 243 | CLEAN 239 / DIVERGED 4 | FLAG 0 | UNANALYZABLE 0
- smoke positive: FLAG ok (real-RM2 P1 shape)
- Zero flags on first contact — no tuning iteration used. Run executed
  before the lane's commit (working tree state); the definitive gate run is
  re-executed at the lane commit below.

## Amendment-3 triple review (between runs; fixes in the lane commit)

Review passes (a) project-code (/code-review high, 8 finder angles +
verification), (b) standalone JLS semantics, (c) open-source practice
comparison. Confirmed findings fixed before the definitive run — notably
two FP-critical: the PascalCase comparison-pair generic misclassification
(now: a `(`-followed generic span is trusted only when `new`-rooted) and
the literal-only-argument arity miscount (`send("boom")` read as arity 0 —
now counted via `_strip_for_arity`, a literal-placeholder projection).
Full record in ISSUES #31 S-D3 close-out. Suite 292/292 at the lane commit.

## Run 2 — lane commit `6523ab0` — PASS (definitive)

- merges 100 | files 243 | CLEAN 239 / DIVERGED 4 | FLAG 0 | UNANALYZABLE 0
- smoke positive: FLAG ok | driver_commit=6523ab0
- `summary.txt` in this directory is the run-2 report.

**GD2(iii) verdict: PASS (0 flags on the 100 tune-controls at the
committed lane, zero tuning iterations used).**
