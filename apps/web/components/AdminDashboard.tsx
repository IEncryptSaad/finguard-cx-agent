'use client';

import { useMemo, useState } from 'react';
import type { Conversation, KnowledgeArticle, Message, Ticket } from '../lib/api';

type AuditLog = { event_type: string; payload: Record<string, unknown>; created_at: string };
type MessageMap = Record<string, Message[]>;

type Props = {
  summary: Record<string, unknown>;
  analytics: Record<string, unknown>;
  conversations: Conversation[];
  tickets: Ticket[];
  audits: AuditLog[];
  articles: KnowledgeArticle[];
  insights: Record<string, unknown>;
  messageByConversation: MessageMap;
  loadError?: boolean;
};

const formatDate = (value?: string | null) => {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'UTC',
  }).format(date);
};

const asNumber = (value: unknown, fallback = 0) => {
  const number = typeof value === 'number' ? value : Number(value);
  return Number.isFinite(number) ? number : fallback;
};

const compact = (value: unknown) => new Intl.NumberFormat('en', { notation: 'compact' }).format(asNumber(value));
const truncate = (value = '', length = 150) => value.length > length ? `${value.slice(0, length).trim()}…` : value;

const isRecord = (value: unknown): value is Record<string, unknown> => Boolean(value) && typeof value === 'object' && !Array.isArray(value);

const entriesFromCountMap = (value: unknown) => isRecord(value)
  ? Object.entries(value).map(([label, count]) => [label, asNumber(count)] as [string, number]).filter(([, count]) => count > 0)
  : [];

const entriesFromStringList = (value: unknown) => {
  if (!Array.isArray(value)) return [];
  const counts = new Map<string, number>();
  value.forEach((item) => {
    if (typeof item !== 'string' || !item.trim()) return;
    const label = item.trim();
    counts.set(label, (counts.get(label) ?? 0) + 1);
  });
  return Array.from(counts.entries());
};

const knowledgeGapLabel = (value: unknown) => {
  if (typeof value === 'string') return value.trim();
  if (!isRecord(value)) return '';
  const label = value.query ?? value.search_query ?? value.term ?? value.question ?? value.topic ?? value.category ?? value.id;
  return typeof label === 'string' ? label.trim() : '';
};

const entriesFromKnowledgeGaps = (value: unknown) => {
  if (isRecord(value)) return entriesFromCountMap(value);
  if (!Array.isArray(value)) return [];
  const counts = new Map<string, number>();
  value.forEach((item) => {
    const label = knowledgeGapLabel(item);
    if (!label) return;
    counts.set(label, (counts.get(label) ?? 0) + 1);
  });
  return Array.from(counts.entries());
};

const badgeTone = (value?: string) => {
  const normalized = value?.toLowerCase() ?? '';
  if (['resolved', 'closed', 'low', 'success', 'complete'].some((item) => normalized.includes(item))) return 'border-emerald-400/30 bg-emerald-400/10 text-emerald-200';
  if (['escalated', 'critical', 'high', 'error', 'failed'].some((item) => normalized.includes(item))) return 'border-rose-400/30 bg-rose-400/10 text-rose-200';
  if (['open', 'medium', 'pending', 'warning'].some((item) => normalized.includes(item))) return 'border-amber-400/30 bg-amber-400/10 text-amber-200';
  return 'border-sky-400/30 bg-sky-400/10 text-sky-200';
};

