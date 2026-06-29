export const APP_NAME = 'FinGuard CX Agent';
export const SUPPORT_PRIORITIES = ['low', 'normal', 'high', 'urgent'] as const;
export type SupportPriority = (typeof SUPPORT_PRIORITIES)[number];
export type Role = 'admin' | 'agent' | 'customer';
export interface ErrorResponse { code: string; message: string; details?: Record<string, unknown> }
export interface ChatRequest { message: string; conversation_id?: string; user_id?: string }
export interface ChatResponse { conversation_id: string; message: string; redacted: boolean; handoff_required: boolean; ticket_id?: string | null }
export interface Conversation { id: string; user_id?: string | null; status: string; created_at: string; updated_at: string }
export interface ConversationMessage { id: string; conversation_id: string; role: string; content: string; created_at: string }
export interface Ticket { id: string; conversation_id: string; summary: string; status: string; priority: SupportPriority | string }
export interface KnowledgeArticle { id: string; title: string; body: string; tags: string[] }
export interface PluginMetadata { name: string; enabled: boolean; description?: string }
export type PluginKind = 'ai_provider'|'action'|'tool'|'integration'|'knowledge_source'|'auth_provider'|'analytics_provider'|'notification_provider';
