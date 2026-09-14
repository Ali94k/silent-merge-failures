"""Stage-A detection-validation harness tests (tools/detect_validate.py +
the semantic/semantic_ctl selection criteria in tools/select_materialize.py).

Docker-free: detector subprocess failures are monkeypatched (the
test_fail_closed.py pattern from the driver suite). The one live-Joern test
skips when joern-parse is not on PATH (image-gated test pattern).
"""
from __future__ import annotations

import subprocess
import sys
import shutil
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import detect_validate as dv  # noqa: E402
import select_materialize as sm  # noqa: E402

from core.interfaces import AnalysisResult, Issue  # noqa: E402  (driver pkg)


# --------------------------------------------------------------------------- #
# criterion selection
# --------------------------------------------------------------------------- #
def _row(mergiraf="Tests_passed", nif="2"):
    return {"mergiraf": mergiraf, "num_intersecting_files": nif}


def test_semantic_keeps_only_tests_failed():
    assert sm._semantic(_row(mergiraf="Tests_failed"))
    assert not sm._semantic(_row(mergiraf="Tests_passed"))
    assert not sm._semantic(_row(mergiraf="Merge_failed"))
    assert not sm._semantic({})


def test_semantic_ctl_keeps_only_tests_passed():
    assert sm._semantic_ctl(_row(mergiraf="Tests_passed"))
    assert not sm._semantic_ctl(_row(mergiraf="Tests_failed"))
    assert not sm._semantic_ctl(_row(mergiraf="Merge_failed"))
    assert not sm._semantic_ctl({})


def test_intersect_filter_inactive_when_unset():
    assert sm._intersect_ok(_row(nif="999"), None)
    assert sm._intersect_ok({}, None)


def test_intersect_filter_bounds_and_unparseable():
    assert sm._intersect_ok(_row(nif="2"), 3)
    assert sm._intersect_ok(_row(nif="3.0"), 3)  # float-formatted CSV value
    assert not sm._intersect_ok(_row(nif="4"), 3)
    assert not sm._intersect_ok(_row(nif=""), 3)  # unknown count fails active filter
    assert not sm._intersect_ok({}, 3)


# --------------------------------------------------------------------------- #
# verdict classification
# --------------------------------------------------------------------------- #
def _issue(msg, line=1):
    return Issue(line_number=line, severity="CRITICAL", message=msg, strategy_name="x")


def test_verdict_clean():
    assert dv.verdict_of(AnalysisResult(is_clean=True, issues=[])) == "CLEAN"


def test_verdict_flag_on_genuine_issue():
    res = AnalysisResult(is_clean=False, issues=[_issue("Potential stale read: ...")])
    assert dv.verdict_of(res) == "FLAG"


def test_verdict_unanalyzable_on_fail_closed():
    res = AnalysisResult(
        is_clean=False,
        issues=[_issue("Joern analysis inconclusive: joern-parse failed", line=0)],
    )
    assert dv.verdict_of(res) == "UNANALYZABLE"


def test_verdict_genuine_wins_over_inconclusive_if_mixed():
    res = AnalysisResult(is_clean=False, issues=[
        _issue("analysis inconclusive: x", line=0),
        _issue("Potential stale read", line=7),
    ])
    assert dv.verdict_of(res) == "FLAG"


# --------------------------------------------------------------------------- #
# UNANALYZABLE on subprocess failure — all four detectors, driver-faithful
# invocation through run_detector (test_fail_closed.py monkeypatch pattern)
# --------------------------------------------------------------------------- #
SCN = {
    "base_content": "class A {}\n",
    "ours_content": "class A { int x; }\n",
    "theirs_content": "class A { int y; }\n",
}


@pytest.mark.parametrize("name,strategy,mode", dv.DETECTORS,
                         ids=[d[0] for d in dv.DETECTORS])
def test_unanalyzable_on_subprocess_failure(name, strategy, mode, tmp_path, monkeypatch):
    def raise_cpe(*args, **kwargs):
        raise subprocess.CalledProcessError(returncode=1, cmd="joern-parse")

    monkeypatch.setattr(subprocess, "run", raise_cpe)
    merged = tmp_path / "Foo.java"
    merged.write_text("class Foo {}\n")

    rec = dv.run_detector(name, strategy, mode, str(merged), SCN)

    assert rec["verdict"] == "UNANALYZABLE"
    assert rec["issues"]


def test_unanalyzable_on_strategy_exception(tmp_path):
    class Boom:
        def analyze(self, *a, **k):
            raise RuntimeError("unexpected")

    merged = tmp_path / "Foo.java"
    merged.write_text("class Foo {}\n")
    rec = dv.run_detector("Boom", Boom(), "merged_only", str(merged), SCN)
    assert rec["verdict"] == "UNANALYZABLE"
    assert "harness" in rec["issues"][0]["message"]


