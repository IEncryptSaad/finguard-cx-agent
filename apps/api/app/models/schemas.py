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
class KnowledgeArticle(BaseModel):
    id: str; title: str; body: str; tags: list[str] = []
class AuditLog(BaseModel):
    event_type: str; payload: dict; created_at: str
class LifecycleEvent(BaseModel):
    name: str; description: str = ""
