create table if not exists roles (id text primary key, description text);
create table if not exists users (id uuid primary key default gen_random_uuid(), email text unique not null, role text references roles(id) default 'customer', display_name text, created_at timestamptz default now());
create table if not exists conversations (id uuid primary key default gen_random_uuid(), user_id uuid references users(id), status text default 'open', created_at timestamptz default now(), updated_at timestamptz default now());
create table if not exists conversation_messages (id uuid primary key default gen_random_uuid(), conversation_id uuid references conversations(id) on delete cascade, role text not null, content text not null, created_at timestamptz default now());
create table if not exists tickets (id uuid primary key default gen_random_uuid(), conversation_id uuid references conversations(id), summary text not null, status text default 'open', priority text default 'normal', created_at timestamptz default now());
create table if not exists knowledge_articles (id uuid primary key default gen_random_uuid(), title text not null, body text not null, tags text[] default '{}', created_at timestamptz default now(), updated_at timestamptz default now());
create table if not exists audit_logs (id uuid primary key default gen_random_uuid(), event_type text not null, payload jsonb not null default '{}', created_at timestamptz default now());
create table if not exists lifecycle_events (id uuid primary key default gen_random_uuid(), name text not null, payload jsonb not null default '{}', status text default 'queued', created_at timestamptz default now());

-- RC1 hardening: idempotent indexes for operational queries.
create index if not exists idx_conversation_messages_conversation_created on conversation_messages(conversation_id, created_at);
create index if not exists idx_tickets_status_priority on tickets(status, priority);
create index if not exists idx_tickets_conversation on tickets(conversation_id);
create index if not exists idx_knowledge_articles_tags on knowledge_articles using gin(tags);
create index if not exists idx_audit_logs_event_created on audit_logs(event_type, created_at desc);
