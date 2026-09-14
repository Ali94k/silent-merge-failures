import re
import tempfile
from pathlib import Path

from src.core.interfaces import MergeTool, MergeResult, MergeOutcome
from src.core.docker_runner import run_native, write_workspace_files


class GitMergeFileTool(MergeTool):
    """Adapter for git merge-file (textual 3-way merge)."""

    @property
    def name(self) -> str:
        return "git-merge-file"

    def merge(self, base: str, ours: str, theirs: str, timeout: int = 30) -> MergeResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            base_path, ours_path, theirs_path = write_workspace_files(
                workspace, base, ours, theirs
            )

            # git merge-file writes result to the first file (ours)
            # --stdout sends merged output to stdout instead
            result = run_native(
                [
                    "git", "merge-file", "--stdout",
                    str(ours_path), str(base_path), str(theirs_path),
                ],
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

            merged = result.stdout
            conflict_count = len(re.findall(r"^<<<<<<<", merged, re.MULTILINE))

            if result.return_code < 0:
                outcome = MergeOutcome.CRASH
            elif result.return_code > 0:
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
