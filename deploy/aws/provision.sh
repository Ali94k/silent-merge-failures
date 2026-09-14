#!/usr/bin/env bash
# provision.sh — run ON the EC2 instance (Ubuntu 24.04 LTS, native x86_64).
# Mirrors the local setup exactly: native Python + native Joern + Docker tool
# images. Idempotent-ish; safe to re-run.
#
# Expects these in the home dir (scp'd from your laptop after bundle.sh):
#   repo.tar.gz  scenarios.tar.gz  images.tar.gz
#
# Usage:  bash provision.sh
#   then LOG OUT and back in (docker group), and follow RUNBOOK.md "Run".
set -euo pipefail

JOERN_VERSION="4.0.436"          # PINNED — detectors were validated against this
HOME_DIR="$HOME"
REPO_DIR="$HOME_DIR/thesis-projects"
MTC="$REPO_DIR/merge-tool-comparison"

echo "==================================================================="
echo " P2 provision — Joern $JOERN_VERSION, Docker images, Python venv"
echo "==================================================================="

echo "==> apt packages (Docker, git, Python 3.12, JDK 21, tmux)"
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  docker.io git curl unzip tmux \
  python3.12 python3.12-venv python3-pip \
  openjdk-21-jdk

echo "==> add $USER to docker group (takes effect on next login)"
sudo usermod -aG docker "$USER" || true
sudo systemctl enable --now docker

echo "==> unpack repo + scenarios"
mkdir -p "$REPO_DIR"
tar xzf "$HOME_DIR/repo.tar.gz" -C "$REPO_DIR"
# scenarios.tar.gz carries data/scenarios_semantic{,_ctl} relative to MTC
tar xzf "$HOME_DIR/scenarios.tar.gz" -C "$MTC"
test -d "$MTC/data/scenarios_semantic"     || { echo "ERR: positives missing"; exit 1; }
test -d "$MTC/data/scenarios_semantic_ctl" || { echo "ERR: controls missing"; exit 1; }
# Stage-C reuse + oracle reference come from the committed file inside repo.tar.gz:
test -f "$MTC/reports_detection/full/raw_results.json" \
  || { echo "ERR: Stage-C raw_results.json missing from repo archive"; exit 1; }

echo "==> docker load the 5 amd64 tool images (uses sudo until re-login)"
sudo docker load < <(gunzip -c "$HOME_DIR/images.tar.gz")
echo "    images present:"
sudo docker images --format '  {{.Repository}}:{{.Tag}}' | grep -E "merge-tools" || true

echo "==> install Joern $JOERN_VERSION to ~/bin/joern (pinned release zip)"
mkdir -p "$HOME_DIR/bin/joern"
cd "$HOME_DIR/bin/joern"
if [ ! -x "$HOME_DIR/bin/joern/joern-cli/joern" ]; then
  # Self-contained dist; needs a JDK on PATH (openjdk-21 installed above).
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

echo "==> Python venv + deps (matches merge-tool-comparison/pyproject.toml)"
cd "$MTC"
python3.12 -m venv .venv
./.venv/bin/pip install --upgrade pip wheel
./.venv/bin/pip install -e .          # click pyyaml tabulate gitpython tree-sitter[-java]
./.venv/bin/python -c "import tree_sitter_java, yaml, tabulate; print('deps OK')"

echo
echo "==================================================================="
echo " provision complete."
echo " NOW: log out + back in (or run 'newgrp docker') so docker works"
echo "      without sudo, then follow RUNBOOK.md → 'Run'."
echo "   sanity: docker run --rm merge-tools/mergiraf:0.17.0 --version 2>/dev/null || true"
echo "           joern --version | tail -1"
echo "==================================================================="
