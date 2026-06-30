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


def test_auth_required_anonymous_chat_returns_401(monkeypatch):
    monkeypatch.setenv('AUTH_REQUIRED', 'true')
    from app.core.config import get_settings
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        assert client.post('/api/v1/chat', json={'message': 'hello'}).status_code == 401
    finally:
        monkeypatch.delenv('AUTH_REQUIRED', raising=False)
        get_settings.cache_clear()


def test_production_anonymous_chat_requires_auth_unless_public_enabled(monkeypatch):
    monkeypatch.setenv('APP_ENV', 'production')
    monkeypatch.delenv('PUBLIC_CUSTOMER_CHAT', raising=False)
    from app.core.config import get_settings
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        assert client.post('/api/v1/chat', json={'message': 'hello'}).status_code == 401

        monkeypatch.setenv('PUBLIC_CUSTOMER_CHAT', 'true')
        get_settings.cache_clear()
        assert client.post('/api/v1/chat', json={'message': 'hello'}).status_code == 200
    finally:
        monkeypatch.delenv('APP_ENV', raising=False)
        monkeypatch.delenv('PUBLIC_CUSTOMER_CHAT', raising=False)
        get_settings.cache_clear()


def test_authorized_user_can_chat_when_auth_required(monkeypatch):
    monkeypatch.setenv('AUTH_REQUIRED', 'true')
    from app.core.config import get_settings
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        response = client.post('/api/v1/chat', headers={'X-FinGuard-Role': 'customer'}, json={'message': 'hello'})
        assert response.status_code == 200
    finally:
        monkeypatch.delenv('AUTH_REQUIRED', raising=False)
        get_settings.cache_clear()


def test_streaming_chat_uses_same_auth_rule(monkeypatch):
    monkeypatch.setenv('AUTH_REQUIRED', 'true')
    from app.core.config import get_settings
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        assert client.post('/api/v1/chat/stream', json={'message': 'hello'}).status_code == 401
        with client.stream('POST', '/api/v1/chat/stream', headers={'X-FinGuard-Role': 'customer'}, json={'message': 'hello'}) as response:
            body = ''.join(response.iter_text())
        assert response.status_code == 200
        assert 'event: message.done' in body
    finally:
        monkeypatch.delenv('AUTH_REQUIRED', raising=False)
        get_settings.cache_clear()


def test_repository_backend_selection(monkeypatch):
    from app.core.config import get_settings
    from app.services import repository
    from app.db.supabase import SupabaseRepository

    previous = repository._REPO
    try:
        repository._REPO = None
        monkeypatch.setenv('SUPABASE_URL', 'https://example.supabase.co')
        monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'service-role')
        get_settings.cache_clear()
        assert isinstance(repository.get_repository(), SupabaseRepository)
        assert repository.active_backend() == 'supabase'

        repository._REPO = None
        monkeypatch.delenv('SUPABASE_URL', raising=False)
        monkeypatch.delenv('SUPABASE_SERVICE_ROLE_KEY', raising=False)
        monkeypatch.setenv('FINGUARD_REPOSITORY', 'memory')
        get_settings.cache_clear()
        assert repository.active_backend() == 'memory'
    finally:
        repository._REPO = previous
        monkeypatch.delenv('SUPABASE_URL', raising=False)
        monkeypatch.delenv('SUPABASE_SERVICE_ROLE_KEY', raising=False)
        monkeypatch.delenv('FINGUARD_REPOSITORY', raising=False)
        get_settings.cache_clear()


def test_docs_csp_allows_swagger_assets_but_api_stays_strict():
    client = TestClient(app)
    docs_csp = client.get('/api/v1/docs').headers['content-security-policy']
    assert 'cdn.jsdelivr.net' in docs_csp
    assert "'unsafe-inline'" in docs_csp
    assert client.get('/api/v1/health').headers['content-security-policy'] == "default-src 'self'"
