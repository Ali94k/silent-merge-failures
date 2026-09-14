import re
import tempfile
from pathlib import Path

from src.core.interfaces import MergeTool, MergeResult, MergeOutcome
from src.core.docker_runner import run_in_docker, write_workspace_files


class WeaveTool(MergeTool):
    """Adapter for Weave entity-level merge.

    Mirrors the semantic_merge_driver WeaveBackend invocation so the comparator
    and the driver exercise the *same* tool (CLAUDE.md: comparator tracks the
    driver's backends). The image ENTRYPOINT is ``["weave-driver"]``; the CLI is
    ``BASE OURS THEIRS -o OUT [-l len] [-p path]`` (base first). The merged
    result is written to the ``-o`` file, NOT stdout.

    The ``-o`` form is deliberate: the positional/git-driver form *empties* the
    ours file on an unresolved conflict (silent data loss on v0.3.2).

    Weave is *entity-level*, so its conflict signal is the return code, not
    git-style markers:
        rc 0  -> CLEAN     (merged content in the -o file)
        rc 1  -> CONFLICT  (entity conflict summary; usually NO -o file, NO <<<)
        other -> CRASH
        timeout -> TIMEOUT
    """

    @property
    def name(self) -> str:
        return "weave"

    @property
    def docker_image(self) -> str:
        # Version-pinned per CLAUDE.md "Merge tools invoked via Docker only".
        return "merge-tools/weave:0.3.2"

    def merge(self, base: str, ours: str, theirs: str, timeout: int = 120) -> MergeResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            write_workspace_files(workspace, base, ours, theirs)

            result = run_in_docker(
                image=self.docker_image,
                cmd=[
                    "/workspace/base.java",
                    "/workspace/ours.java",
                    "/workspace/theirs.java",
                    "-o", "/workspace/out",
                    "-l", "7",
                    "-p", "ours.java",
                ],
                workspace_dir=tmpdir,
                timeout=timeout,
            )

            if result.timed_out:
                return MergeResult(
                    outcome=MergeOutcome.TIMEOUT,
                    merged_content=None,
                    conflict_count=0,
                    runtime_seconds=result.runtime_seconds,
                    raw_stdout=result.stdout,
                    raw_stderr=result.stderr,
                )

            # Weave returns 0 (clean) or 1 (entity conflict); anything else crashes.
            if result.return_code not in (0, 1):
                return MergeResult(
                    outcome=MergeOutcome.CRASH,
                    merged_content=None,
                    conflict_count=0,
                    runtime_seconds=result.runtime_seconds,
                    raw_stdout=result.stdout,
                    raw_stderr=result.stderr,
                )

            out_file = workspace / "out"
            produced = out_file.read_text() if out_file.is_file() else None
            marker_count = (
                len(re.findall(r"^<<<<<<<", produced, re.MULTILINE)) if produced else 0
            )

            if result.return_code == 1:
                # Entity-level conflict: signalled by rc, not markers, and Weave
                # usually writes no -o file. Treat as CONFLICT regardless; count
                # at least 1 so the conflict is visible in aggregates.
                return MergeResult(
                    outcome=MergeOutcome.CONFLICT,
                    merged_content=produced,
                    conflict_count=marker_count or 1,
                    runtime_seconds=result.runtime_seconds,
                    raw_stdout=result.stdout,
                    raw_stderr=result.stderr,
                )

            # rc 0 -> clean; the merged content must be in the -o file.
            if produced is None:
                return MergeResult(
                    outcome=MergeOutcome.CRASH,
                    merged_content=None,
                    conflict_count=0,
                    runtime_seconds=result.runtime_seconds,
                    raw_stdout=result.stdout,
                    raw_stderr=result.stderr,
                )

            outcome = MergeOutcome.CONFLICT if marker_count > 0 else MergeOutcome.CLEAN
            return MergeResult(
                outcome=outcome,
                merged_content=produced,
                conflict_count=marker_count,
                runtime_seconds=result.runtime_seconds,
                raw_stdout=result.stdout,
                raw_stderr=result.stderr,
            )
