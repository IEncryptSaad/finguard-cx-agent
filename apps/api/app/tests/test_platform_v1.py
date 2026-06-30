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
