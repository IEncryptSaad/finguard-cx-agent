const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
export type ChatResponse = { conversation_id: string; message: string; redacted: boolean; handoff_required: boolean; ticket_id?: string | null };
export type Conversation = { id: string; user_id?: string | null; status: string; created_at: string; updated_at: string };
export type Message = { id: string; conversation_id: string; role: string; content: string; created_at: string };
export type Ticket = { id: string; conversation_id: string; summary: string; status: string; priority: string };
export type KnowledgeArticle = { id: string; title: string; body: string; tags: string[] };
export type AppSettings = { active_ai_provider:string; model_name:string; temperature:number; system_prompt:string; guardrails_enabled:boolean; pii_redaction_enabled:boolean; rate_limit_per_minute:number; enabled_plugins:string[]; knowledge_source_settings: Record<string, unknown> };
export type Workflow = { id:string; name:string; trigger:string; conditions:Record<string, unknown>[]; actions:Record<string, unknown>[]; retry_policy:Record<string, unknown>; status:string; created_at:string; updated_at:string };
export type ProductItem = { id:string; type:string; title:string; description:string; status:string; priority:string; labels:string[]; owner?:string|null; linked_conversations:string[]; attachments:string[]; ai_summary:string; ai_priority_suggestion:string; duplicate_of?:string|null; created_at:string; updated_at:string };
export type FeedbackClassification = { id:string; conversation_id:string; category:string; sentiment:string; summary:string; recommended_action:string; confidence_score:number; created_at:string };
export type MarketplacePlugin = { name:string; kind:string; enabled:boolean; description:string };
async function json<T>(path: string, init?: RequestInit): Promise<T> { const r = await fetch(`${API_BASE}${path}`, { cache: 'no-store', ...init }); if (!r.ok) throw new Error(`${path}: ${r.status}`); return r.json(); }
export async function sendChat(message: string, conversationId?: string): Promise<ChatResponse> { return json('/api/v1/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message, conversation_id: conversationId }) }); }
export async function streamChat(message: string, conversationId?: string): Promise<ChatResponse> { return sendChat(message, conversationId); }
export const getAdminSummary = () => json<Record<string, unknown>>('/api/v1/admin/summary');
export const getAnalytics = () => json<Record<string, unknown>>('/api/v1/analytics');
export const getInsights = () => json<Record<string, unknown>>('/api/v1/analytics/insights');
export const getConversations = () => json<Conversation[]>('/api/v1/conversations');
export const getAuditLogs = () => json<Array<{event_type:string; payload: Record<string, unknown>; created_at: string}>>('/api/v1/audit');
export const getTickets = () => json<Ticket[]>('/api/v1/tickets');
export const updateTicket = (id:string, payload: Partial<Ticket>) => json<Ticket>(`/api/v1/tickets/${id}`, { method:'PATCH', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
export const getKnowledge = (q?: string) => json<KnowledgeArticle[]>(`/api/v1/knowledge${q ? `?q=${encodeURIComponent(q)}` : ''}`);
export const getSettings = () => json<AppSettings>('/api/v1/settings');
export const getPlugins = () => json<Array<{name:string; enabled:boolean; description:string; type:string}>>('/api/v1/plugins');
export const getWorkflows = () => json<Workflow[]>('/api/v1/workflows');
export const getRoadmap = () => json<ProductItem[]>('/api/v1/roadmap');
export const getRoadmapDashboard = () => json<Record<string, ProductItem[]>>('/api/v1/roadmap/dashboard');
export const getFeedback = () => json<FeedbackClassification[]>('/api/v1/feedback');
export const getMarketplace = () => json<MarketplacePlugin[]>('/api/v1/marketplace');
export const createTicket = (conversation_id: string, summary: string) => json<Ticket>('/api/v1/tickets', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({conversation_id, summary}) });
