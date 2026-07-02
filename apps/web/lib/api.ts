const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
export type Page<T> = { items:T[]; page:number; page_size:number; total:number };
export type ChatResponse = { conversation_id: string; message: string; redacted: boolean; handoff_required: boolean; ticket_id?: string | null };
export type Conversation = { id: string; user_id?: string | null; status: string; created_at: string; updated_at: string };
export type Message = { id: string; conversation_id: string; role: string; content: string; created_at: string };
export type Ticket = { id: string; conversation_id: string; summary: string; status: string; priority: string };
export type KnowledgeArticle = { id: string; title: string; body: string; tags: string[] };
async function json<T>(path: string, init?: RequestInit): Promise<T> { const r = await fetch(`${API_BASE}${path}`, { cache: 'no-store', ...init }); if (!r.ok) { const body = await r.text().catch(()=>''); throw new Error(`${path}: ${r.status} ${body}`); } return r.json(); }
const withPage = (path:string) => `${path}${path.includes('?') ? '&' : '?'}paginated=true&page_size=50`;
const unwrap = async <T>(p: Promise<T[]|Page<T>>) => { const r = await p; return Array.isArray(r) ? r : r.items; };
export async function sendChat(message: string, conversationId?: string): Promise<ChatResponse> { return json('/api/v1/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message, conversation_id: conversationId }) }); }
export async function streamChat(message: string, conversationId: string|undefined, onDelta: (text:string)=>void): Promise<ChatResponse> { const r = await fetch(`${API_BASE}/api/v1/chat/stream`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message, conversation_id: conversationId}) }); if(!r.ok || !r.body) throw new Error(`stream: ${r.status}`); const reader=r.body.getReader(); const decoder=new TextDecoder(); let buffer=''; let donePayload: ChatResponse|undefined; while(true){ const {value,done}=await reader.read(); if(done) break; buffer += decoder.decode(value,{stream:true}); const parts=buffer.split('\n\n'); buffer=parts.pop() ?? ''; for(const part of parts){ const event=part.split('\n').find(l=>l.startsWith('event:'))?.slice(6).trim(); const data=part.split('\n').filter(l=>l.startsWith('data:')).map(l=>l.slice(5).trim()).join('\n'); if(event==='message.delta') onDelta((JSON.parse(data) as {delta:string}).delta); if(event==='message.done') donePayload=JSON.parse(data) as ChatResponse; if(event==='error') throw new Error(data); }} if(!donePayload) throw new Error('stream finished without message.done'); return donePayload; }
export const getAdminSummary = () => json<Record<string, unknown>>('/api/v1/admin/summary');
export const getAnalytics = () => json<Record<string, unknown>>('/api/v1/analytics');
export const getInsights = () => json<Record<string, unknown>>('/api/v1/analytics/insights');
export const getConversations = () => unwrap(json<Conversation[]|Page<Conversation>>(withPage('/api/v1/conversations')));
export const getAuditLogs = () => unwrap(json<Array<{event_type:string; payload: Record<string, unknown>; created_at: string}>|Page<{event_type:string; payload: Record<string, unknown>; created_at: string}>>(withPage('/api/v1/audit')));
export const getTickets = () => unwrap(json<Ticket[]|Page<Ticket>>(withPage('/api/v1/tickets')));
export const updateTicket = (id:string, payload: Partial<Ticket>) => json<Ticket>(`/api/v1/tickets/${id}`, { method:'PATCH', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
export const getKnowledge = (q?: string) => unwrap(json<KnowledgeArticle[]|Page<KnowledgeArticle>>(withPage(`/api/v1/knowledge${q ? `?q=${encodeURIComponent(q)}` : ''}`)));
export const getMessages = (id:string) => json<Message[]>(`/api/v1/conversations/${id}/messages`);
export const createTicket = (conversation_id: string, summary: string) => json<Ticket>('/api/v1/tickets', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({conversation_id, summary}) });
