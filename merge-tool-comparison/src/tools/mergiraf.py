import re
import tempfile
from pathlib import Path

from src.core.interfaces import MergeTool, MergeResult, MergeOutcome
from src.core.docker_runner import run_in_docker, write_workspace_files


class MergirafTool(MergeTool):
    """Adapter for Mergiraf AST-aware merge.

    Mirrors the semantic_merge_driver MergirafBackend invocation so the
    comparator and the driver exercise the *same* tool (CLAUDE.md: comparator
    tracks the driver's backends). The image ENTRYPOINT is
    ``["mergiraf", "merge"]``; the CLI is ``merge BASE OURS THEIRS -p PATH``
    (base first), with the merged result written to stdout. ``-p`` supplies a
    filename so Mergiraf detects the source language.

    Outcome (mirrors the Spork adapter's stdout-marker rule):
        rc 0 or 1 + no <<<<<<<  -> CLEAN
        rc 0 or 1 + <<<<<<<     -> CONFLICT
        any other rc            -> CRASH   (parse failure / runtime error)
        timeout                 -> TIMEOUT
    """

    @property
    def name(self) -> str:
        return "mergiraf"

    @property
    def docker_image(self) -> str:
        # Version-pinned per CLAUDE.md "Merge tools invoked via Docker only".
        return "merge-tools/mergiraf:0.17.0"

    def merge(self, base: str, ours: str, theirs: str, timeout: int = 120) -> MergeResult:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            write_workspace_files(workspace, base, ours, theirs)

            # ENTRYPOINT ["mergiraf", "merge"] -> cmd is BASE OURS THEIRS -p PATH.
            result = run_in_docker(
                image=self.docker_image,
                cmd=[
                    "/workspace/base.java",
                    "/workspace/ours.java",
                    "/workspace/theirs.java",
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

            # Mergiraf returns 0 (clean) or 1 (conflict); anything else is a
            # genuine failure (unparseable input, image/runtime error).
            if result.return_code not in (0, 1):
                return MergeResult(
                    outcome=MergeOutcome.CRASH,
                    merged_content=None,
                    conflict_count=0,
                    runtime_seconds=result.runtime_seconds,
                    raw_stdout=result.stdout,
                    raw_stderr=result.stderr,
                )

            merged = result.stdout
            if not merged:
                # Valid rc but no merged output -> treat as a crash.
                return MergeResult(
                    outcome=MergeOutcome.CRASH,
                    merged_content=None,
                    conflict_count=0,
                    runtime_seconds=result.runtime_seconds,
                    raw_stdout=result.stdout,
                    raw_stderr=result.stderr,
                )

            conflict_count = len(re.findall(r"^<<<<<<<", merged, re.MULTILINE))
            outcome = MergeOutcome.CONFLICT if conflict_count > 0 else MergeOutcome.CLEAN

            return MergeResult(
                outcome=outcome,
                merged_content=merged,
                conflict_count=conflict_count,
                runtime_seconds=result.runtime_seconds,
                raw_stdout=result.stdout,
                raw_stderr=result.stderr,
            )
