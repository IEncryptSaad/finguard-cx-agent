# Environment variables

Backend (`apps/api/.env.example`):
- `APP_ENV`: local, preview, or production label.
- `LLM_PROVIDER`: defaults to `mock` and requires no key.
- `CORS_ORIGINS`: comma-separated frontend origins.
- `RATE_LIMIT_PER_MINUTE`: per-IP request limit.
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`: optional persistence configuration.

Frontend (`apps/web/.env.example`):
- `NEXT_PUBLIC_API_BASE_URL`: backend URL.
