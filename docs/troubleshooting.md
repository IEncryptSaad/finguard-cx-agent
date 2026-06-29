# Troubleshooting

- `503 AI provider is not configured`: switch `ACTIVE_AI_PROVIDER`/settings to `mock` or provide the provider key.
- Production boot fails: set `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`.
- CORS failures: production requires explicit `CORS_ORIGINS`; wildcard origins are rejected.
- `401/403`: include `X-FinGuard-Role: admin|agent|customer` and a stable `X-FinGuard-Actor`.
- `429`: wait for the free-tier local limiter window or raise `RATE_LIMIT_PER_MINUTE`.
