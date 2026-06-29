# Plugin development guide

FinGuard extensions implement the small interfaces in `apps/api/app/plugins/base.py`. Supported plugin categories are AI providers, agent tools, agent actions, integrations, knowledge sources, notification providers, analytics providers, and auth providers.

## Example

`DemoWebhookIntegration` in `apps/api/app/plugins/examples.py` is a working integration plugin. Register plugin instances in `apps/api/app/plugins/registry.py`; orchestration code depends on the plugin interfaces, not concrete paid features.

## Rules

- Keep plugins disabled by default unless they are free and local.
- Read secrets from environment variables only.
- Never return credentials in API responses or audit payloads.
- Add paid/provider-specific behavior in plugin packages without changing `AgentOrchestrator`.

## RC1 plugin compatibility rules

- Keep plugin dependencies inward-facing: plugins may depend on `app.plugins.base` contracts and service-level payloads, but must not import FastAPI route modules or frontend code.
- Preserve existing metadata fields (`name`, `enabled`, `description`) for catalog compatibility.
- Action-like plugins should return serializable dictionaries and handle unavailable external providers gracefully.
- Plugins must not log raw secrets, credentials, card numbers, SSNs, or customer email addresses. Use existing redaction services before writing audit payloads.
- Marketplace entries should use existing plugin kinds: `action`, `workflow`, `ai_provider`, `knowledge_connector`, `analytics`, or `notification`.
