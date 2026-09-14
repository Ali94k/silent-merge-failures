"""P2 whole-driver eval harness tests (tools/whole_driver_eval.py).

Docker-free: every test exercises pure scoring/aggregation/Stage-C-reuse logic.
contents_match runs under conftest's whitespace-only normalization (FORMATTER
and AST_NORMALIZE off), so distinct non-whitespace strings compare unequal.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import whole_driver_eval as wd  # noqa: E402
from src.evaluation.comparator import Classification  # noqa: E402


def _scn(base="A", ours="B", theirs="C", dev="D", sid="repo__abc__F.java"):
    return {"scenario_id": sid, "file_path": "F.java", "merge_id": "repo__abc",
            "base_content": base, "ours_content": ours, "theirs_content": theirs,
            "developer_resolution": dev}


# --------------------------------------------------------------------------- #
# hybrid oracle (the crux)
# --------------------------------------------------------------------------- #
def test_clean_equals_mergiraf_ref_uses_test_label():
    res = {"outcome": "clean", "merged": "MERGEDX"}
    # positive arm: ref output is Tests_failed → silent-wrong → FP
    cls, oracle = wd.score("pos", res, _scn(), mergiraf_ref="MERGEDX")
    assert cls == Classification.FALSE_POSITIVE and oracle == "test-label"
    # control arm: ref output is Tests_passed → correct → TP
    cls, oracle = wd.score("ctl", res, _scn(), mergiraf_ref="MERGEDX")
    assert cls == Classification.TRUE_POSITIVE and oracle == "test-label"


def test_clean_diverges_falls_back_to_dev_match_tp():
    # output != mergiraf ref, but == developer resolution → dev-match TP
    res = {"outcome": "clean", "merged": "DEVRES"}
    cls, oracle = wd.score("pos", res, _scn(dev="DEVRES"), mergiraf_ref="OTHER")
    assert cls == Classification.TRUE_POSITIVE and oracle == "dev-match"


def test_clean_diverges_and_wrong_is_dev_match_fp():
    res = {"outcome": "clean", "merged": "WRONG"}
    cls, oracle = wd.score("ctl", res, _scn(dev="DEVRES"), mergiraf_ref="OTHER")
    assert cls == Classification.FALSE_POSITIVE and oracle == "dev-match"


def test_no_ref_falls_back_to_dev_match():
    res = {"outcome": "clean", "merged": "DEVRES"}
    cls, oracle = wd.score("pos", res, _scn(dev="DEVRES"), mergiraf_ref=None)
    assert cls == Classification.TRUE_POSITIVE and oracle == "dev-match"


def test_conflict_scored_as_visible_via_dev_match():
    # reject (conflict) → CONFLICT branch; dev novel (≠ base/ours/theirs) → TN (x1)
    res = {"outcome": "conflict", "merged": None, "reject_reason": "semantic"}
    cls, oracle = wd.score("pos", res, _scn(dev="NOVEL"), mergiraf_ref="X")
    assert cls in (Classification.TRUE_NEGATIVE, Classification.FALSE_NEGATIVE)
    assert oracle == "dev-match"


def test_crash_and_timeout_classify_directly():
    assert wd.score("pos", {"outcome": "crash"}, _scn(), "X")[0] == Classification.CRASH
    assert wd.score("pos", {"outcome": "timeout"}, _scn(), "X")[0] == Classification.TIMEOUT


# --------------------------------------------------------------------------- #
# reject-reason parsing (driver stdout → reason)
# --------------------------------------------------------------------------- #
def test_reject_reason_parsing():
    assert wd._reject_reason("Backend 'spork' crashed; rejecting merge.") == "crash"
    assert wd._reject_reason("[CRITICAL] RM2: stale\nSemantic Merge Rejected: ...") == "semantic"
    assert wd._reject_reason("Textual Merge Conflicts Exist.") == "textual"
    assert wd._reject_reason("could not read inputs") == "error"


def test_parse_route_basic_and_fallback():
    assert wd._parse_route("nothing here") is None
    r = wd._parse_route("AutoBackend: cluster=intra_body language=java → spork")
    assert r["cluster"] == "intra_body" and r["chosen"] == "spork"
    assert r["effective"] == "spork" and r["fell_back"] is False
    # crash-fallback: chosen is spork but effective becomes git
    out = ("AutoBackend: cluster=migrate_decl language=java → weave\n"
           "AutoBackend: weave crashed; falling back to git-merge-file")
    r = wd._parse_route(out)
    assert r["chosen"] == "weave" and r["fell_back"] is True
    assert r["effective"] == "git-merge-file"


# --------------------------------------------------------------------------- #
# Stage-C reuse mapping (driver-mergiraf / bare-mergiraf)
# --------------------------------------------------------------------------- #
def _sc(file_verdict, merge_outcome="clean", ref="REF"):
    return {"repo__abc__F.java": {"file_verdict": file_verdict,
                                  "merge_outcome": merge_outcome, "ref_merged": ref}}


def test_driver_mergiraf_clean_accepts():
    r = wd.driver_mergiraf_result(_scn(), _sc("CLEAN"))
    assert r["outcome"] == "clean" and r["merged"] == "REF" and r["reject_reason"] is None


def test_driver_mergiraf_flag_semantic_rejects():
    r = wd.driver_mergiraf_result(_scn(), _sc("FLAG"))
    assert r["outcome"] == "conflict" and r["reject_reason"] == "semantic"


def test_driver_mergiraf_unanalyzable_fail_closed():
    r = wd.driver_mergiraf_result(_scn(), _sc("UNANALYZABLE"))
    assert r["outcome"] == "crash" and r["reject_reason"] == "crash"


def test_driver_mergiraf_diverged_textual_reject():
    r = wd.driver_mergiraf_result(_scn(), _sc("DIVERGED", merge_outcome="conflict"))
    assert r["outcome"] == "conflict" and r["reject_reason"] == "textual"


def test_bare_mergiraf_clean_vs_diverged():
    assert wd.bare_mergiraf_result(_scn(), _sc("CLEAN"))["outcome"] == "clean"
    div = wd.bare_mergiraf_result(_scn(), _sc("DIVERGED", merge_outcome="conflict"))
    assert div["outcome"] == "conflict" and div["merged"] is None


def test_stage_c_missing_record_returns_none():
    assert wd.driver_mergiraf_result(_scn(sid="other__x__F.java"), _sc("CLEAN")) is None


# --------------------------------------------------------------------------- #
# per-merge aggregation
# --------------------------------------------------------------------------- #
def _rec(mid, reason, outcome="conflict"):
    return {"merge_id": mid, "reject_reason": reason, "outcome": outcome}


def test_three_outcome_priority_semantic_over_textual():
    recs = [_rec("m", "textual"), _rec("m", "semantic")]
    assert wd.per_merge_three_outcome(recs)["m"] == "semantic"


def test_three_outcome_accept_when_all_clean():
    recs = [{"merge_id": "m", "reject_reason": None, "outcome": "clean"}]
    assert wd.per_merge_three_outcome(recs)["m"] == "accept"


def test_three_outcome_textual_over_crash():
    recs = [_rec("m", "crash"), _rec("m", "textual")]
    assert wd.per_merge_three_outcome(recs)["m"] == "textual"


def test_stage_c_style_r_counts_blocked_and_drops_all_diverged():
    recs = [
        # merge A: one clean file flagged (semantic) → scored + blocked
        {"merge_id": "A", "reject_reason": "semantic", "outcome": "conflict"},
        # merge B: clean accept → scored, not blocked
        {"merge_id": "B", "reject_reason": None, "outcome": "clean"},
        # merge C: all files diverged (textual on conflict) → leaves the sample
        {"merge_id": "C", "reject_reason": "textual", "outcome": "conflict"},
    ]
    blocked, scored = wd.stage_c_style_r(recs)
    assert (blocked, scored) == (1, 2)
