import asyncio
from app.agent.llm import MockLLMProvider
from app.agent.orchestrator import AgentOrchestrator
from app.auth.rbac import can_access
from app.models.schemas import Role
from app.services.guardrails import evaluate_message
from app.services.pii import redact_pii

def test_pii_redaction_masks_sensitive_values():
    clean, changed = redact_pii("email me at person@example.com and card 4111 1111 1111 1111")
    assert changed is True
    assert "person@example.com" not in clean
    assert clean.count("[REDACTED]") == 2

def test_guardrails_trigger_handoff_for_fraud():
    decision = evaluate_message("I see suspected fraud on my card")
    assert decision.allowed is True
    assert decision.handoff_required is True

def test_rbac_agent_can_update_ticket_but_customer_cannot():
    assert can_access(Role.agent, "ticket:update") is True
    assert can_access(Role.customer, "ticket:update") is False

def test_orchestrator_uses_mock_and_creates_handoff():
    response = asyncio.run(AgentOrchestrator(MockLLMProvider()).handle_chat("I need to dispute a transaction"))
    assert response.handoff_required is True
    assert response.ticket_id
    assert response.message
