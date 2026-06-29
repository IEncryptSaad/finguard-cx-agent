# Supabase Setup

1. Create a free Supabase project.
2. Run `apps/api/supabase/migrations/001_mvp_schema.sql`, `002_automation_platform.sql`, and `003_startup_v1.sql` in order.
3. Configure Render environment variables:
   - `APP_ENV=production`
   - `SUPABASE_URL=...`
   - `SUPABASE_SERVICE_ROLE_KEY=...`
   - `CORS_ORIGINS=https://your-vercel-app.vercel.app`
   - `LLM_PROVIDER=mock` for no-cost mock mode.
4. Startup is idempotent: migrations use `if not exists` and seed data is safe to rerun.
