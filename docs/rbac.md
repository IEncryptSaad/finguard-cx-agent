# RBAC

Local requests can omit headers unless `AUTH_REQUIRED=true`. Production always requires auth headers.

```bash
curl -H 'X-FinGuard-Role: admin' -H 'X-FinGuard-Actor: alice@example.com' http://localhost:8000/api/v1/admin/summary
curl -H 'X-FinGuard-Role: agent' http://localhost:8000/api/v1/tickets
```

Protected areas: settings, audit, marketplace install, workflow mutations, roadmap mutations, knowledge mutations, ticket mutations, analytics/admin routes, and plugin configuration routes.
