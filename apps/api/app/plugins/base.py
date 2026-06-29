from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol

@dataclass(frozen=True)
class PluginMetadata:
    name: str
    enabled: bool = False
    description: str = ""

class Plugin(ABC):
    metadata: PluginMetadata

class AIProvider(Plugin, ABC):
    @abstractmethod
    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str: ...

class ActionPlugin(Plugin, ABC):
    @abstractmethod
    async def run(self, payload: dict[str, Any]) -> dict[str, Any]: ...

class ToolPlugin(ActionPlugin): pass
class IntegrationPlugin(ActionPlugin): pass
class KnowledgeSourcePlugin(ActionPlugin): pass
class AuthenticationProviderPlugin(ActionPlugin): pass
class AnalyticsProviderPlugin(ActionPlugin): pass
class NotificationProviderPlugin(ActionPlugin): pass

class WorkflowPlugin(ActionPlugin): pass
class MarketplacePluginBundle(Plugin, ABC): pass
