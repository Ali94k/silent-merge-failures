"""SporkBackend — three-way merge via the merge-tools/spork:0.5.0 Docker image.

Per CLAUDE.md standing rule, Spork is invoked through Docker only — never via a
host-PATH `spork` binary. The image is built from
`merge-tool-comparison/docker/spork/Dockerfile` (`make docker-build` in that
subproject), which pins the Spork JAR to v0.5.0
(github.com/ASSERT-KTH/spork/releases v0.5.0).

Invocation pattern mirrors the proven empirical adapter at
merge-tool-comparison/src/tools/spork.py:25-35: the Docker ENTRYPOINT is
`java -jar /opt/spork.jar`, and Spork's CLI is `spork LEFT BASE RIGHT`, i.e.
`<ours> <base> <theirs>`, emitting the merged result to stdout. Files are
staged with a `.java` extension because Spork (Spoon-based) infers the source
language from the filename; Spork is Java-only, so non-Java inputs fail closed
to CRASH (the driver then rejects the merge — acceptable for a Java backend).

Outcome decided by return code + stdout-marker presence (mirrors spork.py:47-73):
    rc < 0                                  -> CRASH (killed by signal)
    rc != 0 and empty stdout                -> CRASH (no usable output)
    otherwise, <<<<<<< at a line start      -> CONFLICT
    otherwise                               -> CLEAN
Any subprocess error / timeout             -> CRASH
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from core.backends.base import MergeBackend, MergeOutcome


IMAGE = "merge-tools/spork:0.5.0"
TIMEOUT_SECONDS = 120
CONFLICT_MARKER_RE = re.compile(r"^<<<<<<<", re.MULTILINE)


class SporkBackend(MergeBackend):
    @property
    def name(self) -> str:
        return "spork"

    def merge(
        self, base_path: str, ours_path: str, theirs_path: str
    ) -> MergeOutcome:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                tmpdir = Path(tmp)
                shutil.copyfile(base_path, tmpdir / "base.java")
                shutil.copyfile(ours_path, tmpdir / "ours.java")
                shutil.copyfile(theirs_path, tmpdir / "theirs.java")
                proc = subprocess.run(
                    [
                        "docker", "run", "--rm",
                        "--platform", "linux/amd64",
                        "-v", f"{tmpdir}:/workspace",
                        IMAGE,
                        "/workspace/ours.java",
                        "/workspace/base.java",
                        "/workspace/theirs.java",
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=TIMEOUT_SECONDS,
                )
        except (FileNotFoundError, OSError, subprocess.SubprocessError) as e:
            print(
                f"SporkBackend: subprocess error: {e}\n"
                f"  Hint: ensure Docker is running and the image exists:\n"
                f"    docker image inspect {IMAGE}\n"
                f"  Or fall back: SEMANTIC_MERGE_BACKEND=git",
                file=sys.stderr,
            )
            return MergeOutcome.CRASH

        if proc.returncode < 0 or (proc.returncode != 0 and not proc.stdout):
            print(
                f"SporkBackend: docker run exited with returncode {proc.returncode} "
                f"and no usable output.\n"
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
