-- Enterprise extension foundations; all tables are optional/free-tier compatible.
create table if not exists workspaces (
  id text primary key,
  organization_id text not null default 'default-org',
  name text not null,
  deployment_profile text not null default 'free-tier',
  created_at timestamptz not null default now()
);

alter table conversations add column if not exists workspace_id text not null default 'default';
alter table tickets add column if not exists workspace_id text not null default 'default';
alter table audit_logs add column if not exists workspace_id text not null default 'default';

create table if not exists provider_usage_logs (
  id uuid primary key default gen_random_uuid(),
  workspace_id text not null default 'default',
  provider text not null,
  capability text not null default 'chat',
  latency_ms numeric not null default 0,
  estimated_tokens integer not null default 0,
  estimated_cost numeric not null default 0,
  status text not null default 'succeeded',
  created_at timestamptz not null default now()
);

create table if not exists connector_statuses (
  name text primary key,
  workspace_id text not null default 'default',
  enabled boolean not null default false,
  status text not null default 'disabled',
  last_checked_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists rag_chunks (
  id uuid primary key default gen_random_uuid(),
  workspace_id text not null default 'default',
  source_id text not null,
  source_type text not null default 'knowledge_article',
  chunk_index integer not null default 0,
  text text not null,
  metadata jsonb not null default '{}'::jsonb,
  permissions text[] not null default '{}',
  created_at timestamptz not null default now()
);

create table if not exists prompt_versions (
  id uuid primary key default gen_random_uuid(),
  workspace_id text not null default 'default',
  name text not null,
  version integer not null,
  category text not null default 'general',
  template text not null,
  config jsonb not null default '{}'::jsonb,
  status text not null default 'draft',
  evaluation_hooks text[] not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(workspace_id, name, version)
);

create table if not exists tool_executions (
  id uuid primary key default gen_random_uuid(),
  workspace_id text not null default 'default',
  tool_name text not null,
  status text not null,
  side_effect text not null default 'none',
  approval_required boolean not null default false,
  input jsonb not null default '{}'::jsonb,
  output jsonb not null default '{}'::jsonb,
  error text,
  created_at timestamptz not null default now()
);

create table if not exists secret_references (
  name text primary key,
  workspace_id text not null default 'default',
  storage text not null default 'environment_or_redacted',
  redacted_value text not null default '[REDACTED_SECRET]',
  updated_at timestamptz not null default now()
);
