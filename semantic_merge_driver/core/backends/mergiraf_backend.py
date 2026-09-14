"""MergirafBackend — three-way merge via the merge-tools/mergiraf:0.17.0 Docker image.

Per CLAUDE.md standing rule, Mergiraf is invoked through Docker only — never via
a host-PATH `mergiraf` binary. The image is built from
`merge-tool-comparison/docker/mergiraf/Dockerfile` (`make docker-build` in that
subproject).

Invocation pattern: stage base/ours/theirs in a temp dir, mount as /workspace,
run `mergiraf merge BASE OURS THEIRS -p NAME`, write stdout back to ours_path.
The `-p` flag passes the original ours_path filename so Mergiraf can detect
the source language. Verified: `-p Foo.java` is sufficient to trigger AST
mode even when the staged files are extensionless; without `-p`, extensionless
inputs fall back to text mode (see merge-tool-comparison/ISSUES.md #24).

Outcome decided by stdout-marker presence (mirrors the Spork adapter pattern at
merge-tool-comparison/src/tools/spork.py:68):
    rc 0 or 1 + no <<<<<<< at line start  -> CLEAN
    rc 0 or 1 + <<<<<<< markers           -> CONFLICT
    rc anything else / subprocess error / timeout -> CRASH
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from core.backends.base import MergeBackend, MergeOutcome


IMAGE = "merge-tools/mergiraf:0.17.0"
TIMEOUT_SECONDS = 60
CONFLICT_MARKER_RE = re.compile(r"^<<<<<<<", re.MULTILINE)


class MergirafBackend(MergeBackend):
    @property
    def name(self) -> str:
        return "mergiraf"

    def merge(
        self, base_path: str, ours_path: str, theirs_path: str
    ) -> MergeOutcome:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                tmpdir = Path(tmp)
                shutil.copyfile(base_path, tmpdir / "base")
                shutil.copyfile(ours_path, tmpdir / "ours")
                shutil.copyfile(theirs_path, tmpdir / "theirs")
                proc = subprocess.run(
                    [
                        "docker", "run", "--rm",
                        "--platform", "linux/amd64",
                        "-v", f"{tmpdir}:/workspace",
                        IMAGE,
                        "/workspace/base", "/workspace/ours", "/workspace/theirs",
                        "-p", Path(ours_path).name,
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=TIMEOUT_SECONDS,
                )
        except (FileNotFoundError, OSError, subprocess.SubprocessError) as e:
            print(
                f"MergirafBackend: subprocess error: {e}\n"
                f"  Hint: ensure Docker is running and the image exists:\n"
                f"    docker image inspect {IMAGE}\n"
                f"  Or fall back: SEMANTIC_MERGE_BACKEND=git",
                file=sys.stderr,
            )
            return MergeOutcome.CRASH

        if proc.returncode not in (0, 1):
            print(
                f"MergirafBackend: docker run exited with returncode {proc.returncode}.\n"
                f"  stderr: {proc.stderr.strip() or '(empty)'}\n"
                f"  Hint: ensure Docker is running and the image exists:\n"
                f"    docker image inspect {IMAGE}\n"
                f"  Or fall back: SEMANTIC_MERGE_BACKEND=git",
                file=sys.stderr,
            )
            return MergeOutcome.CRASH

        Path(ours_path).write_text(proc.stdout)
        if CONFLICT_MARKER_RE.search(proc.stdout):
            return MergeOutcome.CONFLICT
        return MergeOutcome.CLEAN
