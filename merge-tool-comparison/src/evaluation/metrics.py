import math
from dataclasses import dataclass, field
from collections import defaultdict

from src.evaluation.comparator import Classification


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    """(point, lo, hi) Wilson score interval for k successes in n trials.

    Same formula as tools/detect_validate.py::wilson — duplicated here rather
    than imported because src/ must not depend on tools/ (ISSUES #5).
    """
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / den
    return (p, max(0.0, center - half), min(1.0, center + half))


@dataclass
class ToolMetrics:
    tool_name: str
    category: str = "all"
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0
    crashes: int = 0
    timeouts: int = 0
    total_runtime: float = 0.0
    scenario_count: int = 0

    @property
    def precision(self) -> float:
        denom = self.tp + self.fp
        return self.tp / denom if denom > 0 else 0.0

    @property
    def recall(self) -> float:
        denom = self.tp + self.fn
        return self.tp / denom if denom > 0 else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

    @property
    def precision_ci(self) -> tuple[float, float]:
        """Wilson 95% CI (lo, hi) on precision; (0, 0) when undefined (n=0)."""
        _, lo, hi = wilson(self.tp, self.tp + self.fp)
        return (lo, hi)

    @property
    def recall_ci(self) -> tuple[float, float]:
        """Wilson 95% CI (lo, hi) on recall; (0, 0) when undefined (n=0)."""
        _, lo, hi = wilson(self.tp, self.tp + self.fn)
        return (lo, hi)

    @property
    def avg_runtime(self) -> float:
        return self.total_runtime / self.scenario_count if self.scenario_count > 0 else 0.0

    @property
    def incorrect_merge_rate(self) -> float:
        """Rate of silent incorrect merges (FP / total clean merges)."""
        clean_total = self.tp + self.fp
        return self.fp / clean_total if clean_total > 0 else 0.0

    def weighted_cost(
        self,
        correct_weight: float = 0.0,
        incorrect_weight: float = 10.0,
        unhandled_weight: float = 1.0,
        crash_weight: float = 1.0,
    ) -> float:
        """Compute weighted cost following Schesch et al. cost model.

        Args:
            correct_weight: Cost of TP (correct clean merge) — typically 0.
            incorrect_weight: Cost of FP (silent wrong merge) — high.
            unhandled_weight: Cost of FN/TN (conflict reported) — moderate.
            crash_weight: Cost of CRASH/TIMEOUT — same as unhandled.
        """
        return (
            self.tp * correct_weight
            + self.fp * incorrect_weight
            + (self.fn + self.tn) * unhandled_weight
            + (self.crashes + self.timeouts) * crash_weight
        )

    def add_classification(self, cls: Classification, runtime: float):
        self.scenario_count += 1
        self.total_runtime += runtime
        match cls:
            case Classification.TRUE_POSITIVE:
                self.tp += 1
            case Classification.FALSE_POSITIVE:
                self.fp += 1
            case Classification.TRUE_NEGATIVE:
                self.tn += 1
            case Classification.FALSE_NEGATIVE:
                self.fn += 1
            case Classification.CRASH:
                self.crashes += 1
            case Classification.TIMEOUT:
                self.timeouts += 1

    def to_dict(self) -> dict:
        return {
            "tool": self.tool_name,
            "category": self.category,
            "tp": self.tp,
            "fp": self.fp,
            "tn": self.tn,
            "fn": self.fn,
            "crashes": self.crashes,
            "timeouts": self.timeouts,
            "precision": round(self.precision, 4),
            "precision_ci_low": round(self.precision_ci[0], 4),
            "precision_ci_high": round(self.precision_ci[1], 4),
            "recall": round(self.recall, 4),
            "recall_ci_low": round(self.recall_ci[0], 4),
            "recall_ci_high": round(self.recall_ci[1], 4),
            "f1": round(self.f1, 4),
            "avg_runtime_s": round(self.avg_runtime, 3),
            "incorrect_rate": round(self.incorrect_merge_rate, 4),
            "weighted_cost": round(self.weighted_cost(), 2),
            "scenarios": self.scenario_count,
        }


def compute_metrics(
    classifications: dict[str, dict[str, tuple[Classification, float]]],
    scenarios_categories: dict[str, str] | None = None,
) -> list[ToolMetrics]:
    """
    Compute metrics from classification results.

    Args:
        classifications: {scenario_id: {tool_name: (Classification, runtime)}}
        scenarios_categories: {scenario_id: category} for per-category breakdown

    Returns:
        List of ToolMetrics (one per tool overall + one per tool-category pair).
    """
    # Aggregate per tool (overall)
    tool_metrics: dict[str, ToolMetrics] = {}
    # Aggregate per (tool, category)
    category_metrics: dict[tuple[str, str], ToolMetrics] = {}
    distinct_categories: set[str] = set()

    for scenario_id, tool_results in classifications.items():
        category = (scenarios_categories or {}).get(scenario_id, "unknown")
        distinct_categories.add(category)

        for tool_name, (cls, runtime) in tool_results.items():
            # Overall
            if tool_name not in tool_metrics:
                tool_metrics[tool_name] = ToolMetrics(tool_name=tool_name, category="all")
            tool_metrics[tool_name].add_classification(cls, runtime)

            # Per category
            key = (tool_name, category)
            if key not in category_metrics:
                category_metrics[key] = ToolMetrics(tool_name=tool_name, category=category)
            category_metrics[key].add_classification(cls, runtime)

    results = list(tool_metrics.values())
    # Emit per-(tool, category) rows only when the pivot is non-degenerate.
    # With a single distinct category (all "unknown" before R1 tags, or all
    # "NONE"), every per-category row byte-duplicates its "all" row — that is
    # exactly ISSUES.md #23. The pivot is meaningful only with >=2 categories.
    if len(distinct_categories) > 1:
        results += list(category_metrics.values())
    results.sort(key=lambda m: (m.tool_name, m.category))
    return results
