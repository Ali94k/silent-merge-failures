from src.evaluation.comparator import Classification
from src.evaluation.metrics import ToolMetrics, compute_metrics


def test_tool_metrics_precision_recall():
    m = ToolMetrics(tool_name="test")
    m.add_classification(Classification.TRUE_POSITIVE, 0.1)
    m.add_classification(Classification.TRUE_POSITIVE, 0.2)
    m.add_classification(Classification.FALSE_POSITIVE, 0.1)
    m.add_classification(Classification.FALSE_NEGATIVE, 0.1)

    assert m.tp == 2
    assert m.fp == 1
    assert m.fn == 1
    assert m.precision == 2 / 3
    assert m.recall == 2 / 3
    assert m.scenario_count == 4


def test_tool_metrics_empty():
    m = ToolMetrics(tool_name="empty")
    assert m.precision == 0.0
    assert m.recall == 0.0
    assert m.f1 == 0.0
    assert m.avg_runtime == 0.0
    assert m.incorrect_merge_rate == 0.0
    assert m.weighted_cost() == 0.0


def test_incorrect_merge_rate():
    m = ToolMetrics(tool_name="test")
    m.add_classification(Classification.TRUE_POSITIVE, 0.1)
    m.add_classification(Classification.TRUE_POSITIVE, 0.1)
    m.add_classification(Classification.FALSE_POSITIVE, 0.1)
    # 1 FP out of 3 clean merges (2 TP + 1 FP)
    assert abs(m.incorrect_merge_rate - 1 / 3) < 1e-9


def test_weighted_cost():
    m = ToolMetrics(tool_name="test")
    m.add_classification(Classification.TRUE_POSITIVE, 0.1)   # correct=0
    m.add_classification(Classification.FALSE_POSITIVE, 0.1)   # incorrect=10
    m.add_classification(Classification.TRUE_NEGATIVE, 0.1)    # unhandled=1
    m.add_classification(Classification.FALSE_NEGATIVE, 0.1)   # unhandled=1
    m.add_classification(Classification.CRASH, 0.1)            # crash=1

    # Default weights: correct=0, incorrect=10, unhandled=1, crash=1
    expected = 0 + 10 + 1 + 1 + 1
    assert m.weighted_cost() == expected

    # Custom weights
    assert m.weighted_cost(correct_weight=1.0, incorrect_weight=5.0,
                           unhandled_weight=2.0, crash_weight=3.0) == 1 + 5 + 4 + 3


def test_compute_metrics():
    classifications = {
        "scenario_1": {
            "tool_a": (Classification.TRUE_POSITIVE, 0.5),
            "tool_b": (Classification.FALSE_POSITIVE, 1.0),
        },
        "scenario_2": {
            "tool_a": (Classification.TRUE_NEGATIVE, 0.3),
            "tool_b": (Classification.TRUE_POSITIVE, 0.8),
        },
    }

    metrics = compute_metrics(classifications)
    overall = [m for m in metrics if m.category == "all"]
    assert len(overall) == 2

    tool_a = next(m for m in overall if m.tool_name == "tool_a")
    assert tool_a.tp == 1
    assert tool_a.tn == 1
    assert tool_a.scenario_count == 2


def test_single_category_emits_no_duplicate_rows():
    """ISSUES #23: a degenerate (single-category) pivot must not duplicate
    the 'all' rows with an identical per-category row."""
    classifications = {
        "s1": {"tool_a": (Classification.TRUE_POSITIVE, 0.1)},
        "s2": {"tool_a": (Classification.FALSE_POSITIVE, 0.1)},
    }
    # No categories supplied → every scenario defaults to the single
    # "unknown" bucket (the pre-R1 situation that produced #23).
    metrics = compute_metrics(classifications)
    assert [m.category for m in metrics] == ["all"]

    # Explicit but still single-category (e.g. all "NONE") — same guard.
    one_cat = compute_metrics(classifications, {"s1": "NONE", "s2": "NONE"})
    assert [m.category for m in one_cat] == ["all"]


def test_multi_category_emits_pivot_rows():
    """>=2 distinct categories → 'all' rows plus genuine per-cluster rows,
    with no row that byte-duplicates 'all'."""
    classifications = {
        "s1": {"tool_a": (Classification.TRUE_POSITIVE, 0.1)},
        "s2": {"tool_a": (Classification.FALSE_POSITIVE, 0.1)},
    }
    metrics = compute_metrics(
        classifications, {"s1": "MIGRATE_DECL", "s2": "NONE"}
    )
    cats = sorted(m.category for m in metrics)
    assert cats == ["MIGRATE_DECL", "NONE", "all"]

    all_row = next(m for m in metrics if m.category == "all")
    migrate = next(m for m in metrics if m.category == "MIGRATE_DECL")
    none_row = next(m for m in metrics if m.category == "NONE")
    assert all_row.tp == 1 and all_row.fp == 1 and all_row.scenario_count == 2
    assert migrate.tp == 1 and migrate.fp == 0 and migrate.scenario_count == 1
    assert none_row.tp == 0 and none_row.fp == 1 and none_row.scenario_count == 1
