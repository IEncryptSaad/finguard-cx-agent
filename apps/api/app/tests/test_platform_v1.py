from fastapi.testclient import TestClient
from app.main import app


def test_platform_v1_provider_memory_action_prompt_event_evaluation_observability_cost():
    client = TestClient(app)
    assert any(p['name'] == 'mock' and p['healthy'] for p in client.get('/api/v1/providers').json())
    assert client.post('/api/v1/providers/route', json={'capability': 'chat'}).json()['provider'] == 'mock'
    memory = client.post('/api/v1/memory', json={'scope': 'user', 'key': 'preference', 'value': {'tone': 'concise'}, 'user_id': 'u1'})
    assert memory.status_code == 200
    assert client.get('/api/v1/memory?scope=user&user_id=u1').json()[0]['value']['tone'] == 'concise'
    assert any(a['name'] == 'notify_admin' for a in client.get('/api/v1/actions').json())
    action_run = client.post('/api/v1/actions/notify_admin/run', json={'payload': {'message': 'hello'}})
    assert action_run.status_code == 200 and action_run.json()['status'] == 'succeeded'
    prompt = client.post('/api/v1/prompts', json={'name': 'ops.digest', 'category': 'operations', 'template': 'Summarize {{input}}', 'status': 'active'})
    assert prompt.status_code == 200 and prompt.json()['version'] == 1
    assert client.get('/api/v1/prompts?category=operations').json()[0]['name'] == 'ops.digest'
    sub = client.post('/api/v1/events/subscriptions', json={'event_type': 'platform.test', 'target': 'audit'})
    assert sub.status_code == 200
    published = client.post('/api/v1/events/publish', json={'event_type': 'platform.test', 'payload': {'ok': True}})
    assert published.status_code == 200 and published.json()['matched_subscriptions'] >= 1
    dataset = client.post('/api/v1/evaluations/datasets', json={'name': 'smoke', 'items': [{'input': 'hello', 'expected': 'hello'}]})
    assert dataset.status_code == 200
    run = client.post('/api/v1/evaluations/runs', json={'dataset_id': dataset.json()['id']})
    assert run.status_code == 200 and run.json()['score'] == 1
    assert client.get('/api/v1/observability/health').status_code == 200
    cost = client.get('/api/v1/cost/usage')
    assert cost.status_code == 200 and cost.json()['estimated_cost'] == 0


def test_provider_route_returns_no_route_when_capability_not_advertised():
    client = TestClient(app)
    response = client.post('/api/v1/providers/route', json={'capability': 'embedding'})
    assert response.status_code == 200
    payload = response.json()
    assert payload['provider'] == ''
    assert payload['reason'] == 'no route available'
    assert payload['failover'] == []


def test_memory_records_are_sanitized_before_persistence():
    client = TestClient(app)
    sensitive = {
        'api_key': 'sk-memory-api-key-123',
        'password': 'memory-password-123',
        'token': 'memory-token-123',
        'email': 'user@example.com',
        'phone': '+1 415-555-2671',
        'card': '4111 1111 1111 1111',
        'account': 'account number 1234567890',
    }
    response = client.post('/api/v1/memory', json={'scope': 'user', 'key': 'sensitive-regression', 'value': sensitive, 'user_id': 'sensitive-user'})
    assert response.status_code == 200
    body = response.text
    records = client.get('/api/v1/memory?scope=user&user_id=sensitive-user')
    assert records.status_code == 200
    body += records.text
    for secret in sensitive.values():
        assert secret not in body
    assert '[REDACTED' in body


def test_evaluation_dataset_rejects_malformed_items():
    client = TestClient(app)
    malformed_payloads = [
        {'name': 'missing-input', 'items': [{'expected': 'hello'}]},
        {'name': 'missing-expected', 'items': [{'input': 'hello'}]},
        {'name': 'invalid-input', 'items': [{'input': 123, 'expected': 'hello'}]},
        {'name': 'invalid-actual', 'items': [{'input': 'hello', 'expected': 'hello', 'actual': 123}]},
    ]
    for payload in malformed_payloads:
        response = client.post('/api/v1/evaluations/datasets', json=payload)
        assert response.status_code == 422


def test_memory_credential_like_keys_redact_values_directly():
    client = TestClient(app)
    sensitive = {
        'access_token': 'access-token-secret-value',
        'client_secret': 'client-secret-value',
        'refresh_token': 'refresh-token-secret-value',
        'id_token': 'id-token-secret-value',
        'api_key': 'api-key-secret-value',
        'secret_key': 'secret-key-secret-value',
        'private_key': 'private-key-secret-value',
    }
    response = client.post('/api/v1/memory', json={'scope': 'user', 'key': 'credential-keys', 'value': sensitive, 'user_id': 'credential-key-user'})
    assert response.status_code == 200
    assert response.json()['value'] == {key: '[REDACTED_CREDENTIAL]' for key in sensitive}

    records = client.get('/api/v1/memory?scope=user&user_id=credential-key-user')
    assert records.status_code == 200
    body = response.text + records.text
    for secret in sensitive.values():
        assert secret not in body


def test_evaluation_dataset_rejects_actual_null():
    client = TestClient(app)
    response = client.post('/api/v1/evaluations/datasets', json={'name': 'actual-null', 'items': [{'input': 'hello', 'expected': 'hello', 'actual': None}]})
    assert response.status_code == 422


def test_evaluation_missing_actual_uses_input_safely():
    client = TestClient(app)
    dataset = client.post('/api/v1/evaluations/datasets', json={'name': 'missing-actual', 'items': [{'input': 'hello world', 'expected': 'hello'}]})
    assert dataset.status_code == 200
    run = client.post('/api/v1/evaluations/runs', json={'dataset_id': dataset.json()['id']})
    assert run.status_code == 200
    assert run.json()['metrics']['passed'] == 1


def test_evaluation_valid_actual_is_used_safely():
    client = TestClient(app)
    dataset = client.post('/api/v1/evaluations/datasets', json={'name': 'valid-actual', 'items': [{'input': 'input text', 'expected': 'needle', 'actual': 'actual needle text'}]})
    assert dataset.status_code == 200
    run = client.post('/api/v1/evaluations/runs', json={'dataset_id': dataset.json()['id']})
    assert run.status_code == 200
    assert run.json()['score'] == 1
