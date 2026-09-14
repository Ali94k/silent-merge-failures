#!/usr/bin/env bash
# bundle_sd8.sh — LOCAL (repo root): transfer artifacts for the S-D8
# whole-driver flag-pair re-pricing cycle (ISSUES #31 follow-on).
#
# Image policy (ratified by Ali 2026-07-22): version-PINNED images are built
# ON-INSTANCE (standing rule); the two UNPINNED :latest images (jdime,
# mastery — Dockerfiles clone upstream HEAD) are docker-saved here so the
# canonical six-tool gate compares against the exact bits behind the
# committed reports/results.csv. Both are arch-verified amd64 before saving.
#
#   deploy/dist/repo_sd8.tar.gz       git archive of HEAD (harness, frozen
#                                     driver suite, predicted_flagoff.csv,
#                                     Stage-C + postfix2 caches, canonical
#                                     reports/results.csv, manifest)
#   deploy/dist/scenarios_sd8.tar.gz  gitignored scenario JSONs:
#                                     scenarios_semantic (232, P1 pos),
#                                     scenarios_semantic_ctl (239, P1 ctl),
#                                     scenarios (50, canonical six-tool gate)
#   deploy/dist/images_sd8.tar.gz     jdime:latest + mastery:latest (amd64)
#
# Usage:  bash deploy/aws/bundle_sd8.sh
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
OUT="$ROOT/deploy/dist"
mkdir -p "$OUT"
MTC="merge-tool-comparison"

test -f "$MTC/reports_detectors/whole_driver_flagon/predicted_flagoff.csv" \
  || { echo "ERR: predicted_flagoff.csv not present — pre-register before bundling"; exit 1; }
git diff --quiet -- "$MTC/reports_detectors/whole_driver_flagon/predicted_flagoff.csv" \
  || { echo "ERR: predicted_flagoff.csv has uncommitted changes — commit the pre-registration first"; exit 1; }

echo "==> arch-verify the two shipped images (must be linux/amd64)"
for im in merge-tools/jdime:latest merge-tools/mastery:latest; do
  arch="$(docker inspect --format '{{.Os}}/{{.Architecture}}' "$im")"
  echo "    $im  $arch"
  [ "$arch" = "linux/amd64" ] || { echo "ERR: $im is $arch — rebuild with --platform linux/amd64"; exit 1; }
done

echo "==> repo_sd8.tar.gz (git archive HEAD=$(git rev-parse --short HEAD))"
git archive --format=tar.gz -o "$OUT/repo_sd8.tar.gz" HEAD

echo "==> scenarios_sd8.tar.gz"
COPYFILE_DISABLE=1 tar czf "$OUT/scenarios_sd8.tar.gz" -C "$MTC" \
  data/scenarios_semantic \
  data/scenarios_semantic_ctl \
  data/scenarios

echo "==> images_sd8.tar.gz (docker save jdime + mastery)"
docker save merge-tools/jdime:latest merge-tools/mastery:latest \
  | gzip > "$OUT/images_sd8.tar.gz"

ls -lh "$OUT"/repo_sd8.tar.gz "$OUT"/scenarios_sd8.tar.gz "$OUT"/images_sd8.tar.gz
echo "==> sha256 (verify remote copies against these before running):"
shasum -a 256 "$OUT"/repo_sd8.tar.gz "$OUT"/scenarios_sd8.tar.gz "$OUT"/images_sd8.tar.gz
