#!/usr/bin/env bash
# provision_sd5.sh — ON the EC2 instance (Ubuntu 24.04, x86_64) for the S-D5
# detector evaluation cycle (ISSUES #31). Mirrors provision.sh, except the
# two needed tool images (mergiraf 0.17.0 + refactoring-miner 2.4.0) are
# BUILT ON-INSTANCE from the repo's docker/ contexts — no images tarball.
#
# Expects in $HOME: repo_sd5.tar.gz  scenarios_sd5.tar.gz
# Usage: bash provision_sd5.sh   (then re-login for the docker group)
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
tar xzf "$HOME_DIR/repo_sd5.tar.gz" -C "$REPO_DIR"
tar xzf "$HOME_DIR/scenarios_sd5.tar.gz" -C "$MTC"
find "$MTC/data" -name "._*" -delete || true
for d in scenarios_semantic scenarios_taxonomy_hi scenarios_phase2b \
         scenarios_phase2b_ctl scenarios_detector_tune; do
  test -d "$MTC/data/$d" || { echo "ERR: data/$d missing"; exit 1; }
done
test -f "$MTC/reports_detectors/tune_d3/raw_results.json" \
  || { echo "ERR: tune_d3 known-answer cache missing from repo archive"; exit 1; }
test -f "$MTC/reports_detectors/manifest.json" || { echo "ERR: manifest missing"; exit 1; }
python3 - <<'EOF'
import json
m = json.load(open(f"{__import__('os').environ['HOME']}/thesis-projects/merge-tool-comparison/reports_detectors/manifest.json"))
assert m.get("detector_suite_commit"), "detector_suite_commit not frozen in manifest"
print("frozen suite commit:", m["detector_suite_commit"])
EOF

echo "==> build tool images ON-INSTANCE (native x86_64)"
sudo docker build --platform linux/amd64 -t merge-tools/mergiraf:0.17.0 \
  "$MTC/docker/mergiraf/"
sudo docker build --platform linux/amd64 -t merge-tools/refactoring-miner:2.4.0 \
  "$MTC/docker/refactoring_miner/"
sudo docker images --format '  {{.Repository}}:{{.Tag}}' | grep merge-tools

echo "==> live image probes (a loaded image is not a working image)"
sudo docker run --rm merge-tools/mergiraf:0.17.0 --version
sudo docker run --rm --entrypoint sh merge-tools/refactoring-miner:2.4.0 \
  -c 'ls /opt 2>/dev/null | head -3; echo rm2-image-alive'

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
./.venv/bin/python -c "import tree_sitter_java, yaml, tabulate, git; print('deps OK')"

echo "==================================================================="
echo " S-D5 provision complete. Re-login (docker group), then:"
echo "   bash thesis-projects/deploy/aws/run_sd5.sh"
echo "==================================================================="
