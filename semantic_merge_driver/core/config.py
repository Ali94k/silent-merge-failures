import os
from typing import List, Optional
import yaml


PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG_PATH = os.path.join(PACKAGE_ROOT, "config", "strategies.yaml")


def load_enabled_strategies(config_path: str = DEFAULT_CONFIG_PATH) -> Optional[List[str]]:
    """Load the `enabled` strategy list from a YAML config file.

    Returns:
        - list[str]: strategy names to activate (may be empty).
        - None: config missing or `enabled` key absent/null; caller should
          treat this as "load all discovered strategies".

    Raises:
        ValueError: config file exists but `enabled` is not a list or null.
    """
    if not os.path.exists(config_path):
        return None

    with open(config_path) as f:
        data = yaml.safe_load(f) or {}

    if "enabled" not in data:
        return None

    enabled = data["enabled"]
    if enabled is None:
        return None
    if not isinstance(enabled, list):
        raise ValueError(
            f"{config_path}: `enabled` must be a list or null, got {type(enabled).__name__}"
        )
    return [str(name) for name in enabled]
