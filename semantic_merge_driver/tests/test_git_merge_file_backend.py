"""Tests for GitMergeFileBackend.

Three scenarios:
- Clean merge (theirs adds, ours unchanged) -> MergeOutcome.CLEAN.
- Conflict (both modify same line) -> MergeOutcome.CONFLICT with <<<<<<< markers
  in ours_path.
- Subprocess failure (git not on PATH) -> MergeOutcome.CRASH (fail-closed).
"""
import subprocess

from core.backends.base import MergeOutcome
from core.backends.git_merge_file_backend import GitMergeFileBackend


def _write_three(tmp_path, base, ours, theirs):
    """Stage base/ours/theirs files; return their paths as a tuple."""
    (tmp_path / "base").write_text(base)
    (tmp_path / "ours").write_text(ours)
    (tmp_path / "theirs").write_text(theirs)
    return (
        str(tmp_path / "base"),
        str(tmp_path / "ours"),
        str(tmp_path / "theirs"),
    )


def test_clean_merge(tmp_path):
    """Non-overlapping edit in theirs merges cleanly; ours_path mutated in place."""
    base, ours, theirs = _write_three(
        tmp_path,
        base="line 1\nline 2\n",
        ours="line 1\nline 2\n",
        theirs="line 1\nline 2\nline 3\n",
    )

    outcome = GitMergeFileBackend().merge(base, ours, theirs)

    assert outcome == MergeOutcome.CLEAN
    assert (tmp_path / "ours").read_text() == "line 1\nline 2\nline 3\n"


def test_conflict_emits_markers(tmp_path):
    """Overlapping edits produce conflict markers in ours_path."""
    base, ours, theirs = _write_three(
        tmp_path,
        base="hello\n",
        ours="hello ours\n",
        theirs="hello theirs\n",
    )

    outcome = GitMergeFileBackend().merge(base, ours, theirs)

    assert outcome == MergeOutcome.CONFLICT
    merged = (tmp_path / "ours").read_text()
    assert "<<<<<<<" in merged
    assert "=======" in merged
    assert ">>>>>>>" in merged


def test_fail_closed_on_missing_git(tmp_path, monkeypatch):
    """If git is not on PATH, the backend must return CRASH, never raise."""
    def raise_file_not_found(*args, **kwargs):
        raise FileNotFoundError("git: not found")

    monkeypatch.setattr(subprocess, "run", raise_file_not_found)

    base, ours, theirs = _write_three(tmp_path, "a\n", "a\n", "a\n")

    outcome = GitMergeFileBackend().merge(base, ours, theirs)

    assert outcome == MergeOutcome.CRASH
