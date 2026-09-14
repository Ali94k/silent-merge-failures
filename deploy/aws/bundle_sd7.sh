#!/usr/bin/env bash
# bundle_sd7.sh — LOCAL (repo root): transfer artifacts for the S-D7 Stage-C
# rerun cycle (ISSUES #31 follow-on). Tool images are BUILT ON-INSTANCE
# (standing rule; arm64-image-dies-silently lesson, CLI-DEPLOY.md).
#
#   deploy/dist/repo_sd7.tar.gz       git archive of HEAD (harness, frozen
#                                     driver suite, postfix2 known-answer
#                                     cache, tune_d3 cache, manifest, pins)
#   deploy/dist/scenarios_sd7.tar.gz  gitignored scenario JSONs:
#                                     scenarios_semantic (232, Stage-C pos),
#                                     scenarios_semantic_ctl (239, Stage-C ctl),
#                                     scenarios_detector_tune (smoke/known-answer)
#
# COPYFILE_DISABLE=1 keeps macOS AppleDouble ._* files out (CLI-DEPLOY gotcha).
# Usage:  bash deploy/aws/bundle_sd7.sh
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
OUT="$ROOT/deploy/dist"
mkdir -p "$OUT"
MTC="merge-tool-comparison"

echo "==> repo_sd7.tar.gz (git archive HEAD=$(git rev-parse --short HEAD))"
git archive --format=tar.gz -o "$OUT/repo_sd7.tar.gz" HEAD

echo "==> scenarios_sd7.tar.gz"
COPYFILE_DISABLE=1 tar czf "$OUT/scenarios_sd7.tar.gz" -C "$MTC" \
  data/scenarios_semantic \
  data/scenarios_semantic_ctl \
  data/scenarios_detector_tune

ls -lh "$OUT"/repo_sd7.tar.gz "$OUT"/scenarios_sd7.tar.gz
echo "==> sha256 (verify remote copies against these before running):"
shasum -a 256 "$OUT"/repo_sd7.tar.gz "$OUT"/scenarios_sd7.tar.gz
