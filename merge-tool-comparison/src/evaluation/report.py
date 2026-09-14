import csv
import json
from io import StringIO
from pathlib import Path

from tabulate import tabulate

from src.evaluation.metrics import ToolMetrics


COLUMNS = [
    "tool", "category", "scenarios", "tp", "fp", "tn", "fn",
    "crashes", "timeouts",
    "precision", "precision_ci_low", "precision_ci_high",
    "recall", "recall_ci_low", "recall_ci_high", "f1",
    "incorrect_rate", "weighted_cost", "avg_runtime_s",
]

# Classification cell values for the per-scenario pivot (ISSUES #9).
_OUTCOME_ORDER = ["TP", "FP", "TN", "FN", "CRASH", "TIMEOUT"]


def to_table(metrics: list[ToolMetrics], fmt: str = "grid") -> str:
    """Render metrics as a formatted table."""
    rows = [m.to_dict() for m in metrics]
    headers = {col: col for col in COLUMNS}
    return tabulate(
        [_row_values(r) for r in rows],
        headers=COLUMNS,
        tablefmt=fmt,
        floatfmt=".4f",
    )


def to_csv(metrics: list[ToolMetrics], output_path: str | None = None) -> str:
    """Export metrics as CSV. Returns CSV string and optionally writes to file."""
    rows = [m.to_dict() for m in metrics]
    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row[k] for k in COLUMNS})
    content = buf.getvalue()

    if output_path:
        Path(output_path).write_text(content)

    return content


def to_json(metrics: list[ToolMetrics], output_path: str | None = None) -> str:
    """Export metrics as JSON."""
    data = [m.to_dict() for m in metrics]
    content = json.dumps(data, indent=2)

    if output_path:
        Path(output_path).write_text(content)

    return content


def to_latex(metrics: list[ToolMetrics], output_path: str | None = None) -> str:
    """Export metrics as LaTeX booktabs table."""
    rows = [m.to_dict() for m in metrics]
    content = tabulate(
        [_row_values(r) for r in rows],
        headers=COLUMNS,
        tablefmt="latex_booktabs",
        floatfmt=".4f",
    )

    if output_path:
        Path(output_path).write_text(content)

    return content


def to_per_scenario(
    classifications: dict[str, dict[str, tuple]],
    output_path: str | None = None,
) -> str:
    """Per-scenario pivot (ISSUES #9): rows = scenarios, cols = tools,
    cells = Classification value. Enables qualitative failure-pattern analysis
    that the aggregate table cannot support.

    `classifications` is the compute_metrics() input shape:
    {scenario_id: {tool_name: (Classification, runtime)}}.
    """
    tools = sorted({t for per_tool in classifications.values() for t in per_tool})
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerow(["scenario_id", *tools])
    for sid in sorted(classifications):
        per_tool = classifications[sid]
        writer.writerow([sid, *[
            per_tool[t][0].value if t in per_tool else "" for t in tools
        ]])
    content = buf.getvalue()

    if output_path:
        Path(output_path).write_text(content)

    return content


