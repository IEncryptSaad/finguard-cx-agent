export const APP_NAME = 'FinGuard CX Agent';
export const SUPPORT_PRIORITIES = ['low', 'normal', 'high', 'urgent'] as const;
export type SupportPriority = (typeof SUPPORT_PRIORITIES)[number];
export type Role = 'admin' | 'agent' | 'customer';
export interface ChatRequest { message: string; conversation_id?: string }
export interface ChatResponse { conversation_id: string; message: string; redacted: boolean; handoff_required: boolean; ticket_id?: string | null }
