import re
import tempfile
from pathlib import Path

from src.core.interfaces import MergeTool, MergeResult, MergeOutcome
from src.core.docker_runner import run_in_docker, write_workspace_files


class MasteryTool(MergeTool):
    """Adapter for Mastery structured merge (Zhu et al., SETTA 2022)."""

    @property
    def name(self) -> str:
        return "mastery"

    @property
    def docker_image(self) -> str:
        return "merge-tools/mastery"

    def merge(self, base: str, ours: str, theirs: str, timeout: int = 120) -> MergeResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            write_workspace_files(workspace, base, ours, theirs)

            # Mastery: merge <left> <base> <right> -o <output>
            result = run_in_docker(
                image=self.docker_image,
                cmd=[
                    "merge",
                    "/workspace/ours.java",
                    "/workspace/base.java",
                    "/workspace/theirs.java",
                    "-o", "/workspace/merged.java",
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

            merged_path = workspace / "merged.java"
            if not merged_path.exists() or merged_path.stat().st_size == 0:
                return MergeResult(
                    outcome=MergeOutcome.CRASH,
                    merged_content=None,
                    conflict_count=0,
                    runtime_seconds=result.runtime_seconds,
                    raw_stdout=result.stdout,
                    raw_stderr=result.stderr,
                )

            merged = merged_path.read_text()
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