def to_charts(
    metrics: list[ToolMetrics],
    classifications: dict[str, dict[str, tuple]] | None = None,
    output_dir: str = "reports",
) -> list[str]:
    """Chart pack (ISSUES #4), written as PDFs into output_dir. Returns the
    list of files written. Requires the `viz` extra (matplotlib); returns []
    with a notice if it is not installed — chart generation is optional and
    must never break tabular reporting.

    Charts are rendered from already-computed metrics/classifications, so they
    can be (re)generated on any machine from the CSVs' source data — no tool
    execution, no scoring, no environment sensitivity.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")  # headless; no display needed
        import matplotlib.pyplot as plt
    except ImportError:
        print("charts: matplotlib not installed — `pip install -e .[viz]`; skipping.")
        return []

    overall = sorted((m for m in metrics if m.category == "all"),
                     key=lambda m: m.tool_name)
    if not overall:
        return []
    names = [m.tool_name for m in overall]
    written: list[str] = []
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    def _save(fig, fname: str) -> None:
        path = out / fname
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        written.append(str(path))

    # 1. F1 per tool
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(names, [m.f1 for m in overall], color="#4878a8")
    ax.set_ylabel("F1")
    ax.set_ylim(0, 1.05)
    ax.set_title(f"F1 per tool (n={overall[0].scenario_count} scenarios)")
    ax.tick_params(axis="x", rotation=20)
    _save(fig, "chart_f1.pdf")

    # 2. Precision with Wilson 95% CI error bars (ISSUES #5 made visible)
    fig, ax = plt.subplots(figsize=(7, 4))
    prec = [m.precision for m in overall]
    # clamp at 0: float error can put a Wilson bound past the point estimate
    # by ~1e-17, and matplotlib rejects negative yerr outright
    err_lo = [max(0.0, m.precision - m.precision_ci[0]) for m in overall]
    err_hi = [max(0.0, m.precision_ci[1] - m.precision) for m in overall]
    ax.bar(names, prec, color="#6a9a58", yerr=[err_lo, err_hi], capsize=4)
    ax.set_ylabel("precision (Wilson 95% CI)")
    ax.set_ylim(0, 1.05)
    ax.set_title("Precision per tool with Wilson 95% CI")
    ax.tick_params(axis="x", rotation=20)
    _save(fig, "chart_precision_ci.pdf")

    # 3. Stacked outcome counts
    fig, ax = plt.subplots(figsize=(7, 4))
    stacks = {
        "TP": ([m.tp for m in overall], "#6a9a58"),
        "FP": ([m.fp for m in overall], "#b04a4a"),
        "TN": ([m.tn for m in overall], "#4878a8"),
        "FN": ([m.fn for m in overall], "#c8a04a"),
        "CRASH+TIMEOUT": ([m.crashes + m.timeouts for m in overall], "#777777"),
    }
    bottom = [0] * len(overall)
    for label, (vals, color) in stacks.items():
        ax.bar(names, vals, bottom=bottom, label=label, color=color)
        bottom = [b + v for b, v in zip(bottom, vals)]
    ax.set_ylabel("scenarios")
    ax.set_title("Outcome breakdown per tool")
    ax.legend(fontsize=8)
    ax.tick_params(axis="x", rotation=20)
    _save(fig, "chart_outcomes.pdf")

    # 4. Runtime (log scale — spans native-git ms to Docker-tool tens of s)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(names, [max(m.avg_runtime, 1e-3) for m in overall], color="#8a6aa0")
    ax.set_yscale("log")
    ax.set_ylabel("avg runtime per scenario (s, log)")
    ax.set_title("Average runtime per tool")
    ax.tick_params(axis="x", rotation=20)
    _save(fig, "chart_runtime.pdf")

    # 5. Per-scenario heatmap (needs classifications)
    if classifications:
        tools = sorted({t for pt in classifications.values() for t in pt})
        sids = sorted(classifications)
        cmap = {"TP": 0, "FP": 1, "TN": 2, "FN": 3, "CRASH": 4, "TIMEOUT": 4}
        grid = [[cmap.get(classifications[s][t][0].value, 5) if t in classifications[s]
                 else 5 for t in tools] for s in sids]
        from matplotlib.colors import ListedColormap
        colors = ListedColormap(
            ["#6a9a58", "#b04a4a", "#4878a8", "#c8a04a", "#777777", "#eeeeee"])
        fig, ax = plt.subplots(figsize=(max(4, len(tools) * 1.2),
                                        max(4, len(sids) * 0.12)))
        ax.imshow(grid, aspect="auto", cmap=colors, vmin=0, vmax=5)
        ax.set_xticks(range(len(tools)), tools, rotation=30, ha="right", fontsize=7)
        ax.set_yticks([])
        ax.set_ylabel(f"{len(sids)} scenarios")
        ax.set_title("Per-scenario outcome (green TP / red FP / blue TN / "
                     "yellow FN / gray crash)")
        _save(fig, "chart_per_scenario_heatmap.pdf")

    return written


def generate_report(
    metrics: list[ToolMetrics],
    formats: list[str],
    output_dir: str = "reports",
    classifications: dict[str, dict[str, tuple]] | None = None,
) -> dict[str, str]:
    """Generate reports in requested formats. Returns {format: content}.

    `classifications` (the compute_metrics() input) is required by the
    "per-scenario" and "charts" heatmap formats; those degrade gracefully
    without it.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    results = {}

    for fmt in formats:
        match fmt:
            case "console":
                results["console"] = to_table(metrics)
            case "csv":
                results["csv"] = to_csv(metrics, f"{output_dir}/results.csv")
            case "json":
                results["json"] = to_json(metrics, f"{output_dir}/results.json")
            case "latex":
                results["latex"] = to_latex(metrics, f"{output_dir}/results.tex")
            case "per-scenario":
                if classifications is None:
                    print("per-scenario: classifications not provided; skipping.")
                else:
                    results["per-scenario"] = to_per_scenario(
                        classifications, f"{output_dir}/per_scenario.csv")
            case "charts":
                results["charts"] = "\n".join(
                    to_charts(metrics, classifications, output_dir))

    return results


def _row_values(row: dict) -> list:
    return [row[col] for col in COLUMNS]
