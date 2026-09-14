"""Tests for cli._classify_results — specifically the R2 change that derives
each scenario's category from its R1 RM2 tags (was the constant "unknown").

Docker-free: conftest.py forces MERGE_COMPARATOR_FORMATTER/AST_NORMALIZE off,
so `contents_match` is pure whitespace normalization with no subprocess.
"""
from src.cli import _classify_results
from src.core.interfaces import MergeOutcome, MergeResult, MergeScenario


def _scenario(sid, refactorings):
    return MergeScenario(
        scenario_id=sid,
        repo_name="r",
        merge_commit="m",
        file_path="Foo.java",
        base_content="base",
        ours_content="ours",
        theirs_content="theirs",
        developer_resolution="resolved",
        refactorings=refactorings,
    )


def _clean(content):
    return MergeResult(
        outcome=MergeOutcome.CLEAN,
        merged_content=content,
        conflict_count=0,
        runtime_seconds=0.1,
    )


def test_categories_derived_from_rm2_tags():
    scenarios = [
        _scenario("s_migrate", {"ours": ["Extract Method"], "theirs": []}),
        _scenario("s_untagged", {}),
        _scenario(
            "s_precedence",
            {"ours": ["Rename Method"], "theirs": ["Move Class"]},
        ),
    ]
    results = {
        "s_migrate": {"toolx": _clean("resolved")},
        "s_untagged": {"toolx": _clean("resolved")},
        "s_precedence": {"toolx": _clean("resolved")},
    }

    classifications, categories = _classify_results(results, scenarios)

    # Extract Method → MIGRATE_DECL.
    assert categories["s_migrate"] == "MIGRATE_DECL"
    # No refactorings field at all → NONE (honest: no signal), not "unknown".
    assert categories["s_untagged"] == "NONE"
    # Union across axes + precedence: {SYMBOL_CASCADE, CONTAINER_MOVE} →
    # SYMBOL_CASCADE outranks CONTAINER_MOVE.
    assert categories["s_precedence"] == "SYMBOL_CASCADE"

    # No category is ever the pre-R2 "unknown" sentinel.
    assert "unknown" not in set(categories.values())
    # Classifications still computed alongside categories.
    assert classifications["s_migrate"]["toolx"][0].value == "TP"


def test_missing_axis_key_defaults_to_empty_not_crash():
    # refactorings present but only one axis recorded — .get must not KeyError.
    scenarios = [_scenario("s", {"ours": ["Totally Unknown Type"]})]
    results = {"s": {"t": _clean("resolved")}}

    _, categories = _classify_results(results, scenarios)
    # Unknown/unmapped type → NONE (mirrors the runtime classifier).
    assert categories["s"] == "NONE"
