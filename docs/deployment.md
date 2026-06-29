# Free-tier deployment

## Backend: Render
1. Create a free Web Service from this repo.
2. Root directory: `apps/api`.
3. Build command: `pip install -r requirements.txt`.
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. Environment: `LLM_PROVIDER=mock`, `CORS_ORIGINS=https://your-vercel-app.vercel.app`.

## Frontend: Vercel
1. Import the repo.
2. Framework preset: Next.js.
3. Root directory: `apps/web`.
4. Set `NEXT_PUBLIC_API_BASE_URL` to the Render backend URL.

## Database: Supabase
Run `apps/api/supabase/migrations/001_mvp_schema.sql`, then `apps/api/supabase/seed.sql`. The MVP still runs without Supabase using in-memory mock storage.

## RC1 free-tier deployment verification

### Backend on Render Free

- Root directory: `apps/api`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Required for keyless mock mode: `LLM_PROVIDER=mock`
- Optional persistence: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`

### Frontend on Vercel Free

- Project root: `apps/web`
- Framework preset: Next.js
- Set `NEXT_PUBLIC_API_BASE_URL` to the Render backend URL.

### Supabase from scratch

Run migrations in order from `apps/api/supabase/migrations`, then run `apps/api/supabase/seed.sql`. Migrations and RC1 indexes are idempotent, so rerunning them is safe during setup validation.

### Mock mode

Mock mode is the supported RC1 default and works without paid API keys. Keep `LLM_PROVIDER=mock` unless a provider plugin has been explicitly configured and tested.

## Vercel + Render + Supabase free-tier deployment

1. **Supabase:** create a free project and run all SQL files in `apps/api/supabase/migrations` in order.
2. **Render API:** create a free web service from this repo with start command `cd apps/api && uvicorn app.main:app --host 0.0.0.0 --port $PORT` and env vars from `docs/environment.md`.
3. **Vercel Web:** create a free Vercel project for `apps/web`; set `NEXT_PUBLIC_API_BASE_URL` to the Render API URL.
4. **Auth:** send `X-FinGuard-Role`/`X-FinGuard-Actor` from any admin integration while the free-tier header shim is in use.
5. **Mock LLM:** keep `LLM_PROVIDER=mock` to avoid paid APIs. Non-mock providers safely report degraded/unconfigured status if keys are missing.
6. **Validation:** check `/api/v1/health`, run customer chat, and verify admin routes require auth in production.
