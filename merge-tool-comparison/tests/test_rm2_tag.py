"""Docker-free tests for the RM2 scenario tagger (Phase R1).

The Dockerized RM2 call is injected via the `runner` seam, so these tests run
without Docker. Integration against the real `merge-tools/refactoring-miner`
image is exercised separately by running `python tools/rm2_tag.py`.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import rm2_tag  # noqa: E402


def make_runner(by_right_content):
    """Fake RM2 runner keyed on the staged right-side file content.

    `tag_scenario` calls the runner once per axis with the *side* content on
    the right; keying on that content makes the fake order-independent.
    """
    calls = []

    def _runner(left: Path, right: Path):
        staged = next(right.iterdir())
        content = staged.read_text()
        calls.append(content)
        return by_right_content.get(content, (set(), None))

    _runner.calls = calls
    return _runner


def _scenario(sid="repo__abc__Foo_java", **overrides):
    s = {
        "scenario_id": sid,
        "repo_name": "repo",
        "merge_commit": "abc",
        "file_path": "src/main/java/Foo.java",
        "base_content": "BASE",
        "ours_content": "OURS",
        "theirs_content": "THEIRS",
        "developer_resolution": "RES",
        "category": "unknown",
    }
    s.update(overrides)
    return s


def _write(dir_path: Path, scenario: dict) -> Path:
    p = dir_path / f"{scenario['scenario_id']}.json"
    p.write_text(json.dumps(scenario, indent=2))
    return p


def test_rename_on_ours_only(tmp_path):
    _write(tmp_path, _scenario())
    runner = make_runner({"OURS": ({"Rename Method"}, None), "THEIRS": (set(), None)})
    summary = rm2_tag.process_scenarios(tmp_path, runner=runner)

    refs = json.loads(next(tmp_path.glob("*.json")).read_text())["refactorings"]
    assert refs == {"ours": ["Rename Method"], "theirs": []}
    assert summary["nonempty_ours"] == 1
    assert summary["nonempty_theirs"] == 0
    assert summary["axis_diverged"] == 1
    assert summary["both_empty"] == 0


def test_same_rename_both_branches(tmp_path):
    _write(tmp_path, _scenario())
    runner = make_runner(
        {"OURS": ({"Rename Method"}, None), "THEIRS": ({"Rename Method"}, None)}
    )
    rm2_tag.process_scenarios(tmp_path, runner=runner)

    refs = json.loads(next(tmp_path.glob("*.json")).read_text())["refactorings"]
    assert refs == {"ours": ["Rename Method"], "theirs": ["Rename Method"]}


def test_different_types_across_axes(tmp_path):
    _write(tmp_path, _scenario())
    runner = make_runner(
        {"OURS": ({"Extract Method"}, None), "THEIRS": ({"Rename Method"}, None)}
    )
    summary = rm2_tag.process_scenarios(tmp_path, runner=runner)

    refs = json.loads(next(tmp_path.glob("*.json")).read_text())["refactorings"]
    assert refs == {"ours": ["Extract Method"], "theirs": ["Rename Method"]}
    assert summary["axis_diverged"] == 1


def test_no_refactoring_on_any_axis(tmp_path):
    _write(tmp_path, _scenario())
    runner = make_runner({})  # everything → (empty, None)
    summary = rm2_tag.process_scenarios(tmp_path, runner=runner)

    refs = json.loads(next(tmp_path.glob("*.json")).read_text())["refactorings"]
    assert refs == {"ours": [], "theirs": []}
    assert summary["both_empty"] == 1
    assert summary["axis_diverged"] == 0


def test_cache_skip_when_already_tagged(tmp_path):
    _write(tmp_path, _scenario(refactorings={"ours": [], "theirs": ["Move Method"]}))

    def boom(left, right):
        raise AssertionError("runner must not be called for a cached scenario")

    summary = rm2_tag.process_scenarios(tmp_path, force=False, runner=boom)
    assert summary["skipped_cached"] == 1
    assert summary["tagged"] == 0
    # Cached tag is preserved and still reflected in the distribution counters.
    assert summary["nonempty_theirs"] == 1


def test_force_reextracts_tagged_scenario(tmp_path):
    _write(tmp_path, _scenario(refactorings={"ours": ["stale"], "theirs": ["stale"]}))
    runner = make_runner({"OURS": ({"Inline Method"}, None), "THEIRS": (set(), None)})
    summary = rm2_tag.process_scenarios(tmp_path, force=True, runner=runner)

    refs = json.loads(next(tmp_path.glob("*.json")).read_text())["refactorings"]
    assert refs == {"ours": ["Inline Method"], "theirs": []}
    assert summary["tagged"] == 1
    assert summary["skipped_cached"] == 0


def test_subprocess_error_is_fail_closed(tmp_path):
    _write(tmp_path, _scenario())
    runner = make_runner(
        {
            "OURS": ({"Rename Method"}, None),
            "THEIRS": (set(), "subprocess error: docker not found"),
        }
    )
    summary = rm2_tag.process_scenarios(tmp_path, runner=runner)

    refs = json.loads(next(tmp_path.glob("*.json")).read_text())["refactorings"]
    assert refs == {"ours": ["Rename Method"], "theirs": []}
    assert summary["errored_scenarios"] == 1
    assert "theirs" in summary["errors"][_scenario()["scenario_id"]]


def test_detect_axis_stages_basename_only(tmp_path, monkeypatch):
    """Mirrors R4a: file staged under its basename in a single-file dir."""
    seen = {}

    def spy(left: Path, right: Path):
        lf = next(left.iterdir())
        rf = next(right.iterdir())
        seen["left_name"] = lf.name
        seen["right_name"] = rf.name
        seen["left_text"] = lf.read_text()
        seen["right_text"] = rf.read_text()
        return {"Rename Class"}, None

    types, err = rm2_tag.detect_axis(
        "deep/pkg/path/Bar.java", "B", "O", runner=spy
    )
    assert err is None
    assert types == ["Rename Class"]
    assert seen["left_name"] == "Bar.java" == seen["right_name"]
    assert seen["left_text"] == "B" and seen["right_text"] == "O"


def test_is_tagged_predicate():
    assert rm2_tag._is_tagged({"refactorings": {"ours": [], "theirs": []}}) is True
    assert rm2_tag._is_tagged({"refactorings": {"ours": []}}) is False
    assert rm2_tag._is_tagged({}) is False
    assert rm2_tag._is_tagged({"refactorings": "nope"}) is False


# --- project-level mode (ISSUES #26) ------------------------------------
#
# Same Docker-free posture: the raw RM2 call is injected via `raw_runner`.
# The git-worktree machinery runs against a tiny real repo built in tmp_path.

import subprocess  # noqa: E402


def _make_merge_repo(tmp_path: Path) -> tuple[Path, str]:
    """Tiny clone with one merge commit: base → ours-parent + theirs-parent.

    Layout mirrors data/repos: repos_dir/<repo_name>. The merged file is
    src/Foo.java with contents BASE / OURS / THEIRS per tree, so a spy runner
    can identify which worktree it was handed.
    """
    repos_dir = tmp_path / "repos"
    repo = repos_dir / "repo"
    (repo / "src").mkdir(parents=True)

    def git(*args):
        subprocess.run(
            ["git", "-C", str(repo),
             "-c", "user.name=t", "-c", "user.email=t@t", *args],
            check=True, capture_output=True,
        )

    git("init", "-b", "main")
    (repo / "src" / "Foo.java").write_text("BASE")
    git("add", "."); git("commit", "-m", "base")
    git("checkout", "-b", "side")
    (repo / "src" / "Foo.java").write_text("THEIRS")
    git("commit", "-am", "theirs")
    git("checkout", "main")
    (repo / "src" / "Foo.java").write_text("OURS")
    git("commit", "-am", "ours")
    git("merge", "-s", "ours", "--no-edit", "side")
    merge_sha = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return repos_dir, merge_sha


def _payload(*entries):
    return {"refactorings": [
        {"type": t, "leftSideLocations": [{"filePath": fp}], "rightSideLocations": []}
        for t, fp in entries
    ]}


def test_types_in_same_file_filter():
    payload = _payload(
        ("Move Method", "src/Foo.java"),
        ("Extract Class", "other/Bar.java"),
    )
    assert rm2_tag.types_in(payload) == {"Move Method", "Extract Class"}
    assert rm2_tag.types_in(payload, "src/Foo.java") == {"Move Method"}
    assert rm2_tag.types_in(None, "src/Foo.java") == set()


def test_project_tag_worktrees_and_filter(tmp_path):
    """Worktrees staged at base + side parents; results same-file filtered."""
    repos_dir, merge_sha = _make_merge_repo(tmp_path)
    scen_dir = tmp_path / "scenarios"
    scen_dir.mkdir()
    _write(scen_dir, _scenario(
        repo_name="repo", merge_commit=merge_sha, file_path="src/Foo.java",
        refactorings={"ours": ["Rename Method"], "theirs": []},
    ))

    seen = []

    def spy(left: Path, right: Path, timeout=None):
        base = (left / "src" / "Foo.java").read_text()
        side = (right / "src" / "Foo.java").read_text()
        seen.append((base, side))
        if side == "OURS":
            return _payload(("Move Method", "src/Foo.java"),
                            ("Extract Class", "other/Bar.java")), None
        return _payload(("Rename Class", "src/Foo.java")), None

    summary = rm2_tag.process_scenarios_project(
        scen_dir, repos_dir=repos_dir, raw_runner=spy
    )
    s = json.loads(next(scen_dir.glob("*.json")).read_text())

    # Left tree is always the merge-base; right tree the side parent.
    assert seen == [("BASE", "OURS"), ("BASE", "THEIRS")]
    assert s[rm2_tag.PROJECT_KEY] == {"ours": ["Move Method"], "theirs": ["Rename Class"]}
    assert s[rm2_tag.PROJECT_FULL_KEY] == {
        "ours": ["Extract Class", "Move Method"], "theirs": ["Rename Class"],
    }
    # R1 file-level tags must be untouched.
    assert s["refactorings"] == {"ours": ["Rename Method"], "theirs": []}
    assert summary["tagged"] == 1
    assert summary["errored_scenarios"] == 0
    assert summary["axis_diverged"] == 1
    # No leftover worktrees on the clone.
    wt = subprocess.run(
        ["git", "-C", str(repos_dir / "repo"), "worktree", "list", "--porcelain"],
        capture_output=True, text=True,
    ).stdout
    assert wt.count("worktree ") == 1  # only the main checkout


def test_project_cache_skip_and_force(tmp_path):
    repos_dir, merge_sha = _make_merge_repo(tmp_path)
    scen_dir = tmp_path / "scenarios"
    scen_dir.mkdir()
    cached = {"ours": ["Move Method"], "theirs": []}
    _write(scen_dir, _scenario(
        repo_name="repo", merge_commit=merge_sha, file_path="src/Foo.java",
        **{rm2_tag.PROJECT_KEY: cached},
    ))

    def boom(left, right, timeout=None):
        raise AssertionError("raw_runner must not be called for a cached scenario")

    summary = rm2_tag.process_scenarios_project(
        scen_dir, repos_dir=repos_dir, raw_runner=boom
    )
    assert summary["skipped_cached"] == 1 and summary["tagged"] == 0
    assert summary["nonempty_ours"] == 1

    def fresh(left, right, timeout=None):
        return _payload(("Inline Method", "src/Foo.java")), None

    summary = rm2_tag.process_scenarios_project(
        scen_dir, repos_dir=repos_dir, force=True, raw_runner=fresh
    )
    s = json.loads(next(scen_dir.glob("*.json")).read_text())
    assert summary["tagged"] == 1
    assert s[rm2_tag.PROJECT_KEY] == {"ours": ["Inline Method"], "theirs": ["Inline Method"]}


def test_project_repo_missing_fail_closed(tmp_path):
    scen_dir = tmp_path / "scenarios"
    scen_dir.mkdir()
    _write(scen_dir, _scenario())

    def boom(left, right, timeout=None):
        raise AssertionError("raw_runner must not be called without a repo")

    summary = rm2_tag.process_scenarios_project(
        scen_dir, repos_dir=tmp_path / "repos", raw_runner=boom
    )
    s = json.loads(next(scen_dir.glob("*.json")).read_text())
    assert s[rm2_tag.PROJECT_KEY] == {"ours": [], "theirs": []}
    assert summary["errored_scenarios"] == 1
    errs = summary["errors"][_scenario()["scenario_id"]]
    assert "repo not found" in errs["ours"] and "repo not found" in errs["theirs"]


def test_project_rm2_error_fail_closed_per_axis(tmp_path):
    repos_dir, merge_sha = _make_merge_repo(tmp_path)
    scen_dir = tmp_path / "scenarios"
    scen_dir.mkdir()
    _write(scen_dir, _scenario(
        repo_name="repo", merge_commit=merge_sha, file_path="src/Foo.java",
    ))

    def flaky(left: Path, right: Path, timeout=None):
        if (right / "src" / "Foo.java").read_text() == "OURS":
            return _payload(("Move Method", "src/Foo.java")), None
        return None, "docker exit 1: boom"

    summary = rm2_tag.process_scenarios_project(
        scen_dir, repos_dir=repos_dir, raw_runner=flaky
    )
    s = json.loads(next(scen_dir.glob("*.json")).read_text())
    assert s[rm2_tag.PROJECT_KEY] == {"ours": ["Move Method"], "theirs": []}
    assert summary["errored_scenarios"] == 1
    assert "theirs" in summary["errors"][_scenario()["scenario_id"]]


def test_is_project_tagged_predicate():
    key = rm2_tag.PROJECT_KEY
    assert rm2_tag._is_project_tagged({key: {"ours": [], "theirs": []}}) is True
    assert rm2_tag._is_project_tagged({key: {"ours": []}}) is False
    assert rm2_tag._is_project_tagged({}) is False
    assert rm2_tag._is_project_tagged({key: "nope"}) is False
    # File-level tags alone don't count as project-tagged.
    assert rm2_tag._is_project_tagged({"refactorings": {"ours": [], "theirs": []}}) is False
