# Architecture

The FastAPI backend exposes versioned endpoints for chat, streaming chat, conversations, tickets, knowledge, audit logs, analytics, settings, plugins, and health checks. `AgentOrchestrator` coordinates request flow: redact PII and credentials, evaluate guardrails and policy, persist safe conversation history, call the active AI provider, create handoff tickets, and write audit/analytics events.

The Next.js frontend provides customer chat and an admin dashboard. Storage currently uses lightweight in-memory repositories with Supabase migrations included for free-tier persistence. Extension points live under `apps/api/app/plugins` so new providers or paid capabilities can be added without refactoring core orchestration.

## RC1 architecture validation

FinGuard RC1 preserves the existing monorepo architecture and keeps runtime extension points behind narrow boundaries:

- API traffic enters through the versioned `/api/v1` FastAPI router before reaching service modules or the agent orchestrator.
- Agent orchestration depends on service interfaces and provider abstractions; plugins do not import route handlers or web UI code.
- Plugin types remain backward compatible through the existing `Plugin`, `AIProvider`, and `ActionPlugin` base classes. New plugin categories should subclass the existing abstractions instead of creating route-level dependencies.
- Workflow execution records skipped and failed executions instead of surfacing raw exceptions to callers.
- Persistence remains idempotent: migrations use `create table if not exists` and RC1 indexes use `create index if not exists`.

Dependency direction should remain: `apps/web -> apps/api HTTP contracts -> app/api -> app/services|app/agent -> app/plugins|app/db`. Reverse imports from services/plugins into route modules or frontend packages are not allowed.

## Startup v1.0 architecture additions

- Route handlers now use injectable auth dependencies and repository/service boundaries instead of relying solely on process-local mutable state.
- The repository adapter supports deterministic in-memory tests, local JSON persistence, and a Supabase/Postgres production contract. Production startup fails fast without Supabase credentials.
- SSE streaming emits provider-compatible events: `metadata`, `message.delta`, `message.done`, and `error`; non-streaming `/chat` remains backward compatible.
- Redaction is centralized in `app.services.security` and is applied before prompts, memory, audit payloads, ticket summaries, workflow contexts, and analytics data.
- List endpoints support bounded pagination (`paginated=true&page=1&page_size=50`) while preserving legacy list responses by default.
