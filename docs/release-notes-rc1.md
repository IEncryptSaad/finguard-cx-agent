# FinGuard CX Agent RC1 release notes

## Readiness checklist

- [x] Versioned API remains under `/api/v1` with OpenAPI at `/api/v1/openapi.json` and docs at `/api/v1/docs`.
- [x] Standard error envelopes are returned for validation, HTTP, and internal errors.
- [x] Knowledge uploads reject unsupported file types and oversized documents.
- [x] Workflow failures are recorded as failed executions without crashing callers.
- [x] Supabase migrations include idempotent indexes for common operational queries.
- [x] Mock mode remains keyless and suitable for free-tier demos.
- [x] Plugin contracts remain backward compatible.

## Known limitations

- The default runtime still uses in-memory services unless Supabase persistence is wired into the deployment.
- Authentication/RBAC structures are present, but route-level auth middleware is intentionally minimal for MVP deployments.
- PDF ingestion uses simple text extraction and should be replaced with a richer parser before heavy production document ingestion.
- External provider plugins must be configured and tested individually before being enabled in production.

## Suggested roadmap

### RC2

- Wire Supabase repositories behind service interfaces for persistent conversations, tickets, audit logs, and knowledge articles.
- Add route-level authentication and RBAC enforcement for admin, settings, audit, and marketplace endpoints.
- Add CI checks for import cycles and OpenAPI contract diffs.

### v1.0

- Add production observability dashboards, structured metrics, and alerting.
- Add tenant isolation and organization-level policy controls.
- Certify provider plugins with resilience tests, timeout budgets, and secret scanning.
