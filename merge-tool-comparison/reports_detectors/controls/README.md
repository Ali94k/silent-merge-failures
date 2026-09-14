# Detector-Cycle Control Draws (ISSUES #31, S-D1)

Authority: `outputs/detector-cycle-plan.md` §4 + §12 Amendment 1
(2026-07-16). Drawn by the committed script
`tools/detector_controls_draw.py` — seeded, scripted, never hand-picked.
SHA-256 hashes of every list live in `../manifest.json` and
`draw_log.json`.

## Pool (one pool, both draws — Amendment 1 ruling 2)

`data/schesch-dataset/results/reaper/result_adjusted.csv` rows with a Java
diff and `mergiraf == Tests_passed` (the `semantic_ctl` criterion), with a
parseable `num_intersecting_files` (0 rows excluded as unparseable), minus
the 195 Stage-C control merges (`stagec_exclusion_195.csv`): **2,949 fresh
merges** (≤3 files: 2,365; >3: 584).

## Draw constraints (plan §4, ratified §11.1)

- ≤3 merges per repo (per list).
- Stratified to the census file-count mix: 60% `num_intersecting_files ≤ 3`
  / 40% `> 3` (mirrors the taxonomy A/B 164/111 split).
- Seeded walks: `SEED_TUNE=20260715`, `SEED_EVAL=20260716`.

## Files

| file | contents |
|---|---|
| `tune_controls.csv` | **n=100** (60 ≤3 + 40 >3), Stage-C-style draw-with-materialization: each listed merge is fully materialized in `data/scenarios_detector_tune/` (gitignored, regenerable). This IS the GD2(iii) tune set. |
| `eval_controls.csv` | **n=200** (120 ≤3 + 80 >3) primaries, viability-checked only (blobless clone + by-SHA parent fetch + exactly-one merge-base — **no content extraction**, plan §3 firewall). Materialized only in S-D5. |
| `eval_controls_spares.csv` | **n=40** ordered spares (24 ≤3 + 16 >3), same viability check, same walk. |
| `stagec_exclusion_195.csv` | the 195 Stage-C control merges both draws exclude. |
| `draw_log.json` | pool stats, per-walk skip counters, seeds, quotas, list hashes. |

Disjointness: eval draw excludes Stage-C 195 **and** the tune 100; tune
draw excludes Stage-C 195. All three control sets are mutually disjoint.

## S-D5 replacement rule (Amendment 1 ruling 1 — deterministic, no choice)

When an `eval_controls.csv` primary fails materialization in S-D5 (clone
timeout/fail, multi-merge-base, missing file content), it is replaced by
the **next unused spare in `eval_controls_spares.csv` order of the same
stratum** that keeps per-repo ≤3 among effective members. Every
replacement event is recorded in the cycle manifest. GD3(ii)'s "the 200
eval-controls" = the effective materialized list under this rule.

## Firewall note (plan §3)

Tune-control contents are allowed design/tuning inputs (GD2(iii) tuning is
sanctioned there and only there). Eval-control contents are **never seen
during development** — this session verified viability without reading any
file content; materialization happens in S-D5 after the detector-suite
freeze.
