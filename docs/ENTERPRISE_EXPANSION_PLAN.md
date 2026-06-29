# Enterprise Expansion Plan

## Purpose

This document defines how FinGuard CX Agent should evolve from the current working startup MVP into an enterprise-grade AI automation and product-management platform while remaining deployable on free-tier infrastructure during the MVP stage.

The plan intentionally separates what should be built now from what can safely run on free-tier services, what requires paid infrastructure later, and what belongs in enterprise-only upgrades.

## Planning principles

- **Keep the MVP deployable without paid services.** The current mock AI provider, in-memory repositories, optional Supabase persistence, and simple Next.js/FastAPI deployment model should remain valid until paid services are deliberately enabled.
- **Extend through stable boundaries.** New enterprise capabilities should attach through service, repository, provider, and plugin interfaces instead of rewriting core orchestration.
- **Prefer operational credibility over feature breadth.** Enterprise buyers need reliability, auditability, security controls, and measurable outcomes more than a large list of shallow features.
- **Separate product management from customer support, but connect their data.** Support conversations, tickets, lifecycle events, product signals, experiments, and roadmap decisions should become linked objects over time.
- **Avoid building expensive infrastructure prematurely.** Vector databases, event warehouses, queues, SSO suites, observability platforms, and paid LLM providers should be optional or delayed until usage justifies them.

## 1. SadaPay job-posting alignment

The expansion should align FinGuard CX Agent with the likely expectations of a fintech product, operations, or AI automation role at SadaPay: customer obsession, product sense, automation, data-informed execution, compliance awareness, and ability to ship pragmatic systems under constraints.

### Relevant alignment themes

- **Fintech-grade customer experience:** Automate support safely for sensitive money-adjacent workflows while preserving human escalation for risk, fraud, account, and trust issues.
- **Product operations mindset:** Convert customer conversations into structured product feedback, themes, feature requests, bugs, and roadmap inputs.
- **AI automation with guardrails:** Use AI to reduce manual work, but keep policy checks, PII handling, escalation rules, and audit trails central.
- **Cross-functional execution:** Provide surfaces for support, product, risk, compliance, and engineering teams to collaborate from the same source of customer truth.
- **Metrics and experimentation:** Track funnel, support, lifecycle, and feature-adoption metrics so teams can quantify impact.
- **Resource-aware delivery:** Demonstrate that the system can start on free-tier infrastructure and scale into paid enterprise components without a full rebuild.

### Must build now

- A clear product narrative connecting support automation, lifecycle messaging, and product insights.
- Documentation of safety boundaries, escalation criteria, and realistic implementation phases.
- Minimal data models that can later support product feedback, lifecycle events, analytics, and audit trails.

### Can build on free tier

- Mocked or rule-based classification of conversation topics, feedback types, and escalation reasons.
- Lightweight admin views for conversations, tickets, audit logs, settings, knowledge articles, and basic analytics.
- Supabase-backed persistence for small pilot deployments.

### Requires paid infrastructure later

- High-volume AI classification and summarization.
- Reliable queue-backed background processing.
- Production observability, incident alerting, and data warehouse sync.

### Enterprise-only future upgrade

- SSO/SAML, SCIM, advanced RBAC, private deployments, compliance reporting, custom retention policies, and dedicated customer environments.

## 2. Current MVP capabilities

The current MVP already establishes a credible platform foundation:

- **Customer chat UI:** A Next.js frontend for customer support chat and an admin dashboard.
- **FastAPI backend:** Versioned API routes for chat, streaming chat, conversations, tickets, knowledge, audit, analytics, settings, plugins, and health.
- **Agent orchestration:** A central orchestrator coordinates memory, PII redaction, guardrails, policy checks, prompt rendering, AI provider calls, audit events, and human handoff.
- **Provider abstraction:** The default `mock` provider keeps the MVP free and keyless while paid or local providers can be enabled through configuration.
- **PII and guardrails foundation:** Redaction, policy checks, and audit logging are already first-class concepts.
- **Ticketing workflow:** Handoff and ticket creation provide the bridge from automation to human support.
- **Knowledge management:** Knowledge articles and ingestion endpoints support early self-service and retrieval workflows.
- **Lifecycle foundation:** Lifecycle event services exist as an early automation base.
- **Plugin-ready structure:** Plugin interfaces are present for providers, actions, tools, integrations, knowledge sources, authentication providers, analytics providers, and notification providers.
- **Supabase-ready persistence:** Migrations and seeds provide a path from in-memory development to free-tier persistent storage.

