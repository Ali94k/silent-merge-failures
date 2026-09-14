#!/usr/bin/env bash
# run_sd5.sh — ON-INSTANCE orchestrator for the S-D5 evaluation battery
# (ISSUES #31, GD3). Run detached:  nohup bash run_sd5.sh > sd5_run.log 2>&1 &
#
# Steps (STATUS file at ~/SD5_STATUS after every step; poll that, not pgrep —
# the CLI-DEPLOY overnight-idle lesson):
#   1. materialize the 200 eval-controls (Amendment-1 replacement rule)
#   2. smoke gate (every lane × flag-state fires)
#   3. known-answer env validation vs the committed tune_d3 cache (3 merges)
#   4. populations, shards in parallel: heldout, derivation, evalctl (6-way),
#      spgroup_ctl + spgroup_pos (2-way)
#   5. --score (aggregate + gate verdicts)
set -uo pipefail

MTC="$HOME/thesis-projects/merge-tool-comparison"
export PATH="$HOME/bin/joern/joern-cli:$PATH"     # non-interactive ssh skips .bashrc
# 4 parallel shards × Joern JVMs on a 16 GB instance: cap each JVM so the
# composition can't OOM (host JVMs inherit _JAVA_OPTIONS; docker JVMs don't).
export _JAVA_OPTIONS="-Xmx2500m"
STATUS="$HOME/SD5_STATUS"
LOGS="$MTC/reports_detectors/eval/logs"
mkdir -p "$LOGS"
PY="$MTC/.venv/bin/python"

export DRIVER_COMMIT="$($PY - <<'EOF'
import json, os
print(json.load(open(os.path.expanduser(
    "~/thesis-projects/merge-tool-comparison/reports_detectors/manifest.json")))
    ["detector_suite_commit"])
EOF
)"
echo "DRIVER_COMMIT=$DRIVER_COMMIT"

step() { echo "$1 $(date -u +%FT%TZ)" | tee "$STATUS"; }
fail() { echo "FAILED:$1 $(date -u +%FT%TZ)" | tee "$STATUS"; exit 1; }

cd "$MTC"

step "1_MATERIALIZE"
$PY tools/detector_eval_materialize.py > "$LOGS/materialize.log" 2>&1 \
  || fail materialize

step "2_SMOKE"
$PY tools/detector_eval_run.py --smoke > "$LOGS/smoke.log" 2>&1 || fail smoke

step "3_KNOWN_ANSWER"
$PY tools/detector_eval_run.py --known-answer 3 > "$LOGS/known_answer.log" 2>&1 \
  || fail known_answer

run_pop() {  # run_pop <population> <n_shards>
  local pop="$1" n="$2" pids=() rc=0
  step "4_RUN_${pop}"
  for ((k=0; k<n; k++)); do
    $PY tools/detector_eval_run.py --population "$pop" --shard "$k/$n" \
      > "$LOGS/${pop}_shard${k}_${n}.log" 2>&1 &
    pids+=($!)
  done
  for p in "${pids[@]}"; do wait "$p" || rc=1; done
  [ $rc -eq 0 ] || fail "run_${pop}"
}

run_pop heldout 4
run_pop derivation 4
run_pop evalctl 4
run_pop spgroup_ctl 2
run_pop spgroup_pos 2

step "5_SCORE"
$PY tools/detector_eval_run.py --score > "$LOGS/score.log" 2>&1 || fail score

step "DONE"
echo "battery complete; artifacts in reports_detectors/eval/"
