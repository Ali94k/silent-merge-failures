# S-D5 evaluation battery — run record (ISSUES #31, GD3)

Suite frozen at `732d8ff` (manifest `suite_freeze`, commit `21dcda1`) BEFORE
any evaluation. Harness `tools/detector_eval_run.py` + materializer
`tools/detector_eval_materialize.py` at `0e4b35b` (+ CSV-writer fix
`027ec4c`). One AWS cycle per `deploy/aws/CLI-DEPLOY.md` (fifth cycle —
record appended there).

## Local pre-flight (tune contents only — held-out never opened locally pre-run)

- smoke gate: 8/8 (lane × flag-state) FLAG, incl. the old-lane (flag0)
  UnresolvedReference positive (erudika shape, live Joern).
- known-answer: 42/42 file×lane verdicts match the committed
  `tune_d3/raw_results.json` over 3 tune merges.
- plumbing (scratchpad): 2-way shard + resume (no re-execution) + score +
  reports on 3 tune merges; both arms CLEAN, GD3-style verdict PASS.

## Cycle timeline (UTC)

| when | step |
|---|---|
| 07-16 21:58 | instance up: `i-0a3193cadee961264`, c7i.2xlarge, eu-central-1, 80 GB gp3; bundles `repo_sd5`/`scenarios_sd5` transferred cat\|ssh, sha256-verified |
| 07-16 22:05 | provision (Joern 4.0.436 pinned; mergiraf 0.17.0 + RM2 2.4.0 **built on-instance**, live-probed; venv) — run 1 launched |
| 07-16 22:23 | run 1 FAILED after full materialization: materializer CSV-writer fieldnames bug (spare rows carry `spare_order`); fix `027ec4c` shipped, relaunched with resume |
| 07-16 22:27–22:39 | eval-controls re-verified (200/832, 2 replacements); smoke PASS; known-answer PASS on-instance |
| 07-16 22:39 → 07-17 03:55 | heldout, 4 shards (291 files, both arms) |
| 07-17 03:55 → 14:20 | derivation, 4 shards (545 files) — straggler tail on shard 3 |
| 07-17 14:20 → 07-18 12:10 | evalctl (832 files): 4 shards; shards 2/3 drained, shards 0/1 projected 12–17 h alone (shard 0 held 338/832 files) → **half-shard surgery** at 07-18 04:34: killed 0/4+1/4, seeded 0/8+4/8+1/8+5/8 from their caches (identity: {i≡K mod 4} = {i≡K mod 8} ∪ {i≡K+4 mod 8}; keys are shard-independent), finished 12:10 |
| 07-18 12:10 → 13:50 | tail runner: spgroup_ctl (2 shards) + spgroup_pos (2 shards) + `--score` |
| 07-18 ~14:15 | artifacts pulled as one tarball (sha256 match), instance terminated, SG+key deleted, account verified empty (no instances, no volumes) |

Instance ≈ 40.3 h ≈ **$14.6 + EBS ≈ $3 ⇒ ~$17–18 total** vs the plan §10
~$5–10 estimate. Cause is structural, not idle: the FULL two-arm composition
is 8 lane-executions/file over 1,751 files and is Joern-bound (the P2
finding), CPU-saturated at 4 shards (load ~14 on 8 vCPUs). No overnight-idle
loss (STATUS-file monitor, 3-min polls).

## Materialization (Amendment 1 executed)

200/200 effective (120 ≤3 / 80 >3), 832 files, **2 replacement events**:
`urbanairship_datacube__61755d7739` (clone_fail — repo gone) → spare#1
`pablissimo_sonartsplugin__6a86fcb79d`; `ymnk_jsch-agent-proxy__be10f22b86`
(extract_fail) → spare#25 `valotrading_silvertip__9d31f81110`. Effective
list + sha256 in `eval_controls_effective.csv` / `materialize_log.json`.

## Results (machine numbers; GD3 gate verdicts PENDING Ali — see gd3_flag_package.md)

- Held-out (PRIMARY, 110/110 scored): baseline 5/110 = 4.5% [2.0, 10.2],
  experimental **20/110 = 18.2% [12.1, 26.4]**, added **15/110 = 13.6%
  [8.4, 21.3]**; pooled name-binding family baseline 2/37 = 5.4% →
  experimental **16/37 = 43.2% [28.7, 59.1]**, family added **14/37 = 37.8%
  [24.1, 53.9]**. Per-lane (file rows, exp arm): ImportPruneUsage 16,
  UnresolvedRef[Joern] 6, RM2Rename 4, UnresolvedRef[D3-widened] 1,
  SignatureStaleCall 0. Nestedness violations 0; classifier drift 0;
  baseline-arm UNANALYZABLE-only units 1 (fail-closed, reported, not a catch).
- Derivation (TUNING-TAINTED, descriptive): baseline 11/165 → experimental
  39/165; family 5/48 → 30/48.
- GD3(ii) eval-controls: baseline **0**/197 scored (3 all-diverged);
  experimental **1**/197 — `jgralab_jgralab__d1a767cb2d` (D1).
- GD3(iii) spgroup-clean: experimental **1**/66 — `jOOQ__d96120f327__org.jooq.impl.DSL`
  (D1). spgroup-positive (descriptive): 0/17.
- Both flags packaged with execution-verified evidence in
  `gd3_flag_package.md`; session STOPPED per plan §5 pending Ali's rulings.

## Incidents and lessons

1. **Materializer CSV bug** (run 1): fieldnames from a primary row crashed on
   the first spare row — only surfaced because a replacement actually fired;
   local plumbing never exercised one. Fix `027ec4c`; materialization itself
   was already complete and resumed cleanly.
2. **Static shard imbalance**: sharding by merge index balances counts, not
   work (shard 0 drew 41% of evalctl's files). Half-shard surgery (seeded
   re-partition) recovered ~10 h. If S-D7/S-D8 run: use a work-queue or
   shard by cumulative file bytes.
3. **Local `--score` overwrote instance artifacts** with an
   evalctl-less view (its scenario dir wasn't local), silently dropping the
   GD3(ii) section; restored from the pulled tarball. Guard added post-run
   (clearly post-hoc, does not affect the recorded results): `--score` now
   refuses to score evalctl against an incomplete scenario dir.
4. zsh does not word-split `$VAR` (transfer loop no-op) but does split
   `$(...)`; per-file cat|ssh of ~50 MB times out — tar once, verify one
   checksum.
5. `pgrep -f` self-match (the CLI-DEPLOY lesson) avoided throughout with
   bracket-pattern tricks.
