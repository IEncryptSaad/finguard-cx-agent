# Architecture

The FastAPI backend exposes versioned endpoints for chat, streaming chat, conversations, tickets, knowledge, audit logs, analytics, settings, plugins, and health checks. `AgentOrchestrator` coordinates request flow: redact PII and credentials, evaluate guardrails and policy, persist safe conversation history, call the active AI provider, create handoff tickets, and write audit/analytics events.

The Next.js frontend provides customer chat and an admin dashboard. Storage currently uses lightweight in-memory repositories with Supabase migrations included for free-tier persistence. Extension points live under `apps/api/app/plugins` so new providers or paid capabilities can be added without refactoring core orchestration.
