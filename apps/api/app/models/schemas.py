from enum import StrEnum
from pydantic import BaseModel, Field
class Role(StrEnum):
    admin = "admin"; agent = "agent"; customer = "customer"
class ErrorResponse(BaseModel):
    code: str; message: str; details: dict | None = None
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000); conversation_id: str | None = None; user_id: str | None = None
class ChatResponse(BaseModel):
    conversation_id: str; message: str; redacted: bool; handoff_required: bool; ticket_id: str | None = None
class User(BaseModel):
    id: str; email: str; role: Role = Role.customer; display_name: str | None = None
class Conversation(BaseModel):
    id: str; user_id: str | None = None; status: str = "open"; created_at: str; updated_at: str
class ConversationMessage(BaseModel):
    id: str; conversation_id: str; role: str; content: str; created_at: str
class Ticket(BaseModel):
    id: str; conversation_id: str; summary: str; status: str = "open"; priority: str = "normal"
class KnowledgeArticleBase(BaseModel):
    title: str; body: str; tags: list[str] = []
class KnowledgeArticleCreate(KnowledgeArticleBase):
    pass
class KnowledgeArticleUpdate(KnowledgeArticleBase):
    pass
class KnowledgeArticle(KnowledgeArticleBase):
    id: str
class AuditLog(BaseModel):
    event_type: str; payload: dict; created_at: str
class LifecycleEvent(BaseModel):
    name: str; description: str = ""


class TicketCreate(BaseModel):
    conversation_id: str = Field(min_length=1, max_length=120)
    summary: str = Field(min_length=1, max_length=1000)
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")

class TicketUpdate(BaseModel):
    status: str | None = Field(default=None, pattern="^(open|pending|resolved|closed|escalated)$")
    priority: str | None = Field(default=None, pattern="^(low|normal|high|urgent)$")
    summary: str | None = Field(default=None, min_length=1, max_length=1000)

class KnowledgeSearchResponse(BaseModel):
    query: str
    results: list[KnowledgeArticle]

class AppSettings(BaseModel):
    active_ai_provider: str = "mock"
    model_name: str = "mock-support-v1"
    temperature: float = Field(default=0.2, ge=0, le=2)
    system_prompt: str = Field(default="You are FinGuard, a careful financial services customer support assistant. Be concise, compliant, and avoid requesting sensitive PII.", min_length=1, max_length=4000)
    guardrails_enabled: bool = True
    pii_redaction_enabled: bool = True
    rate_limit_per_minute: int = Field(default=60, ge=1, le=1000)
    enabled_plugins: list[str] = ["mock", "demo_webhook"]
    knowledge_source_settings: dict = {}

class AnalyticsSummary(BaseModel):
    total_conversations: int
    resolved_tickets: int
    escalated_tickets: int
    average_response_time_ms: float
    ai_provider_usage: dict[str, int]
    knowledge_searches: int
    recent_audit_events: list[dict]
