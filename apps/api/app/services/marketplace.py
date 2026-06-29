from app.models.schemas import MarketplaceInstallRequest, MarketplacePlugin
from app.services.audit import log_event
_INSTALLED: dict[str, MarketplacePlugin] = {
    "demo_webhook": MarketplacePlugin(name="demo_webhook", kind="notification", enabled=True, description="Posts workflow events to a webhook-compatible endpoint."),
    "mock_ai_provider": MarketplacePlugin(name="mock_ai_provider", kind="ai_provider", enabled=True, description="Free local mock AI provider for demos and tests."),
}
def list_marketplace() -> list[MarketplacePlugin]: return list(_INSTALLED.values())
def install_plugin(payload: MarketplaceInstallRequest) -> MarketplacePlugin:
    plugin = MarketplacePlugin(name=payload.name, kind=payload.kind, enabled=payload.enabled, description=f"Installed {payload.kind} plugin")
    _INSTALLED[plugin.name] = plugin; log_event("plugin.installed", plugin.model_dump()); return plugin
