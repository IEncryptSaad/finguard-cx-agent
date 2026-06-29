from fastapi.testclient import TestClient
from app.main import app
from app.services.pii import redact_pii
from app.services.policy import redact_credentials


def test_production_auth_enforced_when_enabled(monkeypatch):
    monkeypatch.setenv('AUTH_REQUIRED', 'true')
    from app.core.config import get_settings
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        assert client.get('/api/v1/admin/summary').status_code == 401
        ok = client.get('/api/v1/admin/summary', headers={'X-FinGuard-Role':'admin','X-FinGuard-Actor':'admin@example.com'})
        assert ok.status_code == 200
    finally:
        monkeypatch.delenv('AUTH_REQUIRED', raising=False)
        get_settings.cache_clear()


def test_customer_cannot_mutate_settings_when_auth_enabled(monkeypatch):
    monkeypatch.setenv('AUTH_REQUIRED', 'true')
    from app.core.config import get_settings
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        response = client.put('/api/v1/settings', headers={'X-FinGuard-Role':'customer'}, json={
            'active_ai_provider':'mock','model_name':'mock-support-v1','temperature':0.2,'system_prompt':'safe',
            'guardrails_enabled':True,'pii_redaction_enabled':True,'rate_limit_per_minute':60,
            'enabled_plugins':['mock'],'knowledge_source_settings':{}
        })
        assert response.status_code == 403
    finally:
        monkeypatch.delenv('AUTH_REQUIRED', raising=False)
        get_settings.cache_clear()


def test_streaming_contract_and_pagination():
    client = TestClient(app)
    with client.stream('POST', '/api/v1/chat/stream', json={'message':'hello'}) as response:
        body = ''.join(response.iter_text())
    assert response.status_code == 200
    assert 'event: metadata' in body
    assert 'event: message.delta' in body
    assert 'event: message.done' in body
    page = client.get('/api/v1/conversations?paginated=true&page_size=1').json()
    assert set(['items','page','page_size','total']).issubset(page)
    assert len(page['items']) <= 1


def test_redaction_positive_and_false_positive_examples():
    sensitive = 'Email me at a@example.com, phone 415-555-1212, card 4111 1111 1111 1111, acct 1234567890.'
    clean, changed = redact_pii(sensitive)
    assert changed is True
    assert 'a@example.com' not in clean and '4111 1111' not in clean and '415-555' not in clean
    cred, changed = redact_credentials('api key is sk-test-secret-token')
    assert changed is True and 'sk-test-secret-token' not in cred
    harmless, changed = redact_pii('Order 12345 ships on 2026-06-29 and ticket ABC-123 remains open.')
    assert changed is False
    assert '12345' in harmless and 'ABC-123' in harmless
