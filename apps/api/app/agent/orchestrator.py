from app.agent.llm import LLMProvider
from app.models.schemas import ChatResponse
from app.services.audit import log_event
from app.services.guardrails import evaluate_message
from app.services.handoff import request_handoff
from app.services.memory import add_message, get_or_create_conversation, history
from app.services.pii import redact_pii
from app.services.policy import policy_engine, redact_credentials
from app.services.prompts import prompt_manager
class AgentOrchestrator:
    def __init__(self, llm: LLMProvider): self.llm = llm
    async def handle_chat(self, message: str, conversation_id: str | None = None, user_id: str | None = None) -> ChatResponse:
        conv = get_or_create_conversation(conversation_id, user_id)
        pii_clean, pii_redacted = redact_pii(message)
        clean, credential_redacted = redact_credentials(pii_clean)
        was_redacted = pii_redacted or credential_redacted
        decision = policy_engine.evaluate(clean, evaluate_message(clean))
        if decision.allowed:
            add_message(conv.id, "customer", clean)
        log_event("chat.received", {"conversation_id": conv.id, "redacted": was_redacted, "allowed": decision.allowed})
        if not decision.allowed:
            ticket = request_handoff(conv.id, decision.reason)
            reply = "I cannot complete that request automatically. A specialist will review it."
            add_message(conv.id, "agent", reply)
            return ChatResponse(conversation_id=conv.id, message=reply, redacted=was_redacted, handoff_required=True, ticket_id=ticket.id)
        transcript = "\n".join(f"{m.role}: {m.content}" for m in history(conv.id)[-8:])
        prompt = prompt_manager.render("chat", message=f"{transcript}\nagent:")
        answer = await self.llm.complete(prompt, system_prompt=prompt_manager.get("system"))
        ticket_id = None
        if decision.handoff_required:
            ticket_id = request_handoff(conv.id, clean[:200]).id
            log_event("handoff.requested", {"conversation_id": conv.id, "ticket_id": ticket_id})
        add_message(conv.id, "agent", answer)
        log_event("chat.responded", {"conversation_id": conv.id, "handoff_required": decision.handoff_required})
        return ChatResponse(conversation_id=conv.id, message=answer, redacted=was_redacted, handoff_required=decision.handoff_required, ticket_id=ticket_id)
