# GD2(iii) run log — D1 `ImportPruneUsage` on the 100 tune-controls (S-D2)

Committed list: `controls/tune_controls.csv`; scenarios materialized at
`data/scenarios_detector_tune/` (gitignored, regenerable); runner
`tools/detector_tune_run.py` (embedded positive smoke gate FLAGged on both
runs — no vacuous pass possible). Mergiraf `merge-tools/mergiraf:0.17.0`;
merge reproductions cached image-keyed in `raw_results.json`, detector
verdicts cached per driver commit.

## Run 1 — lane commit `9f871b1` — FAIL (1 flag)

- merges 100 | files 243 | CLEAN 238 / FLAG 1 / DIVERGED 4 | UNANALYZABLE 0
- FLAG `dynjs_dynjs__ee2219fc8b__..._ExecutionContext.java` L46 —
  `VariableValues` credited to a lost `import java.util.*;`.
  Diagnosis (scenario inspected — tune contents are sanctioned §3 design
  inputs): theirs narrowed `java.util.*` to four explicit imports; ours
  added five usages of `org.dynjs.runtime.VariableValues`, a SAME-PACKAGE
  type needing no import. Genuine detector FP: the wildcard-mining path
  credited a JDK wildcard with unknowable membership.

## Tuning fix — commit `423c215` (sanctioned: plan §5 GD2, in-session only)

Lost `java.*` TYPE wildcards now yield candidates only from embedded JDK
public-type sets (`_JDK_WILDCARD_TYPES`: java.util, java.io,
java.util.concurrent{,.atomic,.locks}, java.util.function, java.util.stream,
java.util.regex); a `java.*` package without a set yields no candidates
(FN-only). Non-JDK wildcards keep conservative mining (the jnr.ffi/log4j
spec shapes). +2 tests: the dynjs FP shape stays silent; a genuine
`java.util.*` narrowing (LinkedList) still flags. Driver suite 192/192.

## Run 2 — lane commit `423c215` — PASS

- merges 100 | files 243 | CLEAN 239 / DIVERGED 4 | FLAG 0 | UNANALYZABLE 0

## Post-review fixes — commit `bed3638` (Ali-requested critical review, post-close-out)

Review findings, all probe-verified before fixing (FN-direction except #2):
(1) `throws`/`implements`/`extends`/`permits` clause operands were treated
as declarations → pruned types used in multi-item clauses were missed;
clause keywords added to `_EXPR_KEYWORDS` (+P10/P11 e2e positives).
(2) enum-constant declarations matched no declaration regex → dedicated
depth-tracked constant-list parse feeds `declares_member` (+guard
negative). (3) conflict-marker abstention moved from raw to stripped text
(comment banners can no longer silence a file). Plus the merged==parent
soundness invariant test. Suite 197/197.

## Run 3 — lane commit `bed3638` — PASS (rerun after post-review fixes)

- merges 100 | files 243 | CLEAN 239 / DIVERGED 4 | FLAG 0 | UNANALYZABLE 0
- The widened detection surface (clause-position usages) produced no new
  tune flags. `summary.txt` in this directory is the run-3 report.

**GD2(iii) verdict: PASS (0 flags on the 100 tune-controls, reconfirmed
at `bed3638`).**
