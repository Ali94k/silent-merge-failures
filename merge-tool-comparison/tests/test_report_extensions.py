"""P4 reporting extensions: Wilson CIs (#5), per-scenario pivot (#9),
charts (#4). Docker-free; charts tests skip when matplotlib is absent."""
from __future__ import annotations

import csv
import io

import pytest

from src.evaluation.comparator import Classification
from src.evaluation.metrics import ToolMetrics, compute_metrics, wilson
from src.evaluation.report import (
    COLUMNS, generate_report, to_csv, to_per_scenario,
)


# --------------------------------------------------------------------------- #
# wilson() — golden values
# --------------------------------------------------------------------------- #
def test_wilson_golden_values():
    p, lo, hi = wilson(8, 10)
    assert p == pytest.approx(0.8)
    assert lo == pytest.approx(0.4901, abs=1e-3)
    assert hi == pytest.approx(0.9433, abs=1e-3)


def test_wilson_edges():
    assert wilson(0, 0) == (0.0, 0.0, 0.0)
    p, lo, hi = wilson(10, 10)          # perfect score still has lo < 1
    assert p == 1.0 and lo < 1.0 and hi == 1.0
    p, lo, hi = wilson(0, 10)           # zero score still has hi > 0
    assert p == 0.0 and lo == 0.0 and hi > 0.0


def test_metrics_ci_properties_and_dict():
    m = ToolMetrics(tool_name="t", tp=8, fp=2, fn=0)
    lo, hi = m.precision_ci
    assert (lo, hi) == pytest.approx((0.4901, 0.9433), abs=1e-3)
    d = m.to_dict()
    for k in ("precision_ci_low", "precision_ci_high",
              "recall_ci_low", "recall_ci_high"):
        assert k in d
    assert d["precision_ci_low"] == pytest.approx(0.4901, abs=1e-3)


def test_csv_has_ci_columns():
    m = ToolMetrics(tool_name="t", tp=8, fp=2)
    content = to_csv([m])
    header = content.splitlines()[0].split(",")
    assert header == COLUMNS
    assert "precision_ci_low" in header and "recall_ci_high" in header


# --------------------------------------------------------------------------- #
# per-scenario pivot (#9)
# --------------------------------------------------------------------------- #
def _classifications():
    return {
        "scn_b": {"toolA": (Classification.TRUE_POSITIVE, 0.1),
                  "toolB": (Classification.FALSE_POSITIVE, 2.0)},
        "scn_a": {"toolA": (Classification.CRASH, 0.0)},  # toolB missing here
    }


def test_per_scenario_pivot_shape_and_cells():
    content = to_per_scenario(_classifications())
    rows = list(csv.reader(io.StringIO(content)))
    assert rows[0] == ["scenario_id", "toolA", "toolB"]
    assert rows[1] == ["scn_a", "CRASH", ""]      # sorted; missing tool = empty
    assert rows[2] == ["scn_b", "TP", "FP"]


def test_generate_report_per_scenario_writes_file(tmp_path):
    m = compute_metrics(_classifications())
    out = generate_report(m, ["per-scenario"], str(tmp_path),
                          classifications=_classifications())
    assert "per-scenario" in out
    assert (tmp_path / "per_scenario.csv").exists()


def test_generate_report_per_scenario_skips_without_classifications(tmp_path, capsys):
    m = compute_metrics(_classifications())
    out = generate_report(m, ["per-scenario"], str(tmp_path))
    assert "per-scenario" not in out
    assert "skipping" in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# charts (#4) — smoke; skip without matplotlib
# --------------------------------------------------------------------------- #
def test_charts_smoke(tmp_path):
    pytest.importorskip("matplotlib")
    from src.evaluation.report import to_charts
    m = compute_metrics(_classifications())
    written = to_charts(m, _classifications(), str(tmp_path))
    names = {p.split("/")[-1] for p in written}
    assert {"chart_f1.pdf", "chart_precision_ci.pdf", "chart_outcomes.pdf",
            "chart_runtime.pdf", "chart_per_scenario_heatmap.pdf"} <= names
    for p in written:
        assert (tmp_path / p.split("/")[-1]).stat().st_size > 0


def test_charts_graceful_without_matplotlib(tmp_path, monkeypatch, capsys):
    """Simulate missing matplotlib regardless of the local env."""
    import builtins
    real_import = builtins.__import__

    def fake_import(name, *a, **kw):
        if name.startswith("matplotlib"):
            raise ImportError("no matplotlib")
        return real_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    from src.evaluation.report import to_charts
    m = [ToolMetrics(tool_name="t", tp=1)]
    assert to_charts(m, None, str(tmp_path)) == []
    assert "skipping" in capsys.readouterr().out
