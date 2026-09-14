import re
import tempfile
from pathlib import Path

from src.core.interfaces import MergeTool, MergeResult, MergeOutcome
from src.core.docker_runner import run_in_docker, write_workspace_files


class SporkTool(MergeTool):
    """Adapter for Spork structured merge."""

    @property
    def name(self) -> str:
        return "spork"

    @property
    def docker_image(self) -> str:
        return "merge-tools/spork"

    def merge(self, base: str, ours: str, theirs: str, timeout: int = 120) -> MergeResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            write_workspace_files(workspace, base, ours, theirs)

            # Spork CLI: spork LEFT BASE RIGHT (outputs to stdout)
            result = run_in_docker(
                image=self.docker_image,
                cmd=[
                    "/workspace/ours.java",
                    "/workspace/base.java",
                    "/workspace/theirs.java",
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

            if result.return_code < 0:
                return MergeResult(
                    outcome=MergeOutcome.CRASH,
                    merged_content=None,
                    conflict_count=0,
                    runtime_seconds=result.runtime_seconds,
                    raw_stdout=result.stdout,
                    raw_stderr=result.stderr,
                )

            if result.return_code != 0 and not result.stdout:
                return MergeResult(
                    outcome=MergeOutcome.CRASH,
                    merged_content=None,
                    conflict_count=0,
                    runtime_seconds=result.runtime_seconds,
                    raw_stdout=result.stdout,
                    raw_stderr=result.stderr,
                )

            merged = result.stdout
            conflict_count = len(re.findall(r"^<<<<<<<", merged, re.MULTILINE))

            if conflict_count > 0:
                outcome = MergeOutcome.CONFLICT
            else:
                outcome = MergeOutcome.CLEAN

            return MergeResult(
                outcome=outcome,
                merged_content=merged,
                conflict_count=conflict_count,
                runtime_seconds=result.runtime_seconds,
                raw_stdout=result.stdout,
                raw_stderr=result.stderr,
            )
