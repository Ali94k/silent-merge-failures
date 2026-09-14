"""WeaveBackend — three-way merge via the merge-tools/weave:0.3.2 Docker image.

Per CLAUDE.md standing rule, Weave is invoked through Docker only — never via a
host-PATH `weave-driver` binary (this overrides the stale
docs/plans/weave-integration.md W1 "native, no Docker" decision; see that plan's
header note and CLAUDE.md "Merge tools invoked via Docker only"). The image is
built from `merge-tool-comparison/docker/weave/Dockerfile` (`make docker-build`
in that subproject), pinned to Weave v0.3.2 (Ataraxy-Labs/weave @ tag v0.3.2).

Invocation — verified against `weave-driver --help` for v0.3.2:

    weave-driver <base> <ours> <theirs> [marker-size] [file-path]   (in-place on ours)
    weave-driver <base> <ours> <theirs> -o <output> [-l len] [-p path]

This backend uses the **`-o <output>` form** so the staged `ours` file is never
mutated by Weave directly (the positional form *empties* the ours file on an
unresolved conflict — confirmed empirically on v0.3.2 — which would be silent
data loss). `-p` passes the original filename so Weave's tree-sitter layer
detects the source language.

Weave is *entity-level*. Its observed v0.3.2 behaviour on three-way input:
    rc 0  -> CLEAN: merged content written to the -o output file.
    rc 1  -> CONFLICT: prints an entity conflict summary; on a whole-entity
             conflict it writes NO output file (no git-style <<<<<<< markers).
    other -> CRASH.
    subprocess error / timeout -> CRASH.

On CLEAN we copy the output into ours_path. On CONFLICT we copy the output if
Weave produced one (it may contain entity-annotated markers for partial
conflicts) but otherwise leave ours_path untouched — the driver rejects the
merge via exit 1 regardless, and emptying ours_path would be data loss.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from core.backends.base import MergeBackend, MergeOutcome


IMAGE = "merge-tools/weave:0.3.2"
TIMEOUT_SECONDS = 60
MARKER_LENGTH = "7"
CONFLICT_MARKER_RE = re.compile(r"^<<<<<<<", re.MULTILINE)


class WeaveBackend(MergeBackend):
    @property
    def name(self) -> str:
        return "weave"

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
                        "/workspace/base",
                        "/workspace/ours",
                        "/workspace/theirs",
                        "-o", "/workspace/out",
                        "-l", MARKER_LENGTH,
                        "-p", Path(ours_path).name,
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=TIMEOUT_SECONDS,
                )
                if proc.returncode not in (0, 1):
                    print(
                        f"WeaveBackend: docker run exited with returncode "
                        f"{proc.returncode}.\n"
                        f"  stderr: {proc.stderr.strip() or '(empty)'}\n"
                        f"  Hint: ensure Docker is running and the image exists:\n"
                        f"    docker image inspect {IMAGE}\n"
                        f"  Or fall back: SEMANTIC_MERGE_BACKEND=git",
                        file=sys.stderr,
                    )
                    return MergeOutcome.CRASH

                out_file = tmpdir / "out"
                produced = (
                    out_file.read_text(encoding="utf-8", errors="replace")
                    if out_file.is_file()
                    else ""
                )
        except (FileNotFoundError, OSError, subprocess.SubprocessError) as e:
            print(
                f"WeaveBackend: subprocess error: {e}\n"
                f"  Hint: ensure Docker is running and the image exists:\n"
                f"    docker image inspect {IMAGE}\n"
                f"  Or fall back: SEMANTIC_MERGE_BACKEND=git",
                file=sys.stderr,
            )
            return MergeOutcome.CRASH

        if proc.returncode == 1:
            # Entity-level conflict. Weave usually writes no merged file here;
            # only overwrite ours_path if it actually produced content (which
            # may carry entity-annotated markers). Never blank ours_path.
            if produced:
                Path(ours_path).write_text(produced)
            return MergeOutcome.CONFLICT

        # rc 0 — clean merge; Weave wrote the merged result to the -o file.
        Path(ours_path).write_text(produced)
        if CONFLICT_MARKER_RE.search(produced):
            return MergeOutcome.CONFLICT
        return MergeOutcome.CLEAN
