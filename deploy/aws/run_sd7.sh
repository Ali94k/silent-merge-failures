#!/usr/bin/env bash
# run_sd7.sh — ON-INSTANCE orchestrator for the S-D7 Stage-C rerun battery
# (ISSUES #31 follow-on). Run detached:  nohup bash run_sd7.sh > sd7_run.log 2>&1 &
#
# Steps (STATUS file at ~/SD7_STATUS after every step; poll that, not pgrep —
# the CLI-DEPLOY overnight-idle lesson):
#   1. smoke gate (every lane × flag-state fires)
#   2. known-answer env validation vs the committed tune_d3 cache (3 merges)
#   3. both populations, 4 work-queue workers (each drains pos then ctl)
#   3b. recovery: requeue stale claims, one sequential sweep, completeness check
#   4. --score (Stage-C aggregation + postfix2 known-answer gate)
set -uo pipefail

MTC="$HOME/thesis-projects/merge-tool-comparison"
export PATH="$HOME/bin/joern/joern-cli:$PATH"     # non-interactive ssh skips .bashrc
# 4 parallel workers × Joern JVMs on a 16 GB instance: cap each JVM so the
# composition can't OOM (host JVMs inherit _JAVA_OPTIONS; docker JVMs don't).
export _JAVA_OPTIONS="-Xmx2500m"
STATUS="$HOME/SD7_STATUS"
OUT="$MTC/reports_detectors/stagec_rerun"
LOGS="$OUT/logs"
mkdir -p "$LOGS"
PY="$MTC/.venv/bin/python"
TOOL="tools/detector_stagec_rerun.py"

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

step "1_SMOKE"
$PY $TOOL --smoke > "$LOGS/smoke.log" 2>&1 || fail smoke

step "2_KNOWN_ANSWER_TUNE"
$PY $TOOL --known-answer 3 > "$LOGS/known_answer_tune.log" 2>&1 \
  || fail known_answer_tune

step "3_RUN_QUEUE"
worker() {  # worker <k> : drain positives, then controls
  local k="$1"
  $PY $TOOL --population stagec_pos --worker "$k" \
    > "$LOGS/stagec_pos_w${k}.log" 2>&1 || return 1
  $PY $TOOL --population stagec_ctl --worker "$k" \
    > "$LOGS/stagec_ctl_w${k}.log" 2>&1 || return 1
}
pids=(); rc=0
for k in 0 1 2 3; do worker "$k" & pids+=($!); done
for p in "${pids[@]}"; do wait "$p" || rc=1; done

step "3B_RECOVERY"
$PY $TOOL --requeue-stale > "$LOGS/requeue.log" 2>&1
$PY $TOOL --population stagec_pos --worker 9 > "$LOGS/stagec_pos_w9.log" 2>&1 || rc=1
$PY $TOOL --population stagec_ctl --worker 9 > "$LOGS/stagec_ctl_w9.log" 2>&1 || rc=1
POS_DONE=$(ls "$OUT/queue_stagec_pos/"*.done 2>/dev/null | wc -l)
CTL_DONE=$(ls "$OUT/queue_stagec_ctl/"*.done 2>/dev/null | wc -l)
echo "queue completeness: pos ${POS_DONE}/180 ctl ${CTL_DONE}/195"
[ "$POS_DONE" -eq 180 ] && [ "$CTL_DONE" -eq 195 ] || fail queue_incomplete
[ $rc -eq 0 ] || fail run_queue

step "4_SCORE"
$PY $TOOL --score > "$LOGS/score.log" 2>&1 || fail score

if grep -q "GATE: PASS" "$OUT/summary.txt"; then
  step "DONE"
else
  step "DONE_GATE_NOT_PASS"
fi
echo "battery complete; artifacts in reports_detectors/stagec_rerun/"
