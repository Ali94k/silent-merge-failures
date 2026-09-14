from unittest.mock import patch, MagicMock
from pathlib import Path

from src.core.docker_runner import DockerResult
from src.core.interfaces import MergeOutcome
from src.tools.mastery import MasteryTool


def test_tool_name():
    tool = MasteryTool()
    assert tool.name == "mastery"


def test_docker_image():
    tool = MasteryTool()
    assert tool.docker_image == "merge-tools/mastery"


@patch("src.tools.mastery.run_in_docker")
def test_clean_merge(mock_docker, tmp_path):
    merged_content = "public class Foo { }"
    merged_file = tmp_path / "merged.java"
    merged_file.write_text(merged_content)

    mock_docker.return_value = DockerResult(
        return_code=0, stdout="", stderr="",
        runtime_seconds=1.5, timed_out=False,
    )

    tool = MasteryTool()
    with patch("tempfile.TemporaryDirectory") as mock_tmpdir:
        mock_tmpdir.return_value.__enter__ = MagicMock(return_value=str(tmp_path))
        mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
        result = tool.merge("base", "ours", "theirs")

    assert result.outcome == MergeOutcome.CLEAN
    assert result.merged_content == merged_content
    assert result.conflict_count == 0


@patch("src.tools.mastery.run_in_docker")
def test_conflict_merge(mock_docker, tmp_path):
    merged_content = "<<<<<<< ours\nfoo\n=======\nbar\n>>>>>>>"
    merged_file = tmp_path / "merged.java"
    merged_file.write_text(merged_content)

    mock_docker.return_value = DockerResult(
        return_code=0, stdout="", stderr="",
        runtime_seconds=2.0, timed_out=False,
    )

    tool = MasteryTool()
    with patch("tempfile.TemporaryDirectory") as mock_tmpdir:
        mock_tmpdir.return_value.__enter__ = MagicMock(return_value=str(tmp_path))
        mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
        result = tool.merge("base", "ours", "theirs")

    assert result.outcome == MergeOutcome.CONFLICT
    assert result.conflict_count >= 1


@patch("src.tools.mastery.run_in_docker")
def test_timeout(mock_docker):
    mock_docker.return_value = DockerResult(
        return_code=-1, stdout="", stderr="timed out",
        runtime_seconds=120.0, timed_out=True,
    )

    tool = MasteryTool()
    result = tool.merge("base", "ours", "theirs")
    assert result.outcome == MergeOutcome.TIMEOUT


@patch("src.tools.mastery.run_in_docker")
def test_crash_signal(mock_docker):
    mock_docker.return_value = DockerResult(
        return_code=-9, stdout="", stderr="killed",
        runtime_seconds=5.0, timed_out=False,
    )

    tool = MasteryTool()
    result = tool.merge("base", "ours", "theirs")
    assert result.outcome == MergeOutcome.CRASH


@patch("src.tools.mastery.run_in_docker")
def test_crash_no_output(mock_docker, tmp_path):
    # No merged.java file created
    mock_docker.return_value = DockerResult(
        return_code=1, stdout="", stderr="error",
        runtime_seconds=3.0, timed_out=False,
    )

    tool = MasteryTool()
    with patch("tempfile.TemporaryDirectory") as mock_tmpdir:
        mock_tmpdir.return_value.__enter__ = MagicMock(return_value=str(tmp_path))
        mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
        result = tool.merge("base", "ours", "theirs")

    assert result.outcome == MergeOutcome.CRASH
