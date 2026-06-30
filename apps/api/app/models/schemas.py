from enum import StrEnum
from pydantic import BaseModel, Field, field_validator
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
    id: str; conversation_id: str; summary: str; status: str = "open"; priority: str = "normal"; assignee: str | None = None; internal_notes: list[str] = []
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
    assignee: str | None = Field(default=None, max_length=120)
    internal_note: str | None = Field(default=None, min_length=1, max_length=1000)

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

class WorkflowTrigger(StrEnum):
    new_conversation = "new_conversation"; conversation_resolved = "conversation_resolved"; escalation = "escalation"; knowledge_article_created = "knowledge_article_created"; webhook_received = "webhook_received"; scheduled_event = "scheduled_event"
class WorkflowActionType(StrEnum):
    create_ticket = "create_ticket"; summarize_conversation = "summarize_conversation"; send_webhook = "send_webhook"; generate_knowledge_article = "generate_knowledge_article"; assign_operator = "assign_operator"; notify_admin = "notify_admin"; custom_plugin_action = "custom_plugin_action"
class WorkflowCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    trigger: WorkflowTrigger
    conditions: list[dict] = []
    actions: list[dict] = []
    retry_policy: dict = {"max_attempts": 3, "backoff_seconds": 30}
    status: str = Field(default="draft", pattern="^(draft|active|paused|archived)$")

    @field_validator("retry_policy")
    @classmethod
    def validate_retry_policy(cls, retry_policy: dict) -> dict:
        if "max_attempts" not in retry_policy:
            return retry_policy

        max_attempts = retry_policy["max_attempts"]
        if isinstance(max_attempts, bool) or isinstance(max_attempts, float):
            raise ValueError("retry_policy.max_attempts must be an integer between 0 and 10")

        try:
            attempts = int(max_attempts)
        except (TypeError, ValueError):
            raise ValueError("retry_policy.max_attempts must be an integer between 0 and 10")

        if attempts != max_attempts and str(attempts) != str(max_attempts):
            raise ValueError("retry_policy.max_attempts must be an integer between 0 and 10")
        if attempts < 0 or attempts > 10:
            raise ValueError("retry_policy.max_attempts must be an integer between 0 and 10")

        return {**retry_policy, "max_attempts": attempts}
class Workflow(WorkflowCreate):
    id: str; created_at: str; updated_at: str
class WorkflowExecution(BaseModel):
    id: str; workflow_id: str; status: str; started_at: str; finished_at: str | None = None; attempts: int = 1; input: dict = {}; output: dict = {}; error: str | None = None

class ProductItemType(StrEnum):
    feature_request = "feature_request"; bug_report = "bug_report"; product_feedback = "product_feedback"; roadmap_item = "roadmap_item"
class ProductItemCreate(BaseModel):
    type: ProductItemType
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=4000)
    status: str = Field(default="open", pattern="^(open|in_progress|completed|closed)$")
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    labels: list[str] = []
    owner: str | None = None
    linked_conversations: list[str] = []
    attachments: list[str] = []
class ProductItem(ProductItemCreate):
    id: str; ai_summary: str; ai_priority_suggestion: str; duplicate_of: str | None = None; created_at: str; updated_at: str

class FeedbackClassification(BaseModel):
    id: str; conversation_id: str; category: str; sentiment: str; summary: str; recommended_action: str; confidence_score: float; created_at: str

class InternalAssistantRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None
class InternalAssistantResponse(BaseModel):
    answer: str; sources: list[str]; suggested_actions: list[str]

class MarketplaceInstallRequest(BaseModel):
    name: str
    kind: str = Field(pattern="^(action|workflow|ai_provider|knowledge_connector|analytics|notification)$")
    enabled: bool = True
class MarketplacePlugin(BaseModel):
    name: str; kind: str; enabled: bool; description: str = ""

class ProviderRouteRequest(BaseModel):
    capability: str = "chat"
    preferred_provider: str | None = None
    require_healthy: bool = True
class ProviderRouteResponse(BaseModel):
    provider: str; capability: str; reason: str; failover: list[str] = []

class MemoryScope(StrEnum):
    conversation = "conversation"; user = "user"; session = "session"; workspace = "workspace"
class MemoryRecord(BaseModel):
    id: str | None = None; scope: MemoryScope; key: str; value: dict; user_id: str | None = None; session_id: str | None = None; workspace_id: str = "default"; created_at: str | None = None; updated_at: str | None = None
class MemoryRecordCreate(BaseModel):
    scope: MemoryScope; key: str; value: dict; user_id: str | None = None; session_id: str | None = None; workspace_id: str = "default"

class ActionDefinition(BaseModel):
    name: str; category: str = "general"; description: str = ""; schema: dict = {}; permissions: list[str] = []; enabled: bool = True; lifecycle: str = Field(default="active", pattern="^(draft|active|deprecated|retired)$")
class ActionRunRequest(BaseModel):
    payload: dict = {}; idempotency_key: str | None = None
class ActionExecution(BaseModel):
    id: str; action: str; status: str; input: dict; output: dict = {}; error: str | None = None; started_at: str; finished_at: str | None = None; attempts: int = 1

class PromptTemplateCreate(BaseModel):
    name: str; category: str = "general"; template: str = Field(min_length=1, max_length=8000); config: dict = {}; status: str = Field(default="draft", pattern="^(draft|active|retired)$")
class PromptTemplate(PromptTemplateCreate):
    id: str; version: int = 1; created_at: str; updated_at: str

class EventSubscription(BaseModel):
    id: str | None = None; event_type: str; target: str = "audit"; enabled: bool = True; created_at: str | None = None
class EventPublishRequest(BaseModel):
    event_type: str; payload: dict = {}; async_processing: bool = True

class EvaluationDataset(BaseModel):
    id: str | None = None; name: str; items: list[dict] = []; created_at: str | None = None
class EvaluationRunRequest(BaseModel):
    dataset_id: str; provider: str = "mock"; benchmark: str = "quality"
class EvaluationRun(BaseModel):
    id: str; dataset_id: str; status: str; score: float; metrics: dict; created_at: str
