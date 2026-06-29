-- Startup v1.0 hardening: idempotent persistence extensions and list indexes.
alter table tickets add column if not exists assignee text;
alter table tickets add column if not exists internal_notes jsonb not null default '[]';
alter table tickets add column if not exists updated_at timestamptz not null default now();
alter table audit_logs add column if not exists actor text;
create table if not exists app_settings (id text primary key default 'default', value jsonb not null, updated_at timestamptz not null default now());
create table if not exists marketplace_installs (name text primary key, kind text not null, enabled boolean not null default true, description text not null default '', updated_at timestamptz not null default now());
create table if not exists analytics_events (id uuid primary key default gen_random_uuid(), event_type text not null, payload jsonb not null default '{}', actor text, created_at timestamptz not null default now());
create table if not exists rate_limit_events (id uuid primary key default gen_random_uuid(), key text not null, path text not null, allowed boolean not null, created_at timestamptz not null default now());
create index if not exists idx_conversations_status_updated on conversations(status, updated_at desc);
create index if not exists idx_conversation_messages_conversation_created_desc on conversation_messages(conversation_id, created_at desc);
create index if not exists idx_tickets_assignee_status_updated on tickets(assignee, status, updated_at desc);
create index if not exists idx_knowledge_articles_title on knowledge_articles(title);
create index if not exists idx_product_items_status_priority_updated on product_items(status, priority, updated_at desc);
create index if not exists idx_feedback_created on feedback_classifications(created_at desc);
create index if not exists idx_analytics_events_type_created on analytics_events(event_type, created_at desc);
create index if not exists idx_rate_limit_events_key_created on rate_limit_events(key, created_at desc);
