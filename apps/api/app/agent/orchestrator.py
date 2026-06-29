from uuid import uuid4
from app.agent.llm import LLMProvider
from app.models.schemas import ChatResponse
from app.services.audit import log_event
from app.services.guardrails import evaluate_message
from app.services.handoff import request_handoff
from app.services.pii import redact_pii
class AgentOrchestrator:
    def __init__(self, llm: LLMProvider): self.llm = llm
    async def handle_chat(self, message: str, conversation_id: str | None = None) -> ChatResponse:
        cid = conversation_id or str(uuid4())
        clean, was_redacted = redact_pii(message)
        decision = evaluate_message(clean)
        log_event("chat.received", {"conversation_id": cid, "redacted": was_redacted, "allowed": decision.allowed})
        if not decision.allowed:
            ticket = request_handoff(cid, decision.reason)
            return ChatResponse(conversation_id=cid, message="I cannot complete that request automatically. A specialist will review it.", redacted=was_redacted, handoff_required=True, ticket_id=ticket.id)
        answer = await self.llm.complete(clean)
        ticket_id = None
        if decision.handoff_required:
            ticket_id = request_handoff(cid, clean[:200]).id
            log_event("handoff.requested", {"conversation_id": cid, "ticket_id": ticket_id})
        log_event("chat.responded", {"conversation_id": cid, "handoff_required": decision.handoff_required})
        return ChatResponse(conversation_id=cid, message=answer, redacted=was_redacted, handoff_required=decision.handoff_required, ticket_id=ticket_id)