function Badge({ value }: { value?: string | null }) {
  return <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-medium capitalize ${badgeTone(value ?? undefined)}`}>{value || 'unknown'}</span>;
}

function EmptyState({ title, body }: { title: string; body: string }) {
  return <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-950/40 p-6 text-center"><p className="font-semibold text-slate-200">{title}</p><p className="mt-1 text-sm text-slate-400">{body}</p></div>;
}

function Section({ id, title, eyebrow, children }: { id: string; title: string; eyebrow: string; children: React.ReactNode }) {
  return <section id={id} className="scroll-mt-24 rounded-3xl border border-slate-800/80 bg-slate-900/80 p-5 shadow-2xl shadow-slate-950/30 ring-1 ring-white/5 sm:p-6"><p className="text-xs font-semibold uppercase tracking-[0.25em] text-sky-300">{eyebrow}</p><h2 className="mt-2 text-xl font-semibold text-white">{title}</h2><div className="mt-5">{children}</div></section>;
}

function MiniBar({ label, value, max }: { label: string; value: number; max: number }) {
  const width = max > 0 ? Math.max(8, Math.round((value / max) * 100)) : 8;
  return <div><div className="mb-1 flex justify-between text-xs text-slate-400"><span className="truncate pr-3">{label}</span><span>{value}</span></div><div className="h-2 overflow-hidden rounded-full bg-slate-800"><div className="h-full rounded-full bg-gradient-to-r from-sky-400 to-cyan-300" style={{ width: `${width}%` }} /></div></div>;
}

export default function AdminDashboard({ summary, analytics, conversations, tickets, audits, articles, insights, messageByConversation, loadError }: Props) {
  const [query, setQuery] = useState('');
  const data = { ...analytics, ...summary };
  const totalTickets = tickets.length || asNumber(data.total_tickets) || asNumber(data.ticket_count);
  const escalated = asNumber(data.escalated_tickets) || tickets.filter((ticket) => ticket.status?.toLowerCase().includes('escalat')).length;
  const escalationRate = totalTickets ? Math.round((escalated / totalTickets) * 100) : 0;
  const avgMs = asNumber(data.average_response_time_ms);
  const avgResponse = avgMs ? `${(avgMs / 1000).toFixed(1)}s` : '—';
  const kpis = [
    ['Conversations', compact(data.total_conversations ?? conversations.length), 'Customer sessions captured', 'Healthy'],
    ['Open tickets', compact(data.open_tickets ?? tickets.filter((t) => t.status === 'open').length), 'Active queue requiring review', 'Watch'],
    ['Escalated tickets', compact(data.escalated_tickets ?? escalated), 'Human handoff volume', escalated ? 'Action' : 'Clear'],
    ['Resolved tickets', compact(data.resolved_tickets ?? tickets.filter((t) => t.status === 'resolved').length), 'Completed support outcomes', 'Stable'],
    ['Avg response time', avgResponse, 'Assistant responsiveness', avgMs && avgMs > 5000 ? 'Watch' : 'Fast'],
    ['Knowledge articles', compact(data.knowledge_articles ?? articles.length), 'Approved read-only content', 'Ready'],
  ];
  const filteredConversations = useMemo(() => conversations.filter((conversation) => {
    const messages = messageByConversation[conversation.id] ?? [];
    const haystack = [conversation.id, conversation.status, ...messages.flatMap((message) => [message.role, message.content])].join(' ').toLowerCase();
    return haystack.includes(query.toLowerCase());
  }), [conversations, messageByConversation, query]);
  const categories = entriesFromStringList(analytics.top_complaints ?? insights.top_complaints).slice(0, 5);
  const gaps = entriesFromKnowledgeGaps(analytics.knowledge_gaps ?? insights.knowledge_gaps).slice(0, 5);
  const providerUsage = entriesFromCountMap(analytics.ai_provider_usage ?? insights.ai_provider_usage).slice(0, 4);
  const maxChart = Math.max(1, ...categories.map(([, v]) => asNumber(v)), ...gaps.map(([, v]) => asNumber(v)), ...providerUsage.map(([, v]) => asNumber(v)));

  return <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.18),transparent_34rem)] px-4 py-6 sm:px-8"><div className="mx-auto max-w-7xl space-y-8">
    <header className="rounded-[2rem] border border-slate-800 bg-slate-900/75 p-6 shadow-2xl shadow-slate-950/40 ring-1 ring-white/5 sm:p-8"><div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between"><div><p className="text-sm font-semibold uppercase tracking-[0.3em] text-cyan-300">FinGuard CX Agent</p><h1 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-5xl">Enterprise demo console</h1><p className="mt-3 max-w-3xl text-slate-300">Read-only operational command center for conversations, ticket health, audit activity, knowledge coverage, and demo analytics.</p></div><div className="flex flex-wrap gap-2 text-sm"><Badge value="Mock provider" /><Badge value="Read only" /><Badge value={loadError ? 'Partial data' : 'Live demo data'} /></div></div><nav className="mt-8 flex gap-2 overflow-x-auto pb-1 text-sm text-slate-300">{['Overview','Conversations','Tickets','Audit Logs','Knowledge','Analytics'].map((item) => <a key={item} href={`#${item.toLowerCase().replaceAll(' ', '-')}`} className="whitespace-nowrap rounded-full border border-slate-700 bg-slate-950/50 px-4 py-2 transition hover:border-sky-400 hover:text-white">{item}</a>)}</nav></header>
    {loadError ? <div className="rounded-2xl border border-amber-400/30 bg-amber-400/10 p-4 text-sm text-amber-100">Some admin endpoints did not respond. The console is showing the safe data that was available.</div> : null}
    <section id="overview" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">{kpis.map(([title, value, helper, status]) => <article key={title} className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 ring-1 ring-white/5"><div className="flex items-center justify-between gap-3"><p className="text-sm font-medium text-slate-400">{title}</p><span className={`h-2.5 w-2.5 rounded-full ${status === 'Action' ? 'bg-rose-400' : status === 'Watch' ? 'bg-amber-300' : 'bg-emerald-300'}`} /></div><p className="mt-4 text-3xl font-bold text-white">{value}</p><p className="mt-2 text-xs leading-5 text-slate-400">{helper}</p><p className="mt-4 text-xs font-semibold uppercase tracking-wide text-slate-500">{status}</p></article>)}</section>
    <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]"><Section id="conversations" eyebrow="Customer context" title="Conversations"><div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by ID, status, or message…" className="w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 outline-none transition placeholder:text-slate-500 focus:border-sky-400 sm:max-w-md" /><p className="text-sm text-slate-400">Showing {filteredConversations.length} of {conversations.length}</p></div>{filteredConversations.length === 0 ? <EmptyState title="No matching conversations" body="Send a chat message or clear the search filter to populate this panel." /> : <div className="max-h-[38rem] space-y-4 overflow-y-auto pr-1">{filteredConversations.map((conversation) => { const messages = messageByConversation[conversation.id] ?? []; const lastCustomer = [...messages].reverse().find((message) => message.role === 'user'); const lastAgent = [...messages].reverse().find((message) => message.role !== 'user'); return <article key={conversation.id} className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"><div className="flex flex-wrap items-center gap-2 text-sm"><code className="rounded bg-slate-900 px-2 py-1 text-sky-300">{conversation.id}</code><Badge value={conversation.status} /><span className="text-slate-400">Created {formatDate(conversation.created_at)}</span><span className="text-slate-400">{messages.length} messages</span></div>{messages.length === 0 ? <p className="mt-4 text-sm text-slate-500">No messages loaded for this conversation.</p> : <div className="mt-4 grid gap-3 md:grid-cols-2"><p className="rounded-xl bg-slate-900/80 p-3 text-sm text-slate-300"><span className="block text-xs font-semibold uppercase text-slate-500">Last customer message</span>{truncate(lastCustomer?.content ?? 'No customer message available')}</p><p className="rounded-xl bg-slate-900/80 p-3 text-sm text-slate-300"><span className="block text-xs font-semibold uppercase text-slate-500">Last agent reply</span>{truncate(lastAgent?.content ?? 'No agent reply available')}</p></div>}</article>; })}</div>}</Section>
    <Section id="tickets" eyebrow="Case operations" title="Tickets">{tickets.length === 0 ? <EmptyState title="No tickets yet" body="Escalations and created support cases will appear here." /> : <div className="overflow-hidden rounded-2xl border border-slate-800"><div className="overflow-x-auto"><table className="min-w-full divide-y divide-slate-800 text-left text-sm"><thead className="bg-slate-950/80 text-xs uppercase tracking-wide text-slate-500"><tr>{['Ticket','Status','Priority','Assignee','Created','Summary'].map((head) => <th key={head} className="px-4 py-3 font-semibold">{head}</th>)}</tr></thead><tbody className="divide-y divide-slate-800 bg-slate-950/35">{tickets.map((ticket) => <tr key={ticket.id} className="transition hover:bg-slate-900"><td className="px-4 py-4 font-mono text-sky-300">{ticket.id.slice(0, 8)}</td><td className="px-4 py-4"><Badge value={ticket.status} /></td><td className="px-4 py-4"><Badge value={ticket.priority} /></td><td className="px-4 py-4 text-slate-300">{ticket.assignee || 'Unassigned'}</td><td className="px-4 py-4 text-slate-400">{formatDate(ticket.created_at)}</td><td className="max-w-xs px-4 py-4 text-slate-300">{truncate(ticket.summary, 90)}</td></tr>)}</tbody></table></div></div>}</Section></div>
    <div className="grid gap-6 xl:grid-cols-2"><Section id="audit-logs" eyebrow="Governance" title="Audit logs">{audits.length === 0 ? <EmptyState title="No audit events" body="Safe operational events will render as a timeline when available." /> : <div className="space-y-3">{audits.slice(0, 14).map((audit, index) => { const ref = String(audit.payload?.conversation_id ?? audit.payload?.ticket_id ?? audit.payload?.id ?? '—'); const metadata = Object.entries(audit.payload ?? {}).filter(([key]) => !['system_prompt','provider_config','secret','connector_config'].includes(key)).slice(0, 3).map(([key, value]) => `${key}: ${String(value)}`).join(' · '); return <article key={`${audit.created_at}-${index}`} className="flex gap-4 rounded-2xl border border-slate-800 bg-slate-950/50 p-4"><span className={`mt-1 h-3 w-3 shrink-0 rounded-full ${badgeTone(audit.event_type).includes('rose') ? 'bg-rose-400' : 'bg-sky-400'}`} /><div className="min-w-0"><div className="flex flex-wrap items-center gap-2"><p className="font-semibold text-white">{audit.event_type.replaceAll('_', ' ')}</p><Badge value={audit.event_type.includes('error') ? 'attention' : 'recorded'} /></div><p className="mt-1 text-xs text-slate-500">{formatDate(audit.created_at)} · Ref {ref}</p><p className="mt-2 truncate text-sm text-slate-300">{metadata || 'No additional safe metadata available'}</p></div></article>; })}</div>}</Section>
    <Section id="knowledge" eyebrow="Content coverage" title="Knowledge base">{articles.length === 0 ? <EmptyState title="No knowledge articles" body="Approved help content will appear as read-only article cards." /> : <div className="grid gap-4 sm:grid-cols-2">{articles.map((article) => <article key={article.id} className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4"><h3 className="font-semibold text-white">{article.title}</h3><div className="mt-3 flex flex-wrap gap-2">{article.tags.map((tag) => <span key={tag} className="rounded-full bg-sky-400/10 px-2.5 py-1 text-xs text-sky-200">{tag}</span>)}</div><p className="mt-3 text-xs text-slate-500">Updated {formatDate(article.updated_at)}</p><p className="mt-3 text-sm leading-6 text-slate-300">{truncate(article.body, 180)}</p></article>)}</div>}<p className="mt-4 text-xs text-slate-500">Read-only preview. Uploads, paid embeddings, secrets, and connector settings are intentionally hidden.</p></Section></div>
    <Section id="analytics" eyebrow="Performance" title="Operational analytics"><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"><article className="rounded-2xl bg-slate-950/60 p-4"><p className="text-sm text-slate-400">Conversation count</p><p className="mt-2 text-3xl font-bold">{compact(data.total_conversations ?? conversations.length)}</p></article><article className="rounded-2xl bg-slate-950/60 p-4"><p className="text-sm text-slate-400">Ticket count</p><p className="mt-2 text-3xl font-bold">{compact(totalTickets)}</p></article><article className="rounded-2xl bg-slate-950/60 p-4"><p className="text-sm text-slate-400">Escalation rate</p><p className="mt-2 text-3xl font-bold">{escalationRate}%</p></article><article className="rounded-2xl bg-slate-950/60 p-4"><p className="text-sm text-slate-400">Response time</p><p className="mt-2 text-3xl font-bold">{avgResponse}</p></article></div><div className="mt-5 grid gap-5 lg:grid-cols-3"><div className="rounded-2xl border border-slate-800 bg-slate-950/50 p-4"><h3 className="font-semibold">Provider usage</h3><div className="mt-4 space-y-3">{providerUsage.length ? providerUsage.map(([label, value]) => <MiniBar key={label} label={label} value={asNumber(value)} max={maxChart} />) : <p className="text-sm text-slate-500">No provider usage yet.</p>}</div></div><div className="rounded-2xl border border-slate-800 bg-slate-950/50 p-4"><h3 className="font-semibold">Top complaint categories</h3><div className="mt-4 space-y-3">{categories.length ? categories.map(([label, value]) => <MiniBar key={label} label={label} value={asNumber(value)} max={maxChart} />) : <p className="text-sm text-slate-500">No category trends yet.</p>}</div></div><div className="rounded-2xl border border-slate-800 bg-slate-950/50 p-4"><h3 className="font-semibold">Knowledge gaps</h3><div className="mt-4 space-y-3">{gaps.length ? gaps.map(([label, value]) => <MiniBar key={label} label={label} value={asNumber(value)} max={maxChart} />) : <p className="text-sm text-slate-500">No gaps detected in current demo data.</p>}</div></div></div></Section>
  </div></main>;
}
