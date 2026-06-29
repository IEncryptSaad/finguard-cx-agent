# Plugin development guide

FinGuard extensions implement the small interfaces in `apps/api/app/plugins/base.py`. Supported plugin categories are AI providers, agent tools, agent actions, integrations, knowledge sources, notification providers, analytics providers, and auth providers.

## Example

`DemoWebhookIntegration` in `apps/api/app/plugins/examples.py` is a working integration plugin. Register plugin instances in `apps/api/app/plugins/registry.py`; orchestration code depends on the plugin interfaces, not concrete paid features.

## Rules

- Keep plugins disabled by default unless they are free and local.
- Read secrets from environment variables only.
- Never return credentials in API responses or audit payloads.
- Add paid/provider-specific behavior in plugin packages without changing `AgentOrchestrator`.
