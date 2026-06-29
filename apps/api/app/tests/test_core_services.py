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
from app.services.policy import CREDENTIAL_PLACEHOLDER, redact_credentials
from app.main import app


def test_pii_redaction_masks_sensitive_values():
    clean, changed = redact_pii("email me at person@example.com and card 4111 1111 1111 1111")
    assert changed is True
    assert "person@example.com" not in clean
    assert clean.count("[REDACTED]") == 2


def test_credential_redaction_consumes_common_connectors():
    examples = {
        "api key is sk-test-api-key-123": "sk-test-api-key-123",
        "token is tok-test-token-123": "tok-test-token-123",
        "reset password is reset-test-password-123": "reset-test-password-123",
        "secret is secret-test-value-123": "secret-test-value-123",
        "password is hunter2-test-password-123": "hunter2-test-password-123",
    }

    for message, secret in examples.items():
        clean, changed = redact_credentials(message)

        assert changed is True
        assert secret not in clean
        assert " is " not in clean.lower()
        assert CREDENTIAL_PLACEHOLDER in clean


def test_credential_chat_redacts_values_from_memory_audit_and_messages_api():
    client = TestClient(app)
    examples = {
        "api key is sk-chat-api-key-123": "sk-chat-api-key-123",
        "token is tok-chat-token-123": "tok-chat-token-123",
        "reset password is reset-chat-password-123": "reset-chat-password-123",
        "secret is secret-chat-value-123": "secret-chat-value-123",
        "password is hunter2-chat-password-123": "hunter2-chat-password-123",
    }

    for message, secret in examples.items():
        response = client.post("/api/v1/chat", json={"message": message})
        assert response.status_code == 200
        payload = response.json()
        assert payload["redacted"] is True
        assert secret not in response.text

        messages = client.get(f"/api/v1/conversations/{payload['conversation_id']}/messages")
        assert messages.status_code == 200
        assert secret not in messages.text
        assert CREDENTIAL_PLACEHOLDER in messages.text or payload["handoff_required"] is True

        audit = client.get("/api/v1/audit")
        assert audit.status_code == 200
        assert secret not in audit.text

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

def test_ticket_lifecycle_settings_plugins_analytics_and_knowledge_search():
    client = TestClient(app)
    chat = client.post("/api/v1/chat", json={"message": "I have fraud on my card"}).json()
    ticket_id = chat["ticket_id"]
    updated = client.patch(f"/api/v1/tickets/{ticket_id}", json={"status": "resolved"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "resolved"

    settings = client.get("/api/v1/settings")
    assert settings.status_code == 200
    assert settings.json()["active_ai_provider"] == "mock"

    plugins = client.get("/api/v1/plugins")
    assert plugins.status_code == 200
    assert any(p["name"] == "demo_webhook" for p in plugins.json())

    search = client.get("/api/v1/knowledge?q=dispute")
    assert search.status_code == 200
    assert search.json()

    analytics = client.get("/api/v1/analytics")
    assert analytics.status_code == 200
    assert analytics.json()["total_conversations"] >= 1
    assert "ai_provider_usage" in analytics.json()
