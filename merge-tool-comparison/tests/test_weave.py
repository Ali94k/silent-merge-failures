from unittest.mock import patch, MagicMock

from src.core.docker_runner import DockerResult
from src.core.interfaces import MergeOutcome
from src.tools.weave import WeaveTool


def _docker(return_code, timed_out=False):
    return DockerResult(
        return_code=return_code, stdout="", stderr="",
        runtime_seconds=1.0, timed_out=timed_out,
    )


def _merge_in(tmp_path):
    """Run WeaveTool().merge() with its internal TemporaryDirectory pinned to
    tmp_path, so a pre-placed `out` file is visible to the adapter."""
    tool = WeaveTool()
    with patch("tempfile.TemporaryDirectory") as mock_tmpdir:
        mock_tmpdir.return_value.__enter__ = MagicMock(return_value=str(tmp_path))
        mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
        return tool.merge("base", "ours", "theirs")


def test_tool_name():
    assert WeaveTool().name == "weave"


def test_docker_image():
    assert WeaveTool().docker_image == "merge-tools/weave:0.3.2"


@patch("src.tools.weave.run_in_docker")
def test_clean_merge(mock_docker, tmp_path):
    merged = "public class Foo { }\n"
    (tmp_path / "out").write_text(merged)
    mock_docker.return_value = _docker(0)

    result = _merge_in(tmp_path)

    assert result.outcome == MergeOutcome.CLEAN
    assert result.merged_content == merged
    assert result.conflict_count == 0


@patch("src.tools.weave.run_in_docker")
def test_conflict_no_output_file(mock_docker, tmp_path):
    # Entity-level conflict: rc 1, Weave writes no -o file. Signalled by rc;
    # count is forced to >=1 so the conflict is visible in aggregates.
    mock_docker.return_value = _docker(1)

    result = _merge_in(tmp_path)

    assert result.outcome == MergeOutcome.CONFLICT
    assert result.merged_content is None
    assert result.conflict_count == 1


@patch("src.tools.weave.run_in_docker")
def test_conflict_with_markers_in_output(mock_docker, tmp_path):
    # Partial conflict: rc 1 AND an -o file carrying entity-annotated markers.
    produced = (
        "<<<<<<< ours\na\n=======\nb\n>>>>>>> theirs\n"
        "<<<<<<< ours\nc\n=======\nd\n>>>>>>> theirs\n"
    )
    (tmp_path / "out").write_text(produced)
    mock_docker.return_value = _docker(1)

    result = _merge_in(tmp_path)

    assert result.outcome == MergeOutcome.CONFLICT
    assert result.merged_content == produced
    assert result.conflict_count == 2


@patch("src.tools.weave.run_in_docker")
def test_clean_rc_but_no_output_is_crash(mock_docker, tmp_path):
    # rc 0 promises merged content in the -o file; its absence is a crash.
    mock_docker.return_value = _docker(0)

    result = _merge_in(tmp_path)
    assert result.outcome == MergeOutcome.CRASH


@patch("src.tools.weave.run_in_docker")
def test_crash_bad_return_code(mock_docker, tmp_path):
    mock_docker.return_value = _docker(2)

    result = _merge_in(tmp_path)
    assert result.outcome == MergeOutcome.CRASH


@patch("src.tools.weave.run_in_docker")
def test_timeout(mock_docker):
    mock_docker.return_value = _docker(-1, timed_out=True)

    result = WeaveTool().merge("base", "ours", "theirs")
    assert result.outcome == MergeOutcome.TIMEOUT
