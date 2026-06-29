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
export type WorkflowTrigger = 'new_conversation'|'conversation_resolved'|'escalation'|'knowledge_article_created'|'webhook_received'|'scheduled_event';
export type WorkflowActionType = 'create_ticket'|'summarize_conversation'|'send_webhook'|'generate_knowledge_article'|'assign_operator'|'notify_admin'|'custom_plugin_action';
export interface Workflow { id: string; name: string; trigger: WorkflowTrigger; conditions: Record<string, unknown>[]; actions: Record<string, unknown>[]; retry_policy: Record<string, unknown>; status: 'draft'|'active'|'paused'|'archived'; created_at: string; updated_at: string }
export interface WorkflowExecution { id: string; workflow_id: string; status: string; started_at: string; finished_at?: string | null; attempts: number; input: Record<string, unknown>; output: Record<string, unknown>; error?: string | null }
export type ProductItemType = 'feature_request'|'bug_report'|'product_feedback'|'roadmap_item';
export interface ProductItem { id: string; type: ProductItemType; title: string; description: string; status: string; priority: SupportPriority | string; labels: string[]; owner?: string | null; linked_conversations: string[]; attachments: string[]; ai_summary: string; ai_priority_suggestion: string; duplicate_of?: string | null; created_at: string; updated_at: string }
export interface FeedbackClassification { id: string; conversation_id: string; category: 'Bug'|'Feature Request'|'Complaint'|'Praise'|'Fraud'|'Dispute'|'General Question'|string; sentiment: string; summary: string; recommended_action: string; confidence_score: number; created_at: string }
export type MarketplacePluginKind = 'action'|'workflow'|'ai_provider'|'knowledge_connector'|'analytics'|'notification';
export interface MarketplacePlugin { name: string; kind: MarketplacePluginKind | string; enabled: boolean; description: string }
