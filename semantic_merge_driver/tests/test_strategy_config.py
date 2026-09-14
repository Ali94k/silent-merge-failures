"""YAML-backed strategy configuration.

Replaces the prior hardcoded `strategies=["JoernInfiniteLoop"]` literal in
driver.py. The file at `config/strategies.yaml` is the single source of
truth for which strategies run.
"""
import pytest

from core.config import load_enabled_strategies
from core.plugin_loader import StrategyLoader


def _write_config(tmp_path, body: str):
    path = tmp_path / "strategies.yaml"
    path.write_text(body)
    return str(path)


def test_missing_file_returns_none(tmp_path):
    missing = tmp_path / "does_not_exist.yaml"
    assert load_enabled_strategies(str(missing)) is None


def test_enabled_key_absent_returns_none(tmp_path):
    path = _write_config(tmp_path, "other_key: 1\n")
    assert load_enabled_strategies(path) is None


def test_enabled_null_returns_none(tmp_path):
    path = _write_config(tmp_path, "enabled: null\n")
    assert load_enabled_strategies(path) is None


def test_enabled_list_returned_verbatim(tmp_path):
    path = _write_config(tmp_path, "enabled:\n  - JoernInfiniteLoop\n  - JoernInvalidLoopBounds\n")
    assert load_enabled_strategies(path) == ["JoernInfiniteLoop", "JoernInvalidLoopBounds"]


def test_enabled_empty_list_means_no_strategies(tmp_path):
    path = _write_config(tmp_path, "enabled: []\n")
    assert load_enabled_strategies(path) == []


def test_enabled_wrong_type_raises(tmp_path):
    path = _write_config(tmp_path, "enabled: JoernInfiniteLoop\n")
    with pytest.raises(ValueError, match="must be a list or null"):
        load_enabled_strategies(path)


def test_loader_loads_multiple_strategies_when_configured():
    """With both Joern strategies enabled, the plugin loader returns both."""
    loader = StrategyLoader(config_enabled_list=["JoernInfiniteLoop", "JoernInvalidLoopBounds"])
    strategies = loader.load_strategies()
    names = sorted(s.name for s in strategies)
    assert names == ["JoernInfiniteLoop", "JoernInvalidLoopBounds"]


def test_loader_filters_to_single_strategy():
    """Preserves the ability to run just one strategy via config."""
    loader = StrategyLoader(config_enabled_list=["JoernInfiniteLoop"])
    names = [s.name for s in loader.load_strategies()]
    assert names == ["JoernInfiniteLoop"]


def test_checked_in_config_enables_both_strategies():
    """The repo's config/strategies.yaml ships with both strategies on."""
    enabled = load_enabled_strategies()
    assert enabled is not None
    assert "JoernInfiniteLoop" in enabled
    assert "JoernInvalidLoopBounds" in enabled