# --------------------------------------------------------------------------- #
# per-merge aggregation (plan §3: any-file-flag; diverged files drop out)
# --------------------------------------------------------------------------- #
def _fr(merge_id, arm="pos", outcome="clean", verdict="CLEAN", detectors=None):
    return {"merge_id": merge_id, "arm": arm, "scenario_id": f"{merge_id}__f",
            "file_path": "F.java", "merge_outcome": outcome,
            "file_verdict": verdict if outcome == "clean" else "DIVERGED",
            "detectors": detectors or {}, "runtime_s": 1.0}


def test_aggregate_passed_when_all_files_clean():
    rows = dv.aggregate_merges([_fr("m1"), _fr("m1")])
    assert rows[0]["status"] == "PASSED" and rows[0]["n_scored"] == 2


def test_aggregate_blocked_by_any_file_flag():
    rows = dv.aggregate_merges([_fr("m1"), _fr("m1", verdict="FLAG")])
    assert rows[0]["status"] == "BLOCKED"
    assert rows[0]["block_reason"] == "flag"


def test_aggregate_blocked_fail_closed_when_only_unanalyzable():
    rows = dv.aggregate_merges([_fr("m1", verdict="UNANALYZABLE"), _fr("m1")])
    assert rows[0]["status"] == "BLOCKED"
    assert rows[0]["block_reason"] == "fail_closed"


def test_aggregate_flag_outranks_unanalyzable():
    rows = dv.aggregate_merges(
        [_fr("m1", verdict="UNANALYZABLE"), _fr("m1", verdict="FLAG")])
    assert rows[0]["block_reason"] == "flag"


def test_aggregate_diverged_files_drop_out_of_scoring():
    rows = dv.aggregate_merges([_fr("m1", outcome="conflict"), _fr("m1")])
    assert rows[0]["status"] == "PASSED"
    assert rows[0]["n_diverged"] == 1 and rows[0]["n_scored"] == 1


def test_aggregate_all_diverged_leaves_sample():
    rows = dv.aggregate_merges(
        [_fr("m1", outcome="conflict"), _fr("m1", outcome="crash")])
    assert rows[0]["status"] == "ALL_DIVERGED"


def test_merge_id_fallback_derived_from_scenario_id():
    scn = {"repo_name": "owner_repo", "merge_commit": "abcdef012345"}
    assert dv.merge_id_of(scn) == "owner_repo__abcdef0123"
    assert dv.merge_id_of({**scn, "merge_id": "explicit"}) == "explicit"


# --------------------------------------------------------------------------- #
# G0 thresholds
# --------------------------------------------------------------------------- #
def _mr(runtime_s=10.0):
    return {"merge_id": "m", "arm": "pos", "n_files": 1, "n_diverged": 0,
            "n_scored": 1, "status": "PASSED", "block_reason": None,
            "runtime_s": runtime_s}


def test_g0_silent_below_min_merges():
    assert dv.g0_violation([_mr(99999)] * 4, []) is None


def test_g0_trips_on_median_runtime():
    reason = dv.g0_violation([_mr(2000)] * 5, [])
    assert reason and "median" in reason


def test_g0_trips_on_unanalyzable_fraction():
    una = {"JoernInfiniteLoop": {"verdict": "UNANALYZABLE", "issues": [], "runtime_s": 1}}
    files = [_fr(f"m{i}", detectors=una, verdict="UNANALYZABLE") for i in range(5)]
    files += [_fr(f"n{i}") for i in range(5)]
    reason = dv.g0_violation([_mr()] * 10, files)
    assert reason and "UNANALYZABLE" in reason


def test_g0_quiet_when_healthy():
    files = [_fr(f"m{i}") for i in range(10)]
    assert dv.g0_violation([_mr()] * 10, files) is None


# --------------------------------------------------------------------------- #
# G1 injection + live Joern (skips when Joern absent)
# --------------------------------------------------------------------------- #
def test_inject_snippet_appends_canonical_pattern():
    out = dv.inject_snippet("class Foo {}\n")
    assert out.startswith("class Foo {}\n")
    assert "pendingTasks.clear()" in out
    assert out.index("pendingTasks.clear()") < out.index("for (String task")


def test_inject_snippet_handles_missing_trailing_newline():
    out = dv.inject_snippet("class Foo {}")
    assert "class Foo {}\nclass MergeSanityStaleReadProbe" in out.replace("\n\n", "\n")


@pytest.mark.skipif(shutil.which("joern-parse") is None,
                    reason="joern-parse not on PATH")
