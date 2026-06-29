# Security Notes

- Admin and mutation endpoints use `X-FinGuard-Role` and `X-FinGuard-Actor` headers in the built-in free-tier auth shim. Set `AUTH_REQUIRED=true` or `APP_ENV=production` outside local development.
- Roles: `admin` has all permissions; `agent` can read conversations/audit/analytics and update tickets; `customer` can chat and create tickets.
- Redaction covers emails, phone numbers, SSNs, card-like numbers, bank/account/routing identifiers, bearer tokens, API keys, secrets, passwords, passcodes, and PINs before prompts, memory, audit logs, tickets, workflow contexts, and analytics payloads.
- Production CORS fails closed: do not use `*`; set explicit origins.
- Security headers include nosniff, DENY frame policy, no-referrer, permissions policy, and a default CSP.
