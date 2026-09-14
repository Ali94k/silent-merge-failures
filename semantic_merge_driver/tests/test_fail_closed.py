"""Fail-closed behaviour of Joern-backed strategies.

If the Joern subprocess cannot run (binary missing, or exits non-zero with
check=True), the strategy must return is_clean=False rather than silently
treating the merge as clean. Prior behaviour was fail-open.
"""
import subprocess

import pytest

from strategies.joern_strategies.infinite_loop import JoernInfiniteLoopStrategy
from strategies.joern_strategies.invalid_loop_bounds import JoernInvalidLoopBoundsStrategy
from strategies.joern_strategies.taint_check import JoernDataFlowInterferenceStrategy


STRATEGIES = [
    pytest.param(JoernInfiniteLoopStrategy, id="infinite_loop"),
    pytest.param(JoernInvalidLoopBoundsStrategy, id="invalid_loop_bounds"),
    pytest.param(JoernDataFlowInterferenceStrategy, id="dataflow_interference"),
]


@pytest.mark.parametrize("strategy_cls", STRATEGIES)
def test_fail_closed_on_called_process_error(strategy_cls, tmp_path, monkeypatch):
    """joern-parse exiting non-zero must reject the merge."""
    def raise_called_process_error(*args, **kwargs):
        raise subprocess.CalledProcessError(returncode=1, cmd=args[0] if args else "joern-parse")

    monkeypatch.setattr(subprocess, "run", raise_called_process_error)

    source = tmp_path / "snippet.java"
    source.write_text("class A {}\n")

    result = strategy_cls().analyze(str(source))

    assert result.is_clean is False
    assert len(result.issues) == 1
    assert "inconclusive" in result.issues[0].message


@pytest.mark.parametrize("strategy_cls", STRATEGIES)
def test_fail_closed_on_missing_binary(strategy_cls, tmp_path, monkeypatch):
    """joern-parse not on PATH must reject the merge."""
    def raise_file_not_found(*args, **kwargs):
        raise FileNotFoundError("joern-parse: not found")

    monkeypatch.setattr(subprocess, "run", raise_file_not_found)

    source = tmp_path / "snippet.java"
    source.write_text("class A {}\n")

    result = strategy_cls().analyze(str(source))

    assert result.is_clean is False
    assert len(result.issues) == 1
    assert result.issues[0].severity == "CRITICAL"


@pytest.mark.parametrize("strategy_cls", STRATEGIES)
def test_fail_closed_on_query_returncode(strategy_cls, tmp_path, monkeypatch):
    """Shelled `joern --cpg ...` query exiting non-zero must reject the merge.

    Distinct from the joern-parse path (check=True → CalledProcessError): the
    query is invoked with shell=True and returns a CompletedProcess. A crashed
    query yields empty stdout, which the per-strategy parser would otherwise
    treat as zero issues → is_clean=True (fail-silent).
    """
    def mock_run(*args, **kwargs):
        if kwargs.get("shell"):
            return subprocess.CompletedProcess(
                args=args[0], returncode=1, stdout="", stderr="boom",
            )
        return subprocess.CompletedProcess(
            args=args[0], returncode=0, stdout="", stderr="",
        )

    monkeypatch.setattr(subprocess, "run", mock_run)

    source = tmp_path / "snippet.java"
    source.write_text("class A {}\n")

    result = strategy_cls().analyze(str(source))

    assert result.is_clean is False
    assert len(result.issues) == 1
    assert result.issues[0].severity == "CRITICAL"
    assert "inconclusive" in result.issues[0].message
