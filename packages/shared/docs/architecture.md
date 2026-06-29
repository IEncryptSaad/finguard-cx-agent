# Architecture

FinGuard CX Agent is an API-first monorepo with a Next.js customer/admin UI, a FastAPI service, and shared contracts. The backend routes AI work through `AgentOrchestrator`, which composes conversation memory, prompt templates, PII redaction, guardrails, policy evaluation, provider-agnostic AI adapters, audit logging, support ticket creation, and human handoff hooks.

## Plugin-first extension model

Premium and customer-specific features must be added as plugins instead of changing core orchestration. The core plugin interfaces cover:

- AI Providers
- Actions
- Tools
- Integrations
- Knowledge Sources
- Authentication Providers
- Analytics Providers
- Notification Providers

The default AI provider is `mock`, so local development and free-tier deployments do not require paid API keys. OpenAI, Anthropic, Gemini, Groq, Ollama, and OpenRouter adapters are present as disabled-by-default plugins that become selectable only when their environment variables are configured.

## Runtime services

- REST API versioning uses `/api/v1`; OpenAPI is served at `/api/v1/openapi.json` and docs at `/api/v1/docs`.
- Middleware provides structured JSON logging setup, global error responses, CORS, and in-memory rate limiting suitable for free-tier MVP deployments.
- Conversation memory, tickets, knowledge articles, audit logs, and background task records have in-memory implementations with Supabase schema migrations for persistent deployments.

## Data model

The Supabase migration includes users, roles, conversations, conversation messages, tickets, knowledge articles, audit logs, and lifecycle events. This keeps persistence behind service/repository boundaries while allowing the MVP to run without managed database credentials.
