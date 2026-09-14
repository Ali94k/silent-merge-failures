"""Tests for WeaveBackend.

Three scenarios:
- Clean merge (theirs adds a method) -> MergeOutcome.CLEAN; the -o output is
  copied into ours_path (non-vacuous: asserts the new method is present).
  Requires Docker + image.
- Conflict (both modify the same entity) -> MergeOutcome.CONFLICT. Weave is
  entity-level: on a whole-entity conflict it writes NO git-style marker file
  (verified on v0.3.2), so the contract under test is (a) outcome is CONFLICT
  and (b) ours_path is NOT blanked (no silent data loss). Requires Docker + image.
- Subprocess failure (docker not on PATH) -> MergeOutcome.CRASH via monkeypatched
  subprocess.run. No Docker required.

The first two tests are gated on `docker image inspect merge-tools/weave:0.3.2`
succeeding. On environments without Docker or the image, they skip cleanly
(pytest shows them as 's' rather than failing). Build the image via
`cd merge-tool-comparison && make docker-build`.
"""
import subprocess

import pytest

from core.backends.base import MergeOutcome
from core.backends.weave_backend import IMAGE, WeaveBackend


def _docker_image_available():
    """Check whether the Weave Docker image is loadable on this host."""
    try:
        subprocess.run(
            ["docker", "image", "inspect", IMAGE],
            capture_output=True, check=True,
        )
        return True
    except (FileNotFoundError, OSError, subprocess.CalledProcessError):
        return False


REQUIRES_WEAVE_IMAGE = pytest.mark.skipif(
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


@REQUIRES_WEAVE_IMAGE
def test_clean_merge(tmp_path):
    """Non-overlapping edit (theirs adds method) merges cleanly; ours mutated in place."""
    base, ours, theirs = _write_three(
        tmp_path,
        base='class A {\n  void hello() { System.out.println("x"); }\n}\n',
        ours='class A {\n  void hello() { System.out.println("x"); }\n}\n',
        theirs='class A {\n  void hello() { System.out.println("x"); }\n  void bye() {}\n}\n',
    )

    outcome = WeaveBackend().merge(base, ours, theirs)

    assert outcome == MergeOutcome.CLEAN
    merged = (tmp_path / "ours.java").read_text()
    assert "bye" in merged
    assert "<<<<<<<" not in merged


@REQUIRES_WEAVE_IMAGE
def test_conflict_detected_without_data_loss(tmp_path):
    """Both sides modify the same entity -> CONFLICT, and ours is not blanked.

    Weave is entity-level: on a whole-entity conflict v0.3.2 emits a summary and
    writes no git-style marker output. The backend must still report CONFLICT
    (so the driver rejects) and must NOT empty ours_path.
    """
    base, ours, theirs = _write_three(
        tmp_path,
        base='class A {\n  int v() { return 0; }\n}\n',
        ours='class A {\n  int v() { return 1; }\n}\n',
        theirs='class A {\n  int v() { return 2; }\n}\n',
    )

    outcome = WeaveBackend().merge(base, ours, theirs)

    assert outcome == MergeOutcome.CONFLICT
    merged = (tmp_path / "ours.java").read_text()
    assert merged.strip() != ""  # ours_path not blanked (no silent data loss)


def test_fail_closed_on_missing_docker(tmp_path, monkeypatch):
    """If docker is not on PATH (or any subprocess error), return CRASH, never raise."""
    def raise_file_not_found(*args, **kwargs):
        raise FileNotFoundError("docker: not found")

    monkeypatch.setattr(subprocess, "run", raise_file_not_found)

    base, ours, theirs = _write_three(tmp_path, "a\n", "a\n", "a\n")

    outcome = WeaveBackend().merge(base, ours, theirs)

    assert outcome == MergeOutcome.CRASH