def test_live_joern_fires_on_injected_pattern(tmp_path):
    """The spliced sanity pattern must FLAG under the real DFI strategy
    (single-file Phase-1 mode — one Joern run, keeps the test fast)."""
    name, strategy, _ = dv.DETECTORS[0]
    assert name == "JoernDataFlowInterference"
    merged = tmp_path / "Host.java"
    merged.write_text(dv.inject_snippet("class Host { void noop() {} }\n"))

    rec = dv.run_detector(name, strategy, "merged_only", str(merged), SCN)

    assert rec["verdict"] == "FLAG"
    assert any("stale read" in i["message"].lower() for i in rec["issues"])


# --------------------------------------------------------------------------- #
# Phase-2b: --merged-source developer + per-category recall + out-dir guard
# --------------------------------------------------------------------------- #
def test_reproduce_merge_developer_uses_resolution_no_docker(monkeypatch):
    """developer mode must never construct MergirafTool (no Docker on scorer)."""
    class Nope:
        def __init__(self):  # pragma: no cover - constructing at all is the bug
            raise AssertionError("MergirafTool constructed in developer mode")

    monkeypatch.setattr(dv, "MergirafTool", Nope)
    scn = {"scenario_id": "s1", "developer_resolution": "class M {}\n"}
    cache: dict = {}
    rec = dv.reproduce_merge(scn, cache, save=lambda: None, source="developer")
    assert rec == {"outcome": "clean", "merged": "class M {}\n", "rt": 0.0}
    assert "s1::__merge__::developer" in cache  # distinct from the mergiraf key


def test_aggregate_carries_category():
    fr = _fr("m1")
    fr["category"] = "3-dfi-stale-read"
    rows = dv.aggregate_merges([fr])
    assert rows[0]["category"] == "3-dfi-stale-read"
    assert dv.aggregate_merges([_fr("m2")])[0]["category"] == "unknown"


def _write_reports_text(tmp_path, file_records, merged_source="developer"):
    rows = dv.aggregate_merges(file_records)
    return dv.write_reports(tmp_path, file_records, rows, "abc1234", None,
                            merged_source)


def test_per_category_recall_section(tmp_path):
    frs = []
    for i, (cat, verdict) in enumerate([
        ("3-dfi-stale-read", "FLAG"), ("3-dfi-stale-read", "CLEAN"),
        ("6-rename", "FLAG"), ("none-of-7", "CLEAN"),
    ]):
        fr = _fr(f"m{i}", verdict=verdict)
        fr["category"] = cat
        frs.append(fr)
    text = _write_reports_text(tmp_path, frs)
    assert "Per-category recall" in text
    assert "3-dfi-stale-read" in text and "1/2" in text
    assert "6-rename" in text
    # scenarios.csv gained the category column
    header = (tmp_path / "scenarios.csv").read_text().splitlines()[0]
    assert "category" in header


def test_per_category_section_absent_for_legacy_pools(tmp_path):
    text = _write_reports_text(tmp_path, [_fr("m1"), _fr("m2")],
                               merged_source="mergiraf")
    assert "Per-category recall" not in text
    assert "mergiraf=Tests_failed" in text  # legacy arm labels intact


def test_developer_mode_arm_labels(tmp_path):
    text = _write_reports_text(tmp_path, [_fr("m1")])
    assert "externally labeled interference" in text
    assert "mergiraf=Tests_failed" not in text


def test_out_dir_mode_guard(tmp_path):
    dv.guard_out_dir_mode(tmp_path, "developer")          # stamps meta.json
    dv.guard_out_dir_mode(tmp_path, "developer")          # same mode: fine
    with pytest.raises(SystemExit, match="merged-source=developer"):
        dv.guard_out_dir_mode(tmp_path, "mergiraf")       # cross-mode: abort


def test_sanity_developer_mode_no_docker(monkeypatch, tmp_path):
    """run_sanity in developer mode splices into developer_resolution and
    consults only the (monkeypatched) detector — no MergirafTool."""
    class Nope:
        def __init__(self):  # pragma: no cover
            raise AssertionError("MergirafTool constructed in developer mode")

    monkeypatch.setattr(dv, "MergirafTool", Nope)

    fired = {}

    def fake_run_detector(name, strategy, mode, merged_path, scn):
        content = Path(merged_path).read_text()
        fired[scn["scenario_id"]] = "pendingTasks.clear()" in content
        return {"verdict": "FLAG",
                "issues": [{"line": 1, "severity": "CRITICAL",
                            "message": "Potential stale read (sanity)"}],
                "runtime_s": 0.01}

    monkeypatch.setattr(dv, "run_detector", fake_run_detector)
    ctl = [{"scenario_id": f"c{i}", "file_path": "F.java",
            "developer_resolution": f"class C{i} {{}}\n"}
           for i in range(dv.SANITY_N)]
    ok = dv.run_sanity(ctl, {}, lambda: None, tmp_path, "abc1234",
                       source="developer")
    assert ok
    assert len(fired) == dv.SANITY_N and all(fired.values())
