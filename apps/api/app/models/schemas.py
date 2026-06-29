from enum import StrEnum
from pydantic import BaseModel, Field
class Role(StrEnum):
    admin = "admin"
    agent = "agent"
    customer = "customer"
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    redacted: bool
    handoff_required: bool
    ticket_id: str | None = None
class Ticket(BaseModel):
    id: str
    conversation_id: str
    summary: str
    status: str = "open"
    priority: str = "normal"
