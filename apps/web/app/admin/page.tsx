import AdminDashboard from '../../components/AdminDashboard';
import { getAdminSummary, getAnalytics, getAuditLogs, getConversations, getInsights, getKnowledge, getMessages, getTickets } from '../../lib/api';
import type { Conversation, KnowledgeArticle, Ticket } from '../../lib/api';

type AuditLog = { event_type: string; payload: Record<string, unknown>; created_at: string };

export default async function Admin() {
  const settled = await Promise.allSettled([
    getAdminSummary(),
    getAnalytics(),
    getConversations(),
    getTickets(),
    getAuditLogs(),
    getKnowledge(),
    getInsights(),
  ]);
  const [summary, analytics, conversations, tickets, audits, articles, insights] = settled.map((result) => result.status === 'fulfilled' ? result.value : undefined);
  const safeConversations = (Array.isArray(conversations) ? conversations : []) as Conversation[];
  const recentMessages = await Promise.all(safeConversations.slice(0, 25).map(async (conversation) => ({
    conversationId: conversation.id,
    messages: await getMessages(conversation.id).catch(() => []),
  })));

  return <AdminDashboard
    summary={(summary as Record<string, unknown>) ?? {}}
    analytics={(analytics as Record<string, unknown>) ?? {}}
    conversations={safeConversations}
    tickets={(Array.isArray(tickets) ? tickets : []) as Ticket[]}
    audits={(Array.isArray(audits) ? audits : []) as AuditLog[]}
    articles={(Array.isArray(articles) ? articles : []) as KnowledgeArticle[]}
    insights={(insights as Record<string, unknown>) ?? {}}
    messageByConversation={Object.fromEntries(recentMessages.map((item) => [item.conversationId, item.messages]))}
    loadError={settled.some((result) => result.status === 'rejected')}
  />;
}
