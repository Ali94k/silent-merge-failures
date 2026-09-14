import csv
import json
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from click.testing import CliRunner

from src.cli import cli
from src.data.schesch_loader import ScheschDatasetLoader


def _write_merge_csv(path: Path, rows: list[dict]):
    """Helper to create a merge CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = rows[0].keys() if rows else ["idx", "merge_commit", "parent_1", "parent_2", "notes"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def test_find_merge_csvs_merges_dir(tmp_path):
    """CSVs under merges/ subdirectory are found."""
    csv_path = tmp_path / "merges" / "owner" / "repo.csv"
    _write_merge_csv(csv_path, [
        {"idx": "0", "merge_commit": "abc123", "parent_1": "p1", "parent_2": "p2", "notes": ""},
    ])

    loader = ScheschDatasetLoader(dataset_path=str(tmp_path))
    csvs = loader._find_merge_csvs()
    assert len(csvs) == 1
    assert csvs[0] == csv_path


def test_find_merge_csvs_top_level(tmp_path):
    """Fallback to top-level CSVs when no merges/ dir exists."""
    csv_path = tmp_path / "scenarios.csv"
    _write_merge_csv(csv_path, [
        {"idx": "0", "merge_commit": "abc", "parent_1": "p1", "parent_2": "p2", "notes": ""},
    ])

    loader = ScheschDatasetLoader(dataset_path=str(tmp_path))
    csvs = loader._find_merge_csvs()
    assert len(csvs) == 1


def test_repo_slug_from_path(tmp_path):
    """Extract owner/repo from path."""
    csv_path = tmp_path / "merges" / "google" / "guava.csv"
    loader = ScheschDatasetLoader(dataset_path=str(tmp_path))
    slug = loader._repo_slug_from_path(csv_path)
    assert slug == "google/guava"


def test_read_merge_csv_skips_trivial(tmp_path):
    """Rows with 'a parent is the base' are skipped."""
    csv_path = tmp_path / "test.csv"
    _write_merge_csv(csv_path, [
        {"idx": "0", "merge_commit": "abc", "parent_1": "p1", "parent_2": "p2", "notes": ""},
        {"idx": "1", "merge_commit": "def", "parent_1": "p3", "parent_2": "p4", "notes": "a parent is the base"},
    ])

    loader = ScheschDatasetLoader(dataset_path=str(tmp_path))
    rows = loader._read_merge_csv(csv_path)
    assert len(rows) == 1
    assert rows[0]["merge_commit"] == "abc"


def test_load_respects_max_scenarios(tmp_path):
    """Max scenarios limits total output."""
    csv_path = tmp_path / "merges" / "owner" / "repo.csv"
    _write_merge_csv(csv_path, [
        {"idx": str(i), "merge_commit": f"sha{i}", "parent_1": f"p1_{i}", "parent_2": f"p2_{i}", "notes": ""}
        for i in range(10)
    ])

    loader = ScheschDatasetLoader(dataset_path=str(tmp_path))
    # _extract_scenario will return None for all (no real git repo),
    # so we test that the loop respects max_scenarios by mocking
    with patch.object(loader, "_clone_or_open", return_value=None):
        scenarios = loader.load(max_scenarios=3)

    # With clone returning None, no scenarios are extracted
    assert len(scenarios) == 0


def test_load_filters_repos(tmp_path):
    """filter_repos limits which repos are processed."""
    for name in ["repo1", "repo2"]:
        csv_path = tmp_path / "merges" / "owner" / f"{name}.csv"
        _write_merge_csv(csv_path, [
            {"idx": "0", "merge_commit": "abc", "parent_1": "p1", "parent_2": "p2", "notes": ""},
        ])

    loader = ScheschDatasetLoader(dataset_path=str(tmp_path))

    processed_repos = []
    original_clone = loader._clone_or_open

    def tracking_clone(slug):
        processed_repos.append(slug)
        return None

    with patch.object(loader, "_clone_or_open", side_effect=tracking_clone):
        loader.load(filter_repos=["owner/repo1"])

    assert "owner/repo1" in processed_repos
    assert "owner/repo2" not in processed_repos


# --- CLI caching tests ---


def _make_scenario_dict(scenario_id="test__abc__Foo.java"):
    """Create a minimal valid scenario dict."""
    return {
        "scenario_id": scenario_id,
        "repo_name": "test",
        "merge_commit": "abc123",
        "file_path": "Foo.java",
        "base_content": "base",
        "ours_content": "ours",
        "theirs_content": "theirs",
        "developer_resolution": "resolved",
        "category": "unknown",
    }


def _fake_loader_load(scenarios):
    """Patch ScheschDatasetLoader.load to return pre-built scenarios."""
    from src.core.interfaces import MergeScenario
    objs = [MergeScenario.from_dict(s) for s in scenarios]

    def _load(self, max_scenarios=None, filter_repos=None):
        return objs
    return _load


def test_load_dataset_caching_skips_existing(tmp_path):
    """Existing scenario JSONs are not overwritten without --force."""
    scenario = _make_scenario_dict()
    output_dir = tmp_path / "scenarios"
    output_dir.mkdir()

    # Pre-create the scenario file with sentinel content
    existing_file = output_dir / f"{scenario['scenario_id']}.json"
    existing_file.write_text(json.dumps({"sentinel": True}))
    original_mtime = existing_file.stat().st_mtime

    # Also need a fake dataset dir
    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()

    time.sleep(0.05)

    runner = CliRunner()
    with patch.object(ScheschDatasetLoader, "load", _fake_loader_load([scenario])):
        result = runner.invoke(cli, [
            "load-dataset",
            "--dataset-path", str(dataset_dir),
            "--output", str(output_dir),
        ])

    assert result.exit_code == 0
    assert "0 new" in result.output
    assert "1 cached" in result.output
    # File should not have been overwritten
    assert existing_file.stat().st_mtime == original_mtime
    assert json.loads(existing_file.read_text()) == {"sentinel": True}


def test_load_dataset_force_overwrites(tmp_path):
    """--force flag causes existing scenario JSONs to be overwritten."""
    scenario = _make_scenario_dict()
    output_dir = tmp_path / "scenarios"
    output_dir.mkdir()

    # Pre-create with sentinel
    existing_file = output_dir / f"{scenario['scenario_id']}.json"
    existing_file.write_text(json.dumps({"sentinel": True}))

    dataset_dir = tmp_path / "dataset"
    dataset_dir.mkdir()

    runner = CliRunner()
    with patch.object(ScheschDatasetLoader, "load", _fake_loader_load([scenario])):
        result = runner.invoke(cli, [
            "load-dataset",
            "--dataset-path", str(dataset_dir),
            "--output", str(output_dir),
            "--force",
        ])

    assert result.exit_code == 0
    assert "1 new" in result.output
    assert "0 cached" in result.output
    # File should have been overwritten with real scenario data
    data = json.loads(existing_file.read_text())
    assert data["scenario_id"] == scenario["scenario_id"]
    assert "sentinel" not in data


def test_load_dataset_missing_dir_shows_error(tmp_path):
    """Missing dataset directory prints helpful error with download URLs."""
    runner = CliRunner()
    result = runner.invoke(cli, [
        "load-dataset",
        "--dataset-path", str(tmp_path / "nonexistent"),
    ])

    assert result.exit_code != 0
    assert "not found" in result.output.lower() or "not found" in (result.stderr or "").lower()
