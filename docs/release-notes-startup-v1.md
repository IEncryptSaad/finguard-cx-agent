# Startup v1.0 Release Notes

Milestone M1 upgrades the RC1 demo into a startup-grade foundation: authenticated admin APIs, repository-backed persistence, provider-safe streaming chat, safer redaction, bounded pagination, security headers, CI, and deployment documentation for Vercel + Render + Supabase free tier.

Known limitations: the default local repository is JSON/in-memory for free local development. Production must use Supabase/Postgres credentials and fails fast if they are missing. Shared rate limiting remains pluggable and free-tier safe; the built-in limiter is process-local unless backed by future Postgres event checks.