## 3. Missing capabilities

The MVP is intentionally incomplete for enterprise use. Missing capabilities include:

### Product-management gaps

- Product feedback objects separate from support tickets.
- Feature request capture, deduplication, voting, prioritization, and status tracking.
- Roadmap views, release notes, and customer-impact mapping.
- Links between conversations, customer accounts, product areas, tickets, experiments, and roadmap items.
- Product discovery workflows such as interview notes, opportunity scoring, and customer segments.

### AI automation gaps

- Production-grade retrieval-augmented generation with source citations and freshness controls.
- AI evaluation harnesses, regression tests, and quality scorecards.
- Prompt/version management with approvals and rollbacks.
- Multi-step tool execution with strict permissions and deterministic audit trails.
- Queue-backed asynchronous jobs for summarization, classification, routing, and notifications.

### Support automation gaps

- SLA policies, assignment queues, team inboxes, macros, internal notes, collision detection, and escalation rules.
- Omnichannel ingestion from email, chat widgets, WhatsApp, in-app support, social channels, or call-center systems.
- Customer identity resolution and account-context enrichment.
- CSAT, QA review, and agent-performance workflows.

### Lifecycle messaging gaps

- Campaign builder, audience segmentation, templates, scheduling, throttling, and delivery tracking.
- Multi-channel delivery providers for email, SMS, push, in-app, and WhatsApp.
- Consent management, unsubscribe handling, frequency caps, and localization.

### Analytics and experimentation gaps

- Durable event tracking and event schema governance.
- Funnel, cohort, retention, adoption, and support-deflection dashboards.
- Experiment assignment, metrics attribution, statistical analysis, and guardrail metrics.
- Data warehouse exports and BI integrations.

### Enterprise gaps

- SSO/SAML, SCIM provisioning, organization/workspace isolation, advanced RBAC, and delegated administration.
- Immutable audit logs, exportable compliance reports, retention policies, and legal hold.
- Secrets management, encryption-key management, vulnerability management, and incident workflows.
- HA architecture, queues, managed observability, backups, disaster recovery, and service-level objectives.

## 4. Enterprise-grade target architecture

The long-term architecture should remain modular and plugin-first.

### Target components

1. **Web application**
   - Customer chat widget, support agent workspace, product-management workspace, analytics workspace, and administration console.

2. **API gateway and backend services**
   - FastAPI can remain the primary API service initially.
   - Over time, split high-volume responsibilities into dedicated services only if usage requires it.

3. **Agent orchestration layer**
   - Conversation state, policy checks, tool permissions, prompt templates, provider routing, RAG, evaluation hooks, and audit events.

4. **Workflow automation engine**
   - Rules, triggers, scheduled jobs, human approvals, retry policies, and integration actions.

5. **Operational datastore**
   - Supabase/Postgres for organizations, users, conversations, tickets, feedback, roadmap items, lifecycle campaigns, settings, and audit metadata.

6. **Event and analytics layer**
   - Start with Postgres tables.
   - Later add queue/event streaming, warehouse sync, and BI connectors.

7. **Knowledge and retrieval layer**
   - Start with simple indexed knowledge articles.
   - Later add embeddings, vector search, document permissions, and source-grounded responses.

8. **Integration/plugin layer**
   - Support pluggable AI providers, tools, ticketing systems, CRMs, messaging providers, analytics providers, auth providers, and internal fintech systems.

9. **Security and governance layer**
   - RBAC, audit logs, data retention, encryption, SSO, SCIM, secrets management, and compliance exports.

### Deployment posture

- **MVP/free tier:** Next.js hosting, Python-friendly backend hosting, mock AI provider, in-memory or Supabase free-tier persistence.
- **Growth/paid:** Managed Postgres, object storage, queue workers, paid AI provider, observability, backups, and custom domains.
- **Enterprise:** Isolated tenant environments, SSO/SAML, SCIM, private networking, regional data controls, audit exports, and formal SLOs.

