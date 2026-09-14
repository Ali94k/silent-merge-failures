#!/usr/bin/env bash
# bundle_sd5.sh — LOCAL (repo root): transfer artifacts for the S-D5 detector
# evaluation cycle (ISSUES #31, GD3). Two tarballs only — tool images are
# BUILT ON-INSTANCE from the repo's docker/ contexts (standing rule; avoids
# the arm64-image-dies-silently class from CLI-DEPLOY.md).
#
#   deploy/dist/repo_sd5.tar.gz       git archive of HEAD (harness, driver at
#                                     the frozen suite commit, committed
#                                     controls/labels/pins, tune_d3 cache)
#   deploy/dist/scenarios_sd5.tar.gz  gitignored scenario JSONs:
#                                     scenarios_semantic + scenarios_taxonomy_hi
#                                     (held-out + derivation units, sha-pinned),
#                                     scenarios_phase2b{,_ctl} (spgroup),
#                                     scenarios_detector_tune (smoke/known-answer)
#
# COPYFILE_DISABLE=1 keeps macOS AppleDouble ._* files out (CLI-DEPLOY gotcha).
# Usage:  bash deploy/aws/bundle_sd5.sh
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
OUT="$ROOT/deploy/dist"
mkdir -p "$OUT"
MTC="merge-tool-comparison"

echo "==> repo_sd5.tar.gz (git archive HEAD=$(git rev-parse --short HEAD))"
git archive --format=tar.gz -o "$OUT/repo_sd5.tar.gz" HEAD

echo "==> scenarios_sd5.tar.gz"
COPYFILE_DISABLE=1 tar czf "$OUT/scenarios_sd5.tar.gz" -C "$MTC" \
  data/scenarios_semantic \
  data/scenarios_taxonomy_hi \
  data/scenarios_phase2b \
  data/scenarios_phase2b_ctl \
  data/scenarios_detector_tune

ls -lh "$OUT"/repo_sd5.tar.gz "$OUT"/scenarios_sd5.tar.gz
echo "==> sha256 (verify remote copies against these before running):"
shasum -a 256 "$OUT"/repo_sd5.tar.gz "$OUT"/scenarios_sd5.tar.gz
