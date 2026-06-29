import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient
from app.agent.llm import MockLLMProvider
from app.agent.orchestrator import AgentOrchestrator
from app.auth.rbac import can_access
from app.models.schemas import Role
from app.services.guardrails import evaluate_message
from app.services.pii import redact_pii
from app.main import app


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


def test_blocked_credential_chat_does_not_store_plaintext_secret():
    client = TestClient(app)
    secret = "hunter2"
    response = client.post("/api/v1/chat", json={"message": f"my password is {secret}"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["handoff_required"] is True
    assert payload["redacted"] is True

    messages = client.get(f"/api/v1/conversations/{payload['conversation_id']}/messages")
    assert messages.status_code == 200
    serialized = messages.text
    assert secret not in serialized
    assert "[REDACTED_CREDENTIAL]" in serialized or "customer" not in serialized


def test_knowledge_create_accepts_payload_without_id():
    client = TestClient(app)
    response = client.post("/api/v1/knowledge", json={"title": "A", "body": "B", "tags": []})
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"]
    assert payload["title"] == "A"
    assert payload["body"] == "B"
    assert payload["tags"] == []


def test_chat_schema_root_references_chat_request_contract():
    schema = json.loads(Path("../../packages/shared/schemas/chat.schema.json").read_text())
    assert schema["$ref"] == "#/definitions/ChatRequest"
    request_schema = schema["definitions"]["ChatRequest"]
    assert request_schema["required"] == ["message"]
    assert request_schema["properties"]["message"]["minLength"] == 1
    assert request_schema["properties"]["message"]["maxLength"] == 4000
