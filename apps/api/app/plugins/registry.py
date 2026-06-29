from collections import defaultdict
from typing import TypeVar, Generic
from app.plugins.base import Plugin
T = TypeVar('T', bound=Plugin)
class PluginRegistry(Generic[T]):
    def __init__(self): self._plugins: dict[str, T] = {}
    def register(self, plugin: T): self._plugins[plugin.metadata.name] = plugin; return plugin
    def get(self, name: str) -> T: return self._plugins[name]
    def enabled(self) -> list[T]: return [p for p in self._plugins.values() if p.metadata.enabled]
    def all(self) -> list[T]: return list(self._plugins.values())
