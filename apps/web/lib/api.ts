const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';
export type ChatResponse = { conversation_id: string; message: string; redacted: boolean; handoff_required: boolean; ticket_id?: string | null };
export async function sendChat(message: string, conversationId?: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/api/v1/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message, conversation_id: conversationId }) });
  if (!response.ok) throw new Error('Chat request failed');
  return response.json();
}
export async function getAdminSummary() { const r = await fetch(`${API_BASE}/api/v1/admin/summary`, { cache: 'no-store' }); return r.json(); }
