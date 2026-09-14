"""Tests for MergirafBackend.

Three scenarios:
- Clean merge (theirs adds a method) -> MergeOutcome.CLEAN. Requires Docker + image.
- Conflict (both modify same line) -> MergeOutcome.CONFLICT with <<<<<<< markers
  in ours_path. Requires Docker + image.
- Subprocess failure (docker not on PATH) -> MergeOutcome.CRASH via monkeypatched
  subprocess.run. No Docker required.

The first two tests are gated on `docker image inspect merge-tools/mergiraf:0.17.0`
succeeding. On environments without Docker or the image, they skip cleanly
(pytest shows them as 's' rather than failing). Build the image via
`cd merge-tool-comparison && make docker-build`.
"""
import subprocess

import pytest

from core.backends.base import MergeOutcome
from core.backends.mergiraf_backend import IMAGE, MergirafBackend


def _docker_image_available():
    """Check whether the Mergiraf Docker image is loadable on this host."""
    try:
        subprocess.run(
            ["docker", "image", "inspect", IMAGE],
            capture_output=True, check=True,
        )
        return True
    except (FileNotFoundError, OSError, subprocess.CalledProcessError):
        return False


REQUIRES_MERGIRAF_IMAGE = pytest.mark.skipif(
    not _docker_image_available(),
    reason=f"Docker or {IMAGE} image not available; run `cd merge-tool-comparison && make docker-build`",
)


def _write_three(tmp_path, base, ours, theirs):
    """Stage base/ours/theirs files with .java extensions; return their paths."""
    (tmp_path / "base.java").write_text(base)
    (tmp_path / "ours.java").write_text(ours)
    (tmp_path / "theirs.java").write_text(theirs)
    return (
        str(tmp_path / "base.java"),
        str(tmp_path / "ours.java"),
        str(tmp_path / "theirs.java"),
    )


@REQUIRES_MERGIRAF_IMAGE
def test_clean_merge(tmp_path):
    """Non-overlapping edit (theirs adds method) merges cleanly; ours mutated in place."""
    base, ours, theirs = _write_three(
        tmp_path,
        base='class A {\n  void hello() { System.out.println("x"); }\n}\n',
        ours='class A {\n  void hello() { System.out.println("x"); }\n}\n',
        theirs='class A {\n  void hello() { System.out.println("x"); }\n  void bye() {}\n}\n',
    )

    outcome = MergirafBackend().merge(base, ours, theirs)

    assert outcome == MergeOutcome.CLEAN
    merged = (tmp_path / "ours.java").read_text()
    assert "void bye()" in merged
    assert "<<<<<<<" not in merged


@REQUIRES_MERGIRAF_IMAGE
def test_conflict_emits_markers(tmp_path):
    """Overlapping edits on the same line produce conflict markers in ours."""
    base, ours, theirs = _write_three(
        tmp_path,
        base='class A {\n  void hello() { System.out.println("base"); }\n}\n',
        ours='class A {\n  void hello() { System.out.println("ours"); }\n}\n',
        theirs='class A {\n  void hello() { System.out.println("theirs"); }\n}\n',
    )

    outcome = MergirafBackend().merge(base, ours, theirs)

    assert outcome == MergeOutcome.CONFLICT
    merged = (tmp_path / "ours.java").read_text()
    assert "<<<<<<<" in merged
    assert "=======" in merged
    assert ">>>>>>>" in merged


def test_fail_closed_on_missing_docker(tmp_path, monkeypatch):
    """If docker is not on PATH (or any subprocess error), return CRASH, never raise."""
    def raise_file_not_found(*args, **kwargs):
        raise FileNotFoundError("docker: not found")

    monkeypatch.setattr(subprocess, "run", raise_file_not_found)

    base, ours, theirs = _write_three(tmp_path, "a\n", "a\n", "a\n")

    outcome = MergirafBackend().merge(base, ours, theirs)

    assert outcome == MergeOutcome.CRASH
