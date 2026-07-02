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



def test_demo_admin_read_access_allows_only_dashboard_reads(monkeypatch):
    monkeypatch.setenv('AUTH_REQUIRED', 'true')
    monkeypatch.setenv('APP_ENV', 'production')
    monkeypatch.setenv('DEMO_ADMIN_READ_ACCESS', 'true')
    from app.core.config import get_settings
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        dashboard_read_paths = [
            '/api/v1/admin/summary',
            '/api/v1/conversations',
            '/api/v1/conversations/demo/messages',
            '/api/v1/audit',
            '/api/v1/tickets',
            '/api/v1/knowledge',
            '/api/v1/settings',
            '/api/v1/plugins',
            '/api/v1/workflows',
            '/api/v1/roadmap',
            '/api/v1/feedback',
            '/api/v1/analytics/insights',
            '/api/v1/marketplace',
        ]
        for path in dashboard_read_paths:
            assert client.get(path).status_code == 200, path

        assert client.post('/api/v1/tickets', json={
            'conversation_id': 'demo',
            'summary': 'must stay protected',
            'priority': 'normal',
        }).status_code == 401
        assert client.post('/api/v1/knowledge', json={
            'title': 'private',
            'body': 'must stay protected',
            'tags': [],
        }).status_code == 401
        assert client.post('/api/v1/workflows', json={
            'name': 'protected',
            'trigger': 'manual',
            'conditions': [],
            'actions': [],
            'retry_policy': {},
            'status': 'draft',
        }).status_code == 401
        assert client.post('/api/v1/roadmap', json={
            'type': 'feature',
            'title': 'protected',
            'description': 'must stay protected',
            'status': 'open',
            'priority': 'normal',
            'labels': [],
            'linked_conversations': [],
            'attachments': [],
        }).status_code == 401
        assert client.post('/api/v1/feedback/conversations/demo/classify').status_code == 401
        assert client.post('/api/v1/marketplace/install', json={'name': 'demo'}).status_code == 401
        assert client.put('/api/v1/settings', json={
            'active_ai_provider':'mock','model_name':'mock-support-v1','temperature':0.2,'system_prompt':'safe',
            'guardrails_enabled':True,'pii_redaction_enabled':True,'rate_limit_per_minute':60,
            'enabled_plugins':['mock'],'knowledge_source_settings':{}
        }).status_code == 401
    finally:
        monkeypatch.delenv('AUTH_REQUIRED', raising=False)
        monkeypatch.delenv('APP_ENV', raising=False)
        monkeypatch.delenv('DEMO_ADMIN_READ_ACCESS', raising=False)
        get_settings.cache_clear()


def test_dashboard_reads_require_auth_when_demo_admin_read_access_disabled(monkeypatch):
    monkeypatch.setenv('AUTH_REQUIRED', 'true')
    monkeypatch.setenv('APP_ENV', 'production')
    monkeypatch.delenv('DEMO_ADMIN_READ_ACCESS', raising=False)
    from app.core.config import get_settings
    get_settings.cache_clear()
    try:
        client = TestClient(app)
        protected_read_paths = [
            '/api/v1/admin/summary',
            '/api/v1/conversations',
            '/api/v1/conversations/demo/messages',
            '/api/v1/audit',
            '/api/v1/tickets',
            '/api/v1/knowledge',
            '/api/v1/settings',
            '/api/v1/plugins',
            '/api/v1/workflows',
            '/api/v1/roadmap',
            '/api/v1/feedback',
            '/api/v1/analytics/insights',
            '/api/v1/marketplace',
        ]
        for path in protected_read_paths:
            assert client.get(path).status_code == 401, path
    finally:
        monkeypatch.delenv('AUTH_REQUIRED', raising=False)
        monkeypatch.delenv('APP_ENV', raising=False)
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


def test_supabase_append_uses_plain_insert_headers(monkeypatch):
    import json
    from app.core.config import Settings
    from app.db import supabase
    from app.db.supabase import SupabaseRepository

    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def read(self):
            return b''

    def fake_urlopen(req, timeout):
        captured['method'] = req.get_method()
        captured['url'] = req.full_url
        captured['prefer'] = req.get_header('Prefer')
        captured['body'] = json.loads(req.data.decode())
        return FakeResponse()

    monkeypatch.setattr(supabase.request, 'urlopen', fake_urlopen)
    repo = SupabaseRepository(Settings(supabase_url='https://example.supabase.co', supabase_service_role_key='service-role'))

    repo.append('audit_logs', {'event_type': 'chat', 'payload': {'ok': True}})

    assert captured['method'] == 'POST'
    assert captured['url'] == 'https://example.supabase.co/rest/v1/audit_logs'
    assert captured['prefer'] == 'return=minimal'
    assert 'resolution=merge-duplicates' not in captured['prefer']
    assert 'id' not in captured['body']


