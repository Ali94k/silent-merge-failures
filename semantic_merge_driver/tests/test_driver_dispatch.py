"""driver.main() env-handling for SEMANTIC_MERGE_BACKEND selection.

Validates the env→class wiring without invoking any real merge backend
(no Docker, no git subprocess). Each test inspects what BACKENDS[name]
resolves to or how main() reacts to known/unknown values.
"""
import sys

import pytest

from core import driver
from core.backends.auto_backend import AutoBackend
from core.backends.git_merge_file_backend import GitMergeFileBackend
from core.backends.mergiraf_backend import MergirafBackend
from core.backends.spork_backend import SporkBackend
from core.backends.weave_backend import WeaveBackend


def test_default_backend_is_auto():
    assert driver.DEFAULT_BACKEND == "auto"


def test_default_resolves_to_auto_backend():
    assert driver.BACKENDS[driver.DEFAULT_BACKEND] is AutoBackend


def test_explicit_backends_still_registered():
    """Regression guard: env=git / =mergiraf / =spork / =weave must remain selectable."""
    assert driver.BACKENDS["git"] is GitMergeFileBackend
    assert driver.BACKENDS["mergiraf"] is MergirafBackend
    assert driver.BACKENDS["spork"] is SporkBackend
    assert driver.BACKENDS["weave"] is WeaveBackend
    assert driver.BACKENDS["auto"] is AutoBackend


def test_unknown_backend_name_exits_one(monkeypatch, capsys):
    monkeypatch.setenv("SEMANTIC_MERGE_BACKEND", "nonsense")
    monkeypatch.setattr(sys, "argv", ["driver.py", "b", "c", "t"])
    with pytest.raises(SystemExit) as exc:
        driver.main()
    assert exc.value.code == 1
    assert "Unknown SEMANTIC_MERGE_BACKEND" in capsys.readouterr().err


@pytest.mark.parametrize("name,cls", [
    ("git", GitMergeFileBackend),
    ("mergiraf", MergirafBackend),
    ("spork", SporkBackend),
    ("weave", WeaveBackend),
    ("auto", AutoBackend),
])
def test_env_selects_expected_class(name, cls):
    assert driver.BACKENDS[name] is cls
