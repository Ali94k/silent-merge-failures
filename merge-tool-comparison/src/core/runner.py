import json
import logging
from pathlib import Path

from src.core.interfaces import MergeTool, MergeResult, MergeScenario, MergeOutcome

logger = logging.getLogger(__name__)


def _serialize_result(result: MergeResult) -> dict:
    return {
        "outcome": result.outcome.value,
        "merged_content": result.merged_content,
        "conflict_count": result.conflict_count,
        "runtime_seconds": result.runtime_seconds,
        "raw_stdout": result.raw_stdout[:5000],  # Truncate large output
        "raw_stderr": result.raw_stderr[:5000],
    }


def _deserialize_result(data: dict) -> MergeResult:
    return MergeResult(
        outcome=MergeOutcome(data["outcome"]),
        merged_content=data.get("merged_content"),
        conflict_count=data.get("conflict_count", 0),
        runtime_seconds=data.get("runtime_seconds", 0),
        raw_stdout=data.get("raw_stdout", ""),
        raw_stderr=data.get("raw_stderr", ""),
    )


class ComparisonRunner:
    """Orchestrates running all tools on all scenarios."""

    def __init__(
        self,
        tools: list[MergeTool],
        scenarios: list[MergeScenario],
        results_dir: str = "data/results",
    ):
        self.tools = tools
        self.scenarios = scenarios
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_all(self) -> dict[str, dict[str, MergeResult]]:
        """
        Run all tools on all scenarios.

        Returns: {scenario_id: {tool_name: MergeResult}}
        """
        all_results: dict[str, dict[str, MergeResult]] = {}

        total = len(self.scenarios) * len(self.tools)
        done = 0

        for scenario in self.scenarios:
            all_results[scenario.scenario_id] = {}

            for tool in self.tools:
                # Check for cached result
                cached = self._load_cached(scenario.scenario_id, tool.name)
                if cached:
                    all_results[scenario.scenario_id][tool.name] = cached
                    done += 1
                    logger.info(
                        f"[{done}/{total}] Cached: {tool.name} on {scenario.scenario_id}"
                    )
                    continue

                # Run the tool
                logger.info(
                    f"[{done + 1}/{total}] Running: {tool.name} on {scenario.scenario_id}"
                )
                try:
                    result = tool.merge(
                        base=scenario.base_content,
                        ours=scenario.ours_content,
                        theirs=scenario.theirs_content,
                    )
                except Exception as e:
                    logger.error(f"Tool {tool.name} crashed on {scenario.scenario_id}: {e}")
                    result = MergeResult(
                        outcome=MergeOutcome.CRASH,
                        merged_content=None,
                        conflict_count=0,
                        runtime_seconds=0,
                        raw_stderr=str(e),
                    )

                all_results[scenario.scenario_id][tool.name] = result
                self._save_result(scenario.scenario_id, tool.name, result)
                done += 1

        return all_results

    def _result_path(self, scenario_id: str, tool_name: str) -> Path:
        scenario_dir = self.results_dir / scenario_id
        scenario_dir.mkdir(parents=True, exist_ok=True)
        return scenario_dir / f"{tool_name}.json"

    def _save_result(self, scenario_id: str, tool_name: str, result: MergeResult):
        path = self._result_path(scenario_id, tool_name)
        path.write_text(json.dumps(_serialize_result(result), indent=2))

    def _load_cached(self, scenario_id: str, tool_name: str) -> MergeResult | None:
        path = self._result_path(scenario_id, tool_name)
        if path.exists():
            data = json.loads(path.read_text())
            return _deserialize_result(data)
        return None


def load_results(
    results_dir: str = "data/results",
) -> dict[str, dict[str, MergeResult]]:
    """Load previously saved results from disk."""
    path = Path(results_dir)
    results: dict[str, dict[str, MergeResult]] = {}

    for scenario_dir in sorted(path.iterdir()):
        if not scenario_dir.is_dir():
            continue
        scenario_id = scenario_dir.name
        results[scenario_id] = {}

        for result_file in scenario_dir.glob("*.json"):
            tool_name = result_file.stem
            data = json.loads(result_file.read_text())
            results[scenario_id][tool_name] = _deserialize_result(data)

    return results
