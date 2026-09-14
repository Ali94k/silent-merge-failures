import importlib
import logging
import pkgutil
from typing import Optional

import src.tools as tools_package
from src.core.interfaces import MergeTool

logger = logging.getLogger(__name__)


class ToolLoader:
    """Dynamically discovers MergeTool subclasses in the src.tools package."""

    def __init__(self, enabled_tools: Optional[list[str]] = None):
        self.enabled_tools = enabled_tools

    def load_tools(self) -> list[MergeTool]:
        self._import_all_tool_modules()
        all_tools = [cls() for cls in MergeTool.__subclasses__()]

        if self.enabled_tools is not None:
            all_tools = [t for t in all_tools if t.name in self.enabled_tools]

        return all_tools

    def _import_all_tool_modules(self):
        for importer, modname, ispkg in pkgutil.walk_packages(
            tools_package.__path__, prefix=tools_package.__name__ + "."
        ):
            try:
                importlib.import_module(modname)
            except Exception as e:
                logger.warning(f"Failed to import tool module {modname}: {e}")


def load_tools_from_config(config_path: str) -> list[MergeTool]:
    """Load tools based on tools.yaml config."""
    import yaml
    from pathlib import Path

    config = yaml.safe_load(Path(config_path).read_text())
    enabled = [t["name"] for t in config["tools"] if t.get("enabled", True)]
    return ToolLoader(enabled_tools=enabled).load_tools()
