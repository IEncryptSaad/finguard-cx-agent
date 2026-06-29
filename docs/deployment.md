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
