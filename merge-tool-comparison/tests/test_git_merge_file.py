from pathlib import Path

import pytest

from src.core.interfaces import MergeOutcome
from src.tools.git_merge_file import GitMergeFileTool

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def tool():
    return GitMergeFileTool()


def test_clean_merge(tool):
    base = (FIXTURES / "simple_add" / "base.java").read_text()
    ours = (FIXTURES / "simple_add" / "ours.java").read_text()
    theirs = (FIXTURES / "simple_add" / "theirs.java").read_text()

    result = tool.merge(base, ours, theirs)
    assert result.outcome == MergeOutcome.CLEAN
    assert result.conflict_count == 0
    assert "subtract" in result.merged_content
    assert "multiply" in result.merged_content


def test_conflict_merge(tool):
    base = (FIXTURES / "conflict" / "base.java").read_text()
    ours = (FIXTURES / "conflict" / "ours.java").read_text()
    theirs = (FIXTURES / "conflict" / "theirs.java").read_text()

    result = tool.merge(base, ours, theirs)
    assert result.outcome == MergeOutcome.CONFLICT
    assert result.conflict_count >= 1


def test_tool_name(tool):
    assert tool.name == "git-merge-file"
