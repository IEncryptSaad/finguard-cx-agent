from fastapi.testclient import TestClient
from app.main import app


def test_enterprise_connectors_rag_prompt_and_tool_governance():
    client = TestClient(app)
    connectors = client.get('/api/v1/connectors').json()
    assert {'webhook','email','slack','notion','google_drive','confluence'} <= {c['name'] for c in connectors}
    assert client.post('/api/v1/connectors/slack/test', json={'channel': 'demo'}).json()['demo'] is True

    client.post('/api/v1/knowledge', json={'title':'Dispute RAG seed','body':'Card dispute support can file a transaction dispute safely.','tags':['card','dispute']})
    indexed = client.post('/api/v1/rag/index')
    assert indexed.status_code == 200 and len(indexed.json()) >= 1
    rag = client.post('/api/v1/rag/query', json={'query': 'card dispute', 'top_k': 2})
    assert rag.status_code == 200
    assert rag.json()['grounded'] is True
    assert rag.json()['citations'][0]['source_id']

    v1 = client.post('/api/v1/prompts', json={'name':'risk.review','template':'Review {{input}}','status':'draft'})
    v2 = client.post('/api/v1/prompts', json={'name':'risk.review','template':'Review safely {{input}}','status':'draft'})
    assert v1.status_code == 200 and v2.json()['version'] == 2
    active = client.patch(f"/api/v1/prompts/{v2.json()['id']}/status", json={'status':'active'})
    assert active.status_code == 200 and active.json()['status'] == 'active'
    rollback = client.post('/api/v1/prompts/risk.review/rollback/1')
    assert rollback.status_code == 200 and rollback.json()['version'] == 1

    risky = client.post('/api/v1/actions/refund_payment/run', json={'payload': {'amount': 5}})
    assert risky.status_code == 200 and risky.json()['status'] == 'approval_required'
    denied = client.post('/api/v1/actions/refund_payment/run', json={'payload': {'amount': 5}, 'approved': True, 'actor_permissions': ['workflow:write']})
    assert denied.json()['status'] == 'denied'


def test_enterprise_profile_secrets_and_privacy_foundations():
    client = TestClient(app)
    assert client.get('/api/v1/enterprise/profile').json()['tenant_ready'] is True
    secret = client.post('/api/v1/enterprise/secrets', json={'name':'OPENAI_API_KEY','value':'sk-secret'})
    assert secret.status_code == 200 and secret.json()['value'] == '[REDACTED_SECRET]'
    assert client.post('/api/v1/privacy/export', json={'subject_id':'user-1'}).json()['status'] == 'queued'
    assert client.post('/api/v1/privacy/delete', json={'subject_id':'user-1'}).json()['requires_review'] is True