## 5. AI automation features

### Must build now

- Rule-based routing for high-risk support topics.
- Conversation summarization interface using mock or optional provider output.
- Clear fallback behavior when no real AI provider is configured.
- Prompt and policy documentation for support-safe AI behavior.

### Can build on free tier

- Lightweight topic classification using rules or low-volume configured AI providers.
- Suggested replies for support agents.
- Knowledge-article search and answer drafting.
- Ticket summarization and suggested priority.
- Basic AI usage logs and quality flags.

### Requires paid infrastructure later

- High-volume LLM calls for every conversation.
- Embedding generation and vector search at scale.
- Continuous AI evaluation pipelines.
- Background AI workers for bulk summarization and enrichment.
- Provider fallback, load balancing, and cost controls.

### Enterprise-only future upgrade

- Customer-specific fine-tuning or private model hosting.
- Approval workflows for AI tool execution.
- Full AI governance dashboards.
- Model-risk reporting, red-team evaluation, and regulated workflow controls.

## 6. Product-management features

### Must build now

- Document the product-management data model: feedback, feature request, product area, customer segment, roadmap item, release note, and experiment.
- Design how support conversations become product signals.
- Define admin navigation for future product workspaces without implementing full UI yet.

### Can build on free tier

- Convert support tickets or conversations into product feedback records.
- Tag feedback by product area, sentiment, customer segment, and urgency.
- Simple feature request list with status values such as `new`, `triaged`, `planned`, `in_progress`, `launched`, and `closed`.
- Basic roadmap board backed by Postgres/Supabase.
- Release note drafts generated from completed roadmap items.

### Requires paid infrastructure later

- Large-scale deduplication and semantic clustering of feedback.
- Customer revenue/usage enrichment from CRM or billing systems.
- Advanced prioritization models using product analytics and support cost.
- Data warehouse-backed reporting.

### Enterprise-only future upgrade

- Multi-workspace roadmap governance.
- Approval workflows for roadmap changes.
- Portfolio-level planning, OKR alignment, and executive reporting.
- Customer advisory board portals and private customer roadmap views.

## 7. Customer-support automation features

### Must build now

- Preserve human handoff for sensitive or uncertain cases.
- Maintain audit events for automated decisions.
- Keep ticketing workflows simple and transparent.

### Can build on free tier

- SLA fields and simple priority rules.
- Agent assignment, internal notes, and status transitions.
- Saved replies/macros.
- Basic CSAT capture after ticket closure.
- Auto-tagging and simple escalation rules.

### Requires paid infrastructure later

- Multi-channel support ingestion.
- Queue-backed notification delivery.
- Team inbox collision detection and real-time collaboration.
- Integration with Zendesk, Intercom, Salesforce, HubSpot, Slack, WhatsApp, or email providers.

### Enterprise-only future upgrade

- Workforce management.
- Quality assurance scoring and reviewer workflows.
- Advanced routing by skill, region, risk, customer tier, and compliance queue.
- Dedicated support operations analytics.

## 8. Lifecycle messaging features

### Must build now

- Keep lifecycle events as a core concept.
- Define event types such as signup, onboarding step completed, first support contact, ticket closed, feature adopted, inactivity detected, and renewal risk detected.
- Define safety rules for customer messaging, consent, throttling, and auditability.

### Can build on free tier

- Manual or rule-triggered lifecycle events.
- Basic in-app notification or admin-visible message drafts.
- Simple email provider plugin behind an optional configuration flag.
- Message templates stored in the database.
- Basic delivery status fields.

### Requires paid infrastructure later

- Reliable scheduled delivery workers.
- Email/SMS/WhatsApp/push provider costs.
- Segmentation across large customer datasets.
- Delivery analytics and bounce/unsubscribe webhooks.

### Enterprise-only future upgrade

- Journey builder with branching logic.
- Multi-region delivery controls.
- Consent and preference center with legal/audit workflows.
- AI-personalized lifecycle campaigns with approval controls.

## 9. Analytics and experimentation features

### Must build now

- Define core metrics and event names before adding complex dashboards.
- Track basic support, AI, ticket, lifecycle, and knowledge events.
- Keep analytics implementation simple enough for Postgres/Supabase.