def test_supabase_put_keeps_upsert_resolution_headers(monkeypatch):
    import json
    from app.core.config import Settings
    from app.db import supabase
    from app.db.supabase import SupabaseRepository

    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def read(self):
            return b''

    def fake_urlopen(req, timeout):
        captured['url'] = req.full_url
        captured['prefer'] = req.get_header('Prefer')
        captured['body'] = json.loads(req.data.decode())
        return FakeResponse()

    monkeypatch.setattr(supabase.request, 'urlopen', fake_urlopen)
    repo = SupabaseRepository(Settings(supabase_url='https://example.supabase.co', supabase_service_role_key='service-role'))

    repo.put('tickets', 'ticket-1', {'summary': 'hello', 'assignee': 'agent-1', 'internal_notes': ['note']})

    assert captured['url'] == 'https://example.supabase.co/rest/v1/tickets?on_conflict=id'
    assert captured['prefer'] == 'return=minimal,resolution=merge-duplicates'
    assert captured['body']['id'] == 'ticket-1'
    assert captured['body']['assignee'] == 'agent-1'
    assert captured['body']['internal_notes'] == ['note']


def test_audit_log_supabase_append_allows_database_id_default(monkeypatch):
    import json
    from app.core.config import get_settings
    from app.db import supabase
    from app.services import repository
    from app.services.audit import log_event

    captured = {}
    previous_repo = repository._REPO

    class FakeResponse:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False
        def read(self):
            return b''

    def fake_urlopen(req, timeout):
        captured['url'] = req.full_url
        captured['prefer'] = req.get_header('Prefer')
        captured['body'] = json.loads(req.data.decode())
        return FakeResponse()

    monkeypatch.setattr(supabase.request, 'urlopen', fake_urlopen)
    monkeypatch.setenv('SUPABASE_URL', 'https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'service-role')
    get_settings.cache_clear()
    repository._REPO = None
    try:
        event = log_event('review_test', {'actor': 'reviewer@example.com', 'value': 1})
    finally:
        repository._REPO = previous_repo
        monkeypatch.delenv('SUPABASE_URL', raising=False)
        monkeypatch.delenv('SUPABASE_SERVICE_ROLE_KEY', raising=False)
        get_settings.cache_clear()

    assert event['event_type'] == 'review_test'
    assert captured['url'] == 'https://example.supabase.co/rest/v1/audit_logs'
    assert captured['prefer'] == 'return=minimal'
    assert 'resolution=merge-duplicates' not in captured['prefer']
    assert captured['body']['event_type'] == 'review_test'
    assert 'id' not in captured['body']


def test_ticket_update_persists_assignee_and_internal_notes_through_repository(monkeypatch):
    from app.models.schemas import Ticket
    from app.services import repository
    from app.services import tickets as ticket_service

    captured = {}
    previous_repo = repository._REPO
    previous_tickets = dict(ticket_service._TICKETS)

    class FakeRepository:
        def put(self, table, key, value):
            captured['table'] = table
            captured['key'] = key
            captured['value'] = value

        def append(self, table, value):
            return None

    repository._REPO = FakeRepository()
    ticket_service._TICKETS.clear()
    ticket_service._TICKETS['ticket-1'] = Ticket(
        id='ticket-1',
        conversation_id='conversation-1',
        summary='Need help',
    )
    try:
        updated = ticket_service.update_ticket(
            'ticket-1',
            assignee='agent-1',
            internal_note='private note',
        )
    finally:
        repository._REPO = previous_repo
        ticket_service._TICKETS.clear()
        ticket_service._TICKETS.update(previous_tickets)

    assert updated.assignee == 'agent-1'
    assert updated.internal_notes == ['private note']
    assert captured['table'] == 'tickets'
    assert captured['key'] == 'ticket-1'
    assert captured['value']['assignee'] == 'agent-1'
    assert captured['value']['internal_notes'] == ['private note']


def test_audit_events_hydrates_after_early_log_event_without_repeating(monkeypatch):
    from app.services import audit, repository

    persisted = [
        {
            'event_type': 'persisted.event',
            'payload': {'value': 1},
            'created_at': '2026-07-01T00:00:00+00:00',
        }
    ]
    list_calls = []
    previous_repo = repository._REPO
    previous_events = list(audit._EVENTS)
    previous_hydrated = audit._EVENTS_HYDRATED

    class FakeRepository:
        def list(self, table):
            list_calls.append(table)
            return list(persisted)

        def append(self, table, value):
            persisted.append(value)

    repository._REPO = FakeRepository()
    audit._EVENTS.clear()
    audit._EVENTS_HYDRATED = False
    try:
        early_event = audit.log_event('early.event', {'value': 2})

        first_events = audit.events()
        second_events = audit.events()
    finally:
        repository._REPO = previous_repo
        audit._EVENTS[:] = previous_events
        audit._EVENTS_HYDRATED = previous_hydrated

    assert first_events == [persisted[0], early_event]
    assert second_events == first_events
    assert list_calls == ['audit_logs']



def test_audit_events_retries_hydration_after_repository_failure(monkeypatch):
    from app.services import audit, repository

    persisted = [
        {
            'event_type': 'persisted.event',
            'payload': {'value': 1},
            'created_at': '2026-07-01T00:00:00+00:00',
        }
    ]
    list_calls = []
    previous_repo = repository._REPO
    previous_events = list(audit._EVENTS)
    previous_hydrated = audit._EVENTS_HYDRATED

    class FakeRepository:
        def list(self, table):
            list_calls.append(table)
            if len(list_calls) == 1:
                raise RuntimeError('transient repository failure')
            return list(persisted)

        def append(self, table, value):
            return None

    repository._REPO = FakeRepository()
    audit._EVENTS.clear()
    audit._EVENTS_HYDRATED = False
    try:
        failed_events = audit.events()
        assert audit._EVENTS_HYDRATED is False

        retried_events = audit.events()
        assert audit._EVENTS_HYDRATED is True
    finally:
        repository._REPO = previous_repo
        audit._EVENTS[:] = previous_events
        audit._EVENTS_HYDRATED = previous_hydrated

    assert failed_events == []
    assert retried_events == persisted
    assert list_calls == ['audit_logs', 'audit_logs']

def test_anonymous_chat_auth_required_precedes_unconfigured_provider(monkeypatch):
    from app.core.config import get_settings
    from app.services import settings as settings_service

    previous_settings = settings_service._SETTINGS
    monkeypatch.setenv('AUTH_REQUIRED', 'true')
    monkeypatch.setenv('LLM_PROVIDER', 'openai')
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    get_settings.cache_clear()
    settings_service._SETTINGS = None
    try:
        client = TestClient(app)
        response = client.post('/api/v1/chat', json={'message': 'hello'})
        assert response.status_code == 401

        authorized = client.post('/api/v1/chat', headers={'X-FinGuard-Role': 'customer'}, json={'message': 'hello'})
        assert authorized.status_code == 503
    finally:
        settings_service._SETTINGS = previous_settings
        monkeypatch.delenv('AUTH_REQUIRED', raising=False)
        monkeypatch.delenv('LLM_PROVIDER', raising=False)
        get_settings.cache_clear()


def test_anonymous_stream_auth_required_precedes_unconfigured_provider(monkeypatch):
    from app.core.config import get_settings
    from app.services import settings as settings_service

    previous_settings = settings_service._SETTINGS
    monkeypatch.setenv('AUTH_REQUIRED', 'true')
    monkeypatch.setenv('LLM_PROVIDER', 'openai')
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    get_settings.cache_clear()
    settings_service._SETTINGS = None
    try:
        client = TestClient(app)
        response = client.post('/api/v1/chat/stream', json={'message': 'hello'})
        assert response.status_code == 401

        authorized = client.post('/api/v1/chat/stream', headers={'X-FinGuard-Role': 'customer'}, json={'message': 'hello'})
        assert authorized.status_code == 503
    finally:
        settings_service._SETTINGS = previous_settings
        monkeypatch.delenv('AUTH_REQUIRED', raising=False)
        monkeypatch.delenv('LLM_PROVIDER', raising=False)
        get_settings.cache_clear()
