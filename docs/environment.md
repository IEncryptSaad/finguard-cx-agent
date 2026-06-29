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
