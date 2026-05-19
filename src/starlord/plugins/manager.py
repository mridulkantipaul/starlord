"""Plugin manager (file-based discovery)."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import List


@dataclass
class PluginInfo:
    name: str
    module: str


class PluginManager:
    def __init__(self, plugins_path: Path) -> None:
        self.plugins_path = plugins_path

    def discover(self) -> List[PluginInfo]:
        plugins: List[PluginInfo] = []
        if not self.plugins_path.exists():
            return plugins
        for file in self.plugins_path.glob("*.py"):
            if file.name.startswith("_"):
                continue
            module = f"starlord.plugins.{file.stem}"
            plugins.append(PluginInfo(name=file.stem, module=module))
        return plugins

    def load(self, plugin: PluginInfo):
        return import_module(plugin.module)
