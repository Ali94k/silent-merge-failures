#!/usr/bin/env bash
# bundle.sh — run LOCALLY (repo root) to produce the three transfer artifacts
# for the P2 whole-driver run on a native-x86_64 EC2 instance.
#
#   deploy/dist/repo.tar.gz       tracked repo (git archive) — harness, driver,
#                                 Stage-C raw_results.json (committed), pyproject
#   deploy/dist/scenarios.tar.gz  the gitignored materialized scenario JSONs
#                                 (data/scenarios_semantic{,_ctl}) — self-contained
#   deploy/dist/images.tar.gz     the 5 amd64 tool images (docker save) — the big one
#
# No rebuilding on the instance: the images you already built locally are amd64,
# so they `docker load` and run natively on a c7i/c6i instance.
#
# Usage:  bash deploy/aws/bundle.sh
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
OUT="$ROOT/deploy/dist"
mkdir -p "$OUT"

MTC="merge-tool-comparison"
SEM_POS="$MTC/data/scenarios_semantic"
SEM_CTL="$MTC/data/scenarios_semantic_ctl"

IMAGES=(
  "merge-tools/mergiraf:0.17.0"
  "merge-tools/refactoring-miner:2.4.0"
  "merge-tools/spork:0.5.0"
  "merge-tools/weave:0.3.2"
  "merge-tools/google-java-format:1.22.0"
  # P4 six-tool canonical run (comparator adapters use these exact tags).
  # jdime/mastery are UNPINNED :latest (ISSUES #10 retro-pinning TODO) —
  # shipped as-is; the committed reports/ artifacts remain the citable record.
  # spork:latest is dual-tagged from the same build as spork:0.5.0 (empirical
  # adapter uses the legacy untagged name), so it adds no transfer size.
  "merge-tools/jdime:latest"
  "merge-tools/mastery:latest"
  "merge-tools/spork:latest"
)

echo "==> 1/3  repo.tar.gz  (tracked files only — no heavy gitignored data)"
git archive --format=tar.gz -o "$OUT/repo.tar.gz" HEAD

echo "==> 2/3  scenarios.tar.gz  (gitignored, self-contained base/ours/theirs/dev)"
for d in "$SEM_POS" "$SEM_CTL"; do
  [ -d "$d" ] || { echo "ERROR: $d missing — regenerate with select_materialize.py"; exit 1; }
done
tar czf "$OUT/scenarios.tar.gz" -C "$MTC" \
  data/scenarios_semantic data/scenarios_semantic_ctl

echo "==> 3/3  images.tar.gz  (docker save 5 amd64 images — several GB, be patient)"
have="$(docker images --format '{{.Repository}}:{{.Tag}}')"
for im in "${IMAGES[@]}"; do
  echo "$have" | grep -qx "$im" || { echo "ERROR: image not present locally: $im"; exit 1; }
done
docker save "${IMAGES[@]}" | gzip > "$OUT/images.tar.gz"

echo
echo "==> done. artifacts in $OUT :"
( cd "$OUT" && ls -lh repo.tar.gz scenarios.tar.gz images.tar.gz && shasum -a 256 *.tar.gz )
cat <<EOF

Next (see deploy/aws/RUNBOOK.md):
  # from your laptop, after the instance is up (replace HOST + key):
  scp -i KEY.pem deploy/dist/*.tar.gz deploy/aws/provision.sh ubuntu@HOST:~
  # the images file is the big one — if scp is slow, push it via S3 instead.
EOF
