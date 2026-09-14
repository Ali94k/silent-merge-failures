from unittest.mock import patch

from src.core.docker_runner import DockerResult
from src.core.interfaces import MergeOutcome
from src.tools.mergiraf import MergirafTool


def test_tool_name():
    assert MergirafTool().name == "mergiraf"


def test_docker_image():
    assert MergirafTool().docker_image == "merge-tools/mergiraf:0.17.0"


@patch("src.tools.mergiraf.run_in_docker")
def test_clean_merge(mock_docker):
    merged = "public class Foo { }\n"
    mock_docker.return_value = DockerResult(
        return_code=0, stdout=merged, stderr="",
        runtime_seconds=1.0, timed_out=False,
    )

    result = MergirafTool().merge("base", "ours", "theirs")

    assert result.outcome == MergeOutcome.CLEAN
    assert result.merged_content == merged
    assert result.conflict_count == 0


@patch("src.tools.mergiraf.run_in_docker")
def test_conflict_merge(mock_docker):
    # Mergiraf signals an unresolved conflict with rc 1 + git-style markers.
    merged = (
        "<<<<<<< ours\nfoo\n=======\nbar\n>>>>>>> theirs\n"
        "<<<<<<< ours\nbaz\n=======\nqux\n>>>>>>> theirs\n"
    )
    mock_docker.return_value = DockerResult(
        return_code=1, stdout=merged, stderr="",
        runtime_seconds=1.0, timed_out=False,
    )

    result = MergirafTool().merge("base", "ours", "theirs")

    assert result.outcome == MergeOutcome.CONFLICT
    assert result.conflict_count == 2


@patch("src.tools.mergiraf.run_in_docker")
def test_timeout(mock_docker):
    mock_docker.return_value = DockerResult(
        return_code=-1, stdout="", stderr="timed out",
        runtime_seconds=120.0, timed_out=True,
    )

    result = MergirafTool().merge("base", "ours", "theirs")
    assert result.outcome == MergeOutcome.TIMEOUT


@patch("src.tools.mergiraf.run_in_docker")
def test_crash_bad_return_code(mock_docker):
    # rc outside {0, 1} → genuine failure (unparseable input / runtime error).
    mock_docker.return_value = DockerResult(
        return_code=2, stdout="", stderr="parse error",
        runtime_seconds=1.0, timed_out=False,
    )

    result = MergirafTool().merge("base", "ours", "theirs")
    assert result.outcome == MergeOutcome.CRASH


@patch("src.tools.mergiraf.run_in_docker")
def test_crash_empty_stdout(mock_docker):
    # Valid rc but no merged output on stdout → treated as a crash.
    mock_docker.return_value = DockerResult(
        return_code=0, stdout="", stderr="",
        runtime_seconds=1.0, timed_out=False,
    )

    result = MergirafTool().merge("base", "ours", "theirs")
    assert result.outcome == MergeOutcome.CRASH
