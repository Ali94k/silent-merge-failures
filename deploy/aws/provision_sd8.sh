#!/usr/bin/env bash
# provision_sd8.sh — ON the EC2 instance (Ubuntu 24.04, x86_64) for the S-D8
# whole-driver flag-pair cycle (ISSUES #31 follow-on).
#
# Image policy (Ali 2026-07-22): pinned images BUILT ON-INSTANCE (mergiraf
# 0.17.0, refactoring-miner 2.4.0, spork 0.5.0 [+ legacy untagged dual-tag],
# weave 0.3.2, google-java-format 1.22.0, git-merge-file); the unpinned
# jdime/mastery :latest are docker-LOADED from images_sd8.tar.gz (the exact
# bits behind the committed canonical table). Every image gets a live probe —
# a loaded image is not a working image (arm64 lesson, CLI-DEPLOY.md).
#
# Expects in $HOME: repo_sd8.tar.gz  scenarios_sd8.tar.gz  images_sd8.tar.gz
# Usage: bash provision_sd8.sh   (then re-login for the docker group)
set -euo pipefail

JOERN_VERSION="4.0.436"          # PINNED — detectors were validated against this
HOME_DIR="$HOME"
REPO_DIR="$HOME_DIR/thesis-projects"
MTC="$REPO_DIR/merge-tool-comparison"

echo "==> apt packages"
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  docker.io git curl unzip tmux \
  python3.12 python3.12-venv python3-pip \
  openjdk-21-jdk

sudo usermod -aG docker "$USER" || true
sudo systemctl enable --now docker

echo "==> unpack repo + scenarios"
mkdir -p "$REPO_DIR"
tar xzf "$HOME_DIR/repo_sd8.tar.gz" -C "$REPO_DIR"
tar xzf "$HOME_DIR/scenarios_sd8.tar.gz" -C "$MTC"
find "$MTC/data" -name "._*" -delete || true
for d in scenarios_semantic scenarios_semantic_ctl scenarios; do
  test -d "$MTC/data/$d" || { echo "ERR: data/$d missing"; exit 1; }
done
test -f "$MTC/reports_detection/full/raw_results.json" \
  || { echo "ERR: Stage-C cache missing (hybrid-oracle reference)"; exit 1; }
test -f "$MTC/reports_detectors/whole_driver_flagon/predicted_flagoff.csv" \
  || { echo "ERR: pre-registered prediction missing"; exit 1; }
test -f "$MTC/reports/results.csv" \
  || { echo "ERR: committed canonical six-tool table missing"; exit 1; }
python3 - <<'EOF'
import json, os
m = json.load(open(f"{os.environ['HOME']}/thesis-projects/merge-tool-comparison/reports_detectors/manifest.json"))
assert m.get("detector_suite_commit"), "detector_suite_commit not frozen in manifest"
print("frozen suite commit:", m["detector_suite_commit"])
EOF

echo "==> load shipped unpinned images (jdime, mastery — exact canonical bits)"
sudo docker load < "$HOME_DIR/images_sd8.tar.gz"

echo "==> build PINNED tool images ON-INSTANCE (native x86_64)"
sudo docker build --platform linux/amd64 -t merge-tools/mergiraf:0.17.0 \
  --build-arg MERGIRAF_VERSION=0.17.0 "$MTC/docker/mergiraf/"
sudo docker build --platform linux/amd64 -t merge-tools/refactoring-miner:2.4.0 \
  "$MTC/docker/refactoring_miner/"
sudo docker build --platform linux/amd64 -t merge-tools/spork:0.5.0 -t merge-tools/spork \
  "$MTC/docker/spork/"
sudo docker build --platform linux/amd64 -t merge-tools/weave:0.3.2 \
  --build-arg WEAVE_VERSION=0.3.2 "$MTC/docker/weave/"
sudo docker build --platform linux/amd64 -t merge-tools/google-java-format:1.22.0 \
  --build-arg GJF_VERSION=1.22.0 "$MTC/docker/google-java-format/"
sudo docker build --platform linux/amd64 -t merge-tools/git-merge-file \
  "$MTC/docker/git-merge-file/"
sudo docker images --format '  {{.Repository}}:{{.Tag}}' | grep merge-tools

echo "==> live image probes (a loaded image is not a working image)"
sudo docker run --rm merge-tools/mergiraf:0.17.0 --version
sudo docker run --rm --entrypoint sh merge-tools/refactoring-miner:2.4.0 \
  -c 'ls /opt 2>/dev/null | head -3; echo rm2-image-alive'
sudo docker run --rm --entrypoint sh merge-tools/jdime:latest -c 'echo jdime-image-alive'
sudo docker run --rm --entrypoint sh merge-tools/mastery:latest -c 'echo mastery-image-alive'
sudo docker run --rm --entrypoint sh merge-tools/spork:0.5.0 -c 'echo spork-image-alive'
sudo docker run --rm --entrypoint sh merge-tools/weave:0.3.2 -c 'echo weave-image-alive'
echo "==> gjf REAL format probe (silent-degradation lesson: must produce formatted output)"
GJF_OUT="$(echo 'class A{int  x ;}' | sudo docker run --rm -i \
  merge-tools/google-java-format:1.22.0 2>&1)"
echo "$GJF_OUT" | grep -q "int x;" || { echo "ERR: gjf probe failed: $GJF_OUT"; exit 1; }
echo "    gjf probe OK"

echo "==> install Joern $JOERN_VERSION (pinned)"
mkdir -p "$HOME_DIR/bin/joern"
cd "$HOME_DIR/bin/joern"
if [ ! -x "$HOME_DIR/bin/joern/joern-cli/joern" ]; then
  curl -fL -o joern-cli.zip \
    "https://github.com/joernio/joern/releases/download/v${JOERN_VERSION}/joern-cli.zip"
  unzip -q -o joern-cli.zip
  rm -f joern-cli.zip
fi
JOERN_BIN="$HOME_DIR/bin/joern/joern-cli"
grep -q 'bin/joern/joern-cli' "$HOME_DIR/.bashrc" || \
  echo "export PATH=\"$JOERN_BIN:\$PATH\"" >> "$HOME_DIR/.bashrc"
export PATH="$JOERN_BIN:$PATH"
command -v joern-parse >/dev/null || { echo "ERR: joern-parse not on PATH"; exit 1; }

echo "==> Python venv + deps"
cd "$MTC"
python3.12 -m venv .venv
./.venv/bin/pip install --upgrade pip wheel
./.venv/bin/pip install -e .
./.venv/bin/pip install pytest
./.venv/bin/python -c "import tree_sitter_java, yaml, tabulate, git; print('deps OK')"

echo "==================================================================="
echo " S-D8 provision complete. Re-login (docker group), then:"
echo "   nohup bash thesis-projects/deploy/aws/run_sd8.sh > sd8_run.log 2>&1 &"
echo "==================================================================="
