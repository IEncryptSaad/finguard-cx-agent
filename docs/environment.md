# Environment variables

Backend (`apps/api/.env.example`):
- `APP_ENV`: local, preview, or production label.
- `LLM_PROVIDER`: defaults to `mock` and requires no key.
- `CORS_ORIGINS`: comma-separated frontend origins.
- `RATE_LIMIT_PER_MINUTE`: per-IP request limit.
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`: optional persistence configuration.

Frontend (`apps/web/.env.example`):
- `NEXT_PUBLIC_API_BASE_URL`: backend URL.

## RC1 environment checklist

| Variable | Required | Default | Notes |
| --- | --- | --- | --- |
| `APP_ENV` | No | `local` | Use `production` for hosted environments. |
| `LLM_PROVIDER` | No | `mock` | Mock mode requires no API keys. |
| `SUPABASE_URL` | No | unset | Required only when enabling Supabase persistence. |
| `SUPABASE_SERVICE_ROLE_KEY` | No | unset | Never expose this to the frontend or logs. |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated allowed web origins. |
| `RATE_LIMIT_PER_MINUTE` | No | `60` | Can also be adjusted through app settings at runtime. |
| `NEXT_PUBLIC_API_BASE_URL` | Yes for web deploys | `http://localhost:8000` locally | Browser-visible API base URL. |

## Startup v1.0 environment variables

| Variable | Required | Notes |
| --- | --- | --- |
| `APP_ENV` | Production | Set to `production` to enable fail-fast persistence and CORS checks. |
| `AUTH_REQUIRED` | Production | Require header auth outside local development. Production always requires auth. |
| `SUPABASE_URL` | Production | Supabase project URL. |
| `SUPABASE_SERVICE_ROLE_KEY` | Production | Server-only service role key. Never expose to the browser. |
| `CORS_ORIGINS` | Production | Comma-separated explicit origins. Wildcard is rejected in production. |
| `LLM_PROVIDER` | No | Defaults to `mock`, which runs without paid APIs. |
| `FINGUARD_REPOSITORY` | No | `json` (default) or `memory` for tests/local fallback. |
| `FINGUARD_DATA_FILE` | No | Local JSON persistence path, default `.finguard-data.json`. |
