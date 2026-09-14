#!/usr/bin/env bash
# run_sd8.sh — ON-INSTANCE orchestrator for the S-D8 whole-driver flag-pair
# battery (ISSUES #31 follow-on). Run detached:
#   nohup bash run_sd8.sh > sd8_run.log 2>&1 &
#
# STATUS file at ~/SD8_STATUS after every step (poll that, not pgrep — the
# CLI-DEPLOY overnight-idle lesson). Steps:
#   1. flag-plumbing smoke: the three experimental-lane pytest batteries
#      (validate the flag gating on THIS box) + a 1-merge harness smoke
#   2. canonical six-tool table reproduction (env gate part 1 — arm64 lesson;
#      count columns must match the committed reports/results.csv exactly)
#   3. driver-auto-off full arm (471 files, ~13 h)
#   4. reconciliation gate vs the pre-registered predicted_flagoff.csv
#      (env gate part 2 — ABORTS the battery before the flag-on arm burns)
#   5. driver-auto-on full arm (~14 h; latency delta is a first-class result)
#   6. final report render
#
# NOTE: _JAVA_OPTIONS deliberately NOT set (S-D7 sets it for 4-way workers) —
# S-D8 runs sequentially and must match the P2/P3 single-worker latency
# conditions, since latency IS a deliverable.
set -uo pipefail

MTC="$HOME/thesis-projects/merge-tool-comparison"
export PATH="$HOME/bin/joern/joern-cli:$PATH"     # non-interactive ssh skips .bashrc
STATUS="$HOME/SD8_STATUS"
OUT="$MTC/reports_detectors/whole_driver_flagon"
LOGS="$OUT/logs"
mkdir -p "$LOGS"
PY="$MTC/.venv/bin/python"
TOOL="tools/whole_driver_flagon.py"

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
( cd "$HOME/thesis-projects/semantic_merge_driver" && \
  "$PY" -m pytest tests/test_import_prune_usage.py tests/test_signature_stale_call.py \
    tests/test_unresolved_reference.py -q ) > "$LOGS/smoke_pytest.log" 2>&1 \
  || fail smoke_pytest
$PY $TOOL --limit 1 --out workspace/sd8_smoke_inst > "$LOGS/smoke_harness.log" 2>&1 \
  || fail smoke_harness

step "2_CANONICAL_SIXTOOL"
$PY -m src.cli run > "$LOGS/canonical_run.log" 2>&1 || fail canonical_run
$PY -m src.cli report --format csv --output-dir reports_canonical_check \
  > "$LOGS/canonical_report.log" 2>&1 || fail canonical_report
$PY - <<'EOF' > "$LOGS/canonical_gate.log" 2>&1 || fail canonical_gate
import csv, sys
KEYS = ["tool", "category", "scenarios", "tp", "fp", "tn", "fn",
        "crashes", "timeouts", "weighted_cost"]
def rows(path):
    return {(r["tool"], r["category"]): {k: r[k] for k in KEYS}
            for r in csv.DictReader(open(path))}
ref, got = rows("reports/results.csv"), rows("reports_canonical_check/results.csv")
bad = []
for key in sorted(set(ref) | set(got)):
    a, b = ref.get(key), got.get(key)
    if a != b:
        bad.append(f"{key}: committed={a} reproduced={b}")
spork = ref.get(("spork", "all"))
print(f"canonical rows: committed={len(ref)} reproduced={len(got)}; "
      f"spork/all committed tp={spork['tp']} fp={spork['fp']}")
for line in bad:
    print("  MISMATCH", line)
print("CANONICAL GATE:", "PASS" if not bad else "FAIL")
sys.exit(0 if not bad else 1)
EOF
grep -q "CANONICAL GATE: PASS" "$LOGS/canonical_gate.log" || fail canonical_gate

step "3_FLAGOFF_ARM"
$PY $TOOL --configs driver-auto-off > "$LOGS/flagoff.log" 2>&1 || fail flagoff_arm

step "4_RECONCILIATION_GATE"
$PY $TOOL --check-gate > "$LOGS/gate.log" 2>&1 || fail reconciliation_gate

step "5_FLAGON_ARM"
$PY $TOOL --configs driver-auto-on > "$LOGS/flagon.log" 2>&1 || fail flagon_arm

step "6_REPORT"
$PY $TOOL --report-only > "$LOGS/report.log" 2>&1 || fail report

step "DONE"
echo "battery complete; artifacts in reports_detectors/whole_driver_flagon/"
