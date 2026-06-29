# FinGuard Automation Plugin SDK Example

This lightweight example shows the stable plugin contract for third-party developers. Plugins are local Python classes, need no paid services, and can provide actions, workflows, AI providers, knowledge connectors, analytics, or notifications.

```python
from app.plugins.base import ActionPlugin, PluginMetadata

class NotifyOps(ActionPlugin):
    metadata = PluginMetadata(name="notify_ops", enabled=True, description="Notify operations about workflow events")

    async def run(self, payload: dict) -> dict:
        return {"delivered": True, "payload": payload}
```

Register your plugin with `app.plugins.registry.registry.register(NotifyOps())`, then call it from workflow actions using `custom_plugin_action`.
