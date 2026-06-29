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
