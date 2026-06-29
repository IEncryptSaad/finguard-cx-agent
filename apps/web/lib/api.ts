const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
export type ChatResponse = { conversation_id: string; message: string; redacted: boolean; handoff_required: boolean; ticket_id?: string | null };
export type Conversation = { id: string; user_id?: string | null; status: string; created_at: string; updated_at: string };
export type Message = { id: string; conversation_id: string; role: string; content: string; created_at: string };
export type Ticket = { id: string; conversation_id: string; summary: string; status: string; priority: string };
export type KnowledgeArticle = { id: string; title: string; body: string; tags: string[] };
async function json<T>(path: string, init?: RequestInit): Promise<T> { const r = await fetch(`${API_BASE}${path}`, { cache: 'no-store', ...init }); if (!r.ok) throw new Error(path); return r.json(); }
export async function sendChat(message: string, conversationId?: string): Promise<ChatResponse> { return json('/api/v1/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message, conversation_id: conversationId }) }); }
export async function streamChat(message: string, conversationId?: string): Promise<ChatResponse> { return sendChat(message, conversationId); }
export const getAdminSummary = () => json<Record<string, number>>('/api/v1/admin/summary');
export const getConversations = () => json<Conversation[]>('/api/v1/conversations');
export const getAuditLogs = () => json<Array<{event_type:string; payload: Record<string, unknown>; created_at: string}>>('/api/v1/audit');
export const getTickets = () => json<Ticket[]>('/api/v1/tickets');
export const getKnowledge = () => json<KnowledgeArticle[]>('/api/v1/knowledge');
export const createTicket = (conversation_id: string, summary: string) => json<Ticket>('/api/v1/tickets', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({conversation_id, summary}) });
