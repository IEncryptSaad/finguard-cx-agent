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

## Enterprise extension SDK foundations

FinGuard extension points are intentionally lightweight so the default free-tier deployment remains usable without paid services.

### AI provider adapters
Provider plugins should expose metadata, health, capabilities, timeout seconds, retry count, and optional streaming. Built-in adapters for OpenAI, Anthropic, Gemini, Groq, Ollama, and OpenRouter remain disabled until their environment variables are configured; `mock` remains the default provider.

### Connector adapters
Connector plugins should validate configuration, report health, and support a demo/test mode with no external SaaS dependency. Current foundations cover webhook, email, Slack, Notion, Google Drive, and Confluence.

### Tool/action plugins
Tools declare input and output schemas, required permissions, side-effect class, and whether human approval is required. Risky tools should return `approval_required` until explicitly approved and every execution is audit logged.

### RAG extensions
The RAG layer starts with local chunking, keyword retrieval, citations, permission filters, and grounded-answer metadata. Future vector databases can replace the retriever behind the same query/index API without requiring embeddings API keys in local mode.

### Prompt extensions
Prompts are versioned records with draft, active, archived, and retired states. Activating a version archives other active versions with the same name; rollback reactivates a previous version and emits audit logs.
