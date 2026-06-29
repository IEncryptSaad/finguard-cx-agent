from app.plugins.base import IntegrationPlugin, PluginMetadata

class DemoWebhookIntegration(IntegrationPlugin):
    metadata = PluginMetadata(name="demo_webhook", enabled=True, description="Example integration plugin for workflow handoffs")
    async def run(self, payload: dict) -> dict:
        return {"delivered": True, "provider": self.metadata.name, "payload_keys": sorted(payload.keys())}
