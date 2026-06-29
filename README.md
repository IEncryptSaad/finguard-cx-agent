# FinGuard CX Agent

Production-ready, modular AI agent MVP for secure customer support, workflow automation, and enterprise AI applications. The project is designed to run locally without Docker and without paid API keys.

## Monorepo layout

```text
apps/
  web/        Next.js + Tailwind frontend for customer chat and admin shell
  api/        FastAPI backend with modular agent services
packages/
  shared/     shared TypeScript contracts, schemas, and architecture docs
```

## Features

- Next.js customer chat UI, conversation-aware ticket creation, and responsive admin dashboard with conversation, ticket, audit, knowledge, and settings panels.
- FastAPI backend with typed Pydantic request/response models.
- Mock LLM provider enabled by default; no paid APIs required. Disabled-by-default OpenAI, Anthropic, Gemini, Groq, Ollama, and OpenRouter provider plugins can be enabled by environment variables.
- Provider-agnostic LLM adapter boundary for future OpenAI, Anthropic, local, or enterprise providers.
- PII redaction, guardrails, audit logging, human handoff, and support ticket workflows.
- RBAC-ready auth structure.
- Supabase-ready schema, migrations, seed data, and repository boundary for database/auth/realtime persistence.
- Lifecycle event automation foundation.
- Shared schemas and TypeScript types for frontend/backend alignment.

## Local setup

### Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Run backend tests:

```bash
cd apps/api
pytest
```

### Frontend

```bash
npm install
cp apps/web/.env.example apps/web/.env.local
npm run dev:web
```

Open `http://localhost:3000` for chat and `http://localhost:3000/admin` for the admin shell.

## Configuration

Backend environment variables live in `apps/api/.env.example`:

- `LLM_PROVIDER=mock` keeps the app free and keyless.
- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are optional until persistence is enabled.
- `CORS_ORIGINS` controls browser access to the API.

Frontend environment variables live in `apps/web/.env.example`:

- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` points the UI at the FastAPI app.

## Architecture notes

Requests enter the versioned FastAPI router and are delegated to `AgentOrchestrator`. The orchestrator records conversation memory, redacts PII, applies guardrails and policy checks, renders prompt templates, calls the configured provider plugin, records audit events, and creates high-priority tickets when human handoff is required. Storage and external integrations are intentionally behind narrow service and plugin boundaries so premium AI providers, tools, integrations, knowledge sources, auth providers, analytics, and notifications can be installed without architectural rewrites. OpenAPI docs are available at `/api/v1/docs`.


## MVP endpoint checklist

- `POST /api/v1/chat` and `POST /api/v1/chat/stream` for customer support.
- `GET /api/v1/conversations` and `/conversations/{id}/messages` for admin history.
- `GET/POST/PATCH /api/v1/tickets` for lifecycle and human handoff.
- `GET/POST/PUT/DELETE /api/v1/knowledge`, `GET /api/v1/knowledge?q=...`, and `POST /api/v1/knowledge/ingest` for TXT, Markdown, simple PDF text extraction, and DOCX ingestion.
- `GET /api/v1/audit`, `/analytics`, `/settings`, `/plugins`, and `/health` for operations.

## Documentation

- Architecture: `docs/architecture.md`
- Plugin guide: `docs/plugin-development.md`
- Environment variables: `docs/environment.md`
- Deployment: `docs/deployment.md`
- Supabase schema: `apps/api/supabase/migrations/001_mvp_schema.sql` and `apps/api/supabase/seed.sql`

## Free-tier deployment

- Deploy `apps/api` to a free Python-friendly platform with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Deploy `apps/web` to a free Next.js platform and set `NEXT_PUBLIC_API_BASE_URL` to the backend URL.
- Keep `LLM_PROVIDER=mock` until a real provider is intentionally configured.
- Add Supabase free-tier credentials only when persistent storage is needed.

## Supabase schema

Run `apps/api/supabase/migrations/001_mvp_schema.sql` and `apps/api/supabase/seed.sql` in Supabase SQL editor for persistent free-tier deployments.

## RC1 production-readiness notes

FinGuard CX Agent RC1 focuses on hardening the existing MVP without changing the architecture. The API is versioned under `/api/v1`, OpenAPI is available at `/api/v1/openapi.json`, standard error responses use the shared `ErrorResponse` shape, and mock mode remains the default so the app runs from a clean clone without paid API keys.

See `docs/release-notes-rc1.md` for the RC1 readiness checklist, known limitations, and RC2/v1.0 roadmap.

## Startup v1.0 (M1)

This branch promotes FinGuard CX Agent from RC1 into a deployable v1.0 foundation:

- Repository-backed persistence with local JSON/in-memory fallback and production Supabase fail-fast checks.
- Auth/RBAC guards for admin and mutation routes using free-tier header auth (`X-FinGuard-Role`, `X-FinGuard-Actor`).
- Provider-compatible SSE chat streaming (`message.delta`, `message.done`, `error`, `metadata`).
- Standard API errors, provider health degradation, stronger PII/credential redaction, security headers, and production CORS validation.
- Bounded pagination on list/admin endpoints.
- Support workspace APIs for conversation details, message history, ticket assignment/status/priority/internal notes, AI draft display, and audit trail.
- GitHub Actions for API tests, frontend type checks, and lint.

### Local run

```bash
npm install
pip install -r apps/api/requirements.txt
npm run dev:api
npm run dev:web
```

Mock LLM mode is the default and requires no API keys.

### Tests

```bash
npm run test:api
npm --workspace apps/web exec tsc -- --noEmit
npm --workspace apps/web run lint
```

### Production environment

Production requires Supabase/Postgres credentials and explicit CORS origins:

```bash
APP_ENV=production
AUTH_REQUIRED=true
SUPABASE_URL=https://...
SUPABASE_SERVICE_ROLE_KEY=...
CORS_ORIGINS=https://your-vercel-app.vercel.app
LLM_PROVIDER=mock
```

See `docs/supabase-setup.md`, `docs/deployment.md`, `docs/security.md`, `docs/rbac.md`, and `docs/troubleshooting.md`.
