from src.core.interfaces import MergeOutcome, MergeResult, MergeScenario


def test_merge_result_is_clean():
    result = MergeResult(
        outcome=MergeOutcome.CLEAN,
        merged_content="merged",
        conflict_count=0,
        runtime_seconds=0.1,
    )
    assert result.is_clean is True


def test_merge_result_not_clean():
    result = MergeResult(
        outcome=MergeOutcome.CONFLICT,
        merged_content="conflict",
        conflict_count=1,
        runtime_seconds=0.1,
    )
    assert result.is_clean is False


def test_merge_scenario_roundtrip():
    scenario = MergeScenario(
        scenario_id="test__abc123__Foo_java",
        repo_name="test",
        merge_commit="abc123",
        file_path="Foo.java",
        base_content="base",
        ours_content="ours",
        theirs_content="theirs",
        developer_resolution="resolved",
        category="test_category",
    )
    data = scenario.to_dict()
    restored = MergeScenario.from_dict(data)
    assert restored.scenario_id == scenario.scenario_id
    assert restored.category == "test_category"
    assert restored.developer_resolution == "resolved"


def test_merge_scenario_refactorings_roundtrip():
    scenario = MergeScenario(
        scenario_id="r__s__F_java",
        repo_name="r",
        merge_commit="s",
        file_path="F.java",
        base_content="b",
        ours_content="o",
        theirs_content="t",
        developer_resolution="d",
        refactorings={"ours": ["Rename Method"], "theirs": []},
    )
    data = scenario.to_dict()
    assert data["refactorings"] == {"ours": ["Rename Method"], "theirs": []}
    restored = MergeScenario.from_dict(data)
    assert restored.refactorings == {"ours": ["Rename Method"], "theirs": []}


def test_merge_scenario_defaults_and_unknown_keys_tolerated():
    # Legacy JSON (no refactorings key) loads with the empty-dict default.
    legacy = {
        "scenario_id": "r__s__F_java",
        "repo_name": "r",
        "merge_commit": "s",
        "file_path": "F.java",
        "base_content": "b",
        "ours_content": "o",
        "theirs_content": "t",
        "developer_resolution": "d",
        "category": "unknown",
        "some_future_key": "ignored",  # must not raise
    }
    restored = MergeScenario.from_dict(legacy)
    assert restored.refactorings == {}
    assert restored.category == "unknown"
    assert not hasattr(restored, "some_future_key")
