"""JoernInfiniteLoopStrategy v2 — loop-only, exit-aware, differential.

Each live test encodes a Stage-A pilot false-positive shape (ISSUES #29):
`if(true)` is not a loop; `while(true){...break/return/throw...}` idioms are
deliberate; pre-existing loops are not merge-induced. Fail-closed coverage
stays in test_fail_closed.py (this strategy keeps its no-parents Phase-1
mode, so the shared parametrization still applies).
"""
import shutil

import pytest

from strategies.joern_strategies.infinite_loop import JoernInfiniteLoopStrategy

JOERN = shutil.which("joern-parse") is not None
pytestmark = pytest.mark.skipif(not JOERN, reason="joern-parse not on PATH")

SPIN = """\
public class Loops {
    private int count = 0;
    public void spin() {
        while (true) { count++; }
    }
}
"""

NO_LOOP = """\
public class Loops {
    private int count = 0;
    public void calm() { count++; }
}
"""

IDIOMS = """\
public class Loops {
    private int count = 0;
    public void server() {
        while (true) { if (ready()) { break; } }
    }
    public void returner() {
        while (true) { if (ready()) return; }
    }
    public void thrower() {
        while (true) { throw new RuntimeException("x"); }
    }
    public void notLoop() {
        if (true) { count++; }
    }
    private boolean ready() { return true; }
}
"""


def _write(tmp_path, content):
    p = tmp_path / "Loops.java"
    p.write_text(content, encoding="utf-8")
    return p


def test_flags_exitless_constant_loop_single_file(tmp_path):
    result = JoernInfiniteLoopStrategy().analyze(str(_write(tmp_path, SPIN)))
    assert not result.is_clean
    assert any("infinite loop" in i.message.lower() and "'spin'" in i.message
               for i in result.issues)


def test_pilot_fp_shapes_are_clean_single_file(tmp_path):
    """break/return/throw idioms + if(true): all five pilot FPs, zero flags."""
    result = JoernInfiniteLoopStrategy().analyze(str(_write(tmp_path, IDIOMS)))
    assert result.is_clean is True, [i.message for i in result.issues]


def test_differential_suppresses_preexisting_loop(tmp_path):
    """The loop exists verbatim in a parent -> not merge-induced -> clean."""
    merged = _write(tmp_path, SPIN)
    result = JoernInfiniteLoopStrategy().analyze(
        str(merged), base_content=NO_LOOP, ours_content=SPIN, theirs_content=NO_LOOP)
    assert result.is_clean is True, [i.message for i in result.issues]


def test_differential_flags_merge_induced_loop(tmp_path):
    """Loop in merged but in neither parent -> merge-induced -> flag."""
    merged = _write(tmp_path, SPIN)
    result = JoernInfiniteLoopStrategy().analyze(
        str(merged), base_content=NO_LOOP, ours_content=NO_LOOP, theirs_content=NO_LOOP)
    assert not result.is_clean
    assert any("'spin'" in i.message for i in result.issues)