### Can build on free tier

- Admin dashboard cards for ticket volume, handoff rate, knowledge usage, response latency, CSAT, and top topics.
- Simple event table with typed event names and JSON metadata.
- Export CSV for conversations, tickets, audit logs, and feedback.
- Manual experiment records with status, hypothesis, audience, and success metrics.

### Requires paid infrastructure later

- Warehouse-grade event ingestion.
- Funnel, cohort, retention, and attribution queries over large datasets.
- A/B assignment service and metric computation jobs.
- BI integrations and scheduled reports.

### Enterprise-only future upgrade

- Experiment governance and approval workflows.
- Guardrail-metric monitoring for regulated product changes.
- Cross-product analytics with row-level security by business unit.
- Executive dashboards and compliance-ready reporting packs.

## 10. Security, audit, compliance, and RBAC roadmap

### Must build now

- Keep PII redaction, guardrails, and audit logging in the default request path.
- Define roles such as `admin`, `support_manager`, `support_agent`, `product_manager`, `analyst`, `compliance_reviewer`, and `viewer`.
- Document permission boundaries for conversations, tickets, knowledge, feedback, settings, plugins, analytics, and audit logs.
- Avoid storing secrets in source code or frontend-visible variables.

### Can build on free tier

- Basic role checks in API routes.
- Organization/workspace IDs in persisted records.
- Audit log filters and export.
- Configurable data-retention settings with best-effort deletion jobs.
- Local development security checklist.

### Requires paid infrastructure later

- Managed secret storage.
- Automated backups and point-in-time restore.
- Production vulnerability scanning.
- Centralized logs and alerting.
- Encryption-key management beyond platform defaults.

### Enterprise-only future upgrade

- SSO/SAML, OIDC enterprise auth, SCIM provisioning, and just-in-time user creation.
- Advanced RBAC with custom roles and field-level permissions.
- Immutable audit log storage.
- Legal hold, retention policies by data type, and compliance exports.
- SOC 2 readiness program, penetration testing, vendor risk management, and incident response playbooks.

## 11. Extensibility/plugin roadmap

### Must build now

- Keep all non-core capabilities behind plugin or provider interfaces.
- Document plugin contracts and examples.
- Avoid hard-coding a single AI, analytics, messaging, auth, or ticketing vendor.

### Can build on free tier

- Local plugin registry display.
- Example plugins for mock AI, simple actions, basic analytics, and simple notification stubs.
- Plugin configuration validation.
- Disabled-by-default provider plugins that activate only when environment variables are present.

### Requires paid infrastructure later

- Marketplace-style plugin management.
- Signed plugin bundles and version compatibility checks.
- Sandboxed plugin execution.
- Paid third-party API integrations.

### Enterprise-only future upgrade

- Private customer plugin repositories.
- Tenant-specific integration allowlists.
- Custom workflow actions for internal systems.
- Integration certification and security review workflows.

## 12. Free-tier-compatible implementation phases

### Phase 0: Current MVP stabilization

**Goal:** Keep the working startup MVP reliable and easy to demo.

**Must build now:**

- Improve documentation for architecture, deployment, security boundaries, and product direction.
- Add smoke tests for core API flows if missing.
- Keep mock AI as the default.
- Ensure the app still runs locally without Docker or paid API keys.

**Do not build yet:**

- Complex queues, vector databases, paid messaging, or enterprise auth.

### Phase 1: Product signal capture

**Goal:** Turn support conversations into product-management inputs.

**Can build on free tier:**

- Feedback records linked to conversations and tickets.
- Basic tags, product areas, sentiment, and priority.
- Admin list views and filters.
- CSV export.

**Success metric:** Product managers can review top customer pain points without reading every conversation.

### Phase 2: Support operations depth

**Goal:** Make the support workflow useful for a small team.

**Can build on free tier:**

- SLA fields, assignment, internal notes, macros, status transitions, and CSAT.
- Basic analytics cards for support volume, handoff rate, and top issues.

**Success metric:** A small team can manage tickets from the admin dashboard rather than only demoing chat.

### Phase 3: Lifecycle messaging foundation

