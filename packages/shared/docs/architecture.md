# Architecture

FinGuard CX Agent is an API-first monorepo with a Next.js customer/admin UI, a FastAPI service, and shared contracts. The backend routes all AI work through an orchestrator that composes PII redaction, guardrails, provider-agnostic LLM adapters, audit logging, support ticket creation, and human handoff hooks.

The default LLM provider is `mock`, so local development and free-tier deployments do not require paid API keys. Supabase integration is isolated behind a repository boundary for later persistence, auth, and realtime features.
