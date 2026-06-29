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

- Next.js customer chat UI and admin dashboard shell.
- FastAPI backend with typed Pydantic request/response models.
- Mock LLM provider enabled by default; no paid APIs required.
- Provider-agnostic LLM adapter boundary for future OpenAI, Anthropic, local, or enterprise providers.
- PII redaction, guardrails, audit logging, human handoff, and support ticket workflows.
- RBAC-ready auth structure.
- Supabase-ready repository boundary for later database/auth/realtime persistence.
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

Requests enter the FastAPI router and are delegated to `AgentOrchestrator`. The orchestrator redacts PII, applies guardrails, calls the configured LLM provider, records audit events, and creates high-priority tickets when human handoff is required. Storage and external integrations are intentionally behind narrow service boundaries so the MVP can later add paid LLMs, RAG, multi-agent routing, enterprise tools, analytics, and client-specific workflows.

## Free-tier deployment

- Deploy `apps/api` to a free Python-friendly platform with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- Deploy `apps/web` to a free Next.js platform and set `NEXT_PUBLIC_API_BASE_URL` to the backend URL.
- Keep `LLM_PROVIDER=mock` until a real provider is intentionally configured.
- Add Supabase free-tier credentials only when persistent storage is needed.