**Goal:** Start controlled customer communication without expensive infrastructure.

**Can build on free tier:**

- Lifecycle event records.
- Message templates.
- Draft or manual-send workflows.
- Optional low-volume email plugin.

**Success metric:** Teams can create lifecycle messages from observed support/product events while preserving consent and auditability.

### Phase 4: AI quality and retrieval

**Goal:** Improve AI usefulness without losing control.

**Can build on free tier for pilots:**

- Knowledge search improvements.
- Suggested replies.
- AI summary fields.
- Human feedback on AI responses.

**Requires paid infrastructure for scale:**

- Production LLM usage, embeddings, vector search, evaluation jobs, and background workers.

**Success metric:** AI suggestions reduce support effort while escalation and quality controls remain visible.

### Phase 5: Paid growth infrastructure

**Goal:** Move from demo/pilot to production usage.

**Requires paid infrastructure:**

- Managed Postgres plan, backups, queue workers, object storage, observability, real provider APIs, and custom domains.
- Background tasks for notifications, summarization, classification, and exports.

**Success metric:** The system handles production traffic with basic reliability, monitoring, and recovery.

### Phase 6: Enterprise readiness

**Goal:** Support larger customers and regulated procurement.

**Enterprise-only future upgrade:**

- SSO/SAML, SCIM, custom RBAC, immutable audit logs, private deployment, security reviews, compliance exports, and formal SLAs/SLOs.

**Success metric:** Enterprise buyers can evaluate the platform against security, compliance, operational, and integration requirements.

## 13. Paid upgrade path

The paid upgrade path should be incremental and reversible where possible.

### First paid upgrades

1. **Managed database tier**
   - Upgrade Supabase/Postgres for storage, backups, retention, and higher limits.

2. **Production AI provider**
   - Enable OpenAI, Anthropic, Gemini, Groq, OpenRouter, Ollama, or an enterprise provider based on cost, latency, privacy, and quality needs.

3. **Background workers and queues**
   - Add reliable processing for summarization, notifications, ingestion, exports, and analytics rollups.

4. **Object storage**
   - Store uploaded documents, transcripts, exports, and attachments.

5. **Observability**
   - Add error tracking, structured logs, metrics, traces, uptime checks, and alerting.

6. **Messaging providers**
   - Add paid email, SMS, WhatsApp, push, or in-app messaging services.

7. **Search and retrieval**
   - Add embeddings, vector search, document chunking, and retrieval evaluation.

### Enterprise monetization path

- Per-seat pricing for support/product/admin users.
- Usage-based AI automation credits.
- Add-ons for lifecycle messaging, analytics, advanced AI, and integrations.
- Enterprise plans for SSO, SCIM, audit exports, private deployment, custom retention, premium support, and compliance support.

## 14. Features that must NOT be built yet because they exceed free-tier/budget constraints

The following features should be explicitly deferred until a paid pilot, revenue commitment, or enterprise requirement justifies them:

- Production-scale vector database or managed semantic search.
- Always-on paid LLM calls for every message.
- Fine-tuned or privately hosted models.
- Real-time event streaming platforms such as Kafka or equivalent managed services.
- Large-scale data warehouse, reverse ETL, or BI stack.
- Full journey builder with branching lifecycle campaigns.
- Paid SMS, WhatsApp, or push notification delivery at scale.
- Omnichannel support integrations requiring vendor contracts.
- Marketplace plugin infrastructure with signed bundles and sandbox execution.
- SSO/SAML, SCIM, custom RBAC, and enterprise identity governance.
- Immutable audit storage, legal hold, and formal compliance automation.
- Multi-region high availability, private networking, and dedicated tenant environments.
- Full SOC 2 program, penetration testing, and vendor-risk automation.
- Advanced experimentation platform with automated statistical analysis.
- Workforce management and complex contact-center routing.

## Recommended immediate next steps

1. Keep this document as the enterprise direction baseline.
2. Add a lightweight product-signal data model before building a full roadmap UI.
3. Extend existing analytics with support and AI quality metrics that fit Postgres/Supabase.
4. Preserve mock/free-tier defaults for every new feature.
5. Only introduce paid services behind optional configuration and plugin boundaries.
