import json
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from app.agent.llm import ProviderConfigurationError, provider_from_name
from app.agent.orchestrator import AgentOrchestrator
from app.auth.deps import require, require_chat_access, require_demo_admin_read
from app.core.config import get_settings, Settings
from app.middleware.errors import error_response
from app.models.schemas import *
from app.plugins.registry import plugin_catalog
from app.services.analytics import analytics_summary, insights_dashboard
from app.services.audit import events
from app.services.knowledge import create_article, delete_article, ingest_document, list_articles, search_articles, update_article
from app.services.memory import conversations, history
from app.services.repository import active_backend, paginate
from app.services.settings import get_app_settings, update_app_settings
from app.services.tickets import create_ticket, list_tickets, redact_ticket_summary, update_ticket
from app.services.feedback import classify_conversation, create_product_item, get_classification, list_classifications, list_product_items, product_dashboard
from app.services.internal_assistant import answer_internal
from app.services.marketplace import install_plugin, list_marketplace
from app.services.workflows import create_workflow, execution_history, list_workflows, run_workflow
router = APIRouter(prefix='/api/v1', responses={400:{'model':ErrorResponse},401:{'model':ErrorResponse},403:{'model':ErrorResponse},404:{'model':ErrorResponse},422:{'model':ErrorResponse},500:{'model':ErrorResponse}})

def _page(items, page:int, page_size:int, sort:str|None, order:str, paginated:bool):
    return paginate(items,page,page_size,sort,order) if paginated else list(items)

def orchestrator(settings: Settings = Depends(get_settings)) -> AgentOrchestrator:
    try: return AgentOrchestrator(provider_from_name(get_app_settings().active_ai_provider or settings.llm_provider))
    except ProviderConfigurationError as exc:
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail={'reason':'AI provider is not configured','provider_error':str(exc)})

@router.post('/chat', response_model=ChatResponse)
async def chat(payload: ChatRequest, user=Depends(require_chat_access), agent: AgentOrchestrator = Depends(orchestrator)): return await agent.handle_chat(payload.message, payload.conversation_id, payload.user_id)
@router.post('/chat/stream')
async def chat_stream(payload: ChatRequest, user=Depends(require_chat_access), agent: AgentOrchestrator = Depends(orchestrator)):
    async def gen():
        yield 'event: metadata\ndata: {"status":"started"}\n\n'
        try:
            res = await agent.handle_chat(payload.message, payload.conversation_id, payload.user_id)
            for token in res.message.split(' '):
                yield f"event: message.delta\ndata: {json.dumps({'delta': token + ' '})}\n\n"
            yield f"event: message.done\ndata: {res.model_dump_json()}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps(error_response('stream_error','Streaming failed', {'type': exc.__class__.__name__}))}\n\n"
    return StreamingResponse(gen(), media_type='text/event-stream')

@router.get('/conversations')
def list_conversations(page:int=1,page_size:int=50,sort:str|None='updated_at',order:str='desc',paginated:bool=False, user=Depends(require_demo_admin_read('conversation:read'))): return _page(conversations(),page,page_size,sort,order,paginated)
@router.get('/conversations/{conversation_id}/messages')
def conversation_messages(conversation_id: str, user=Depends(require_demo_admin_read('conversation:read'))): return history(conversation_id)
@router.get('/tickets')
def tickets(page:int=1,page_size:int=50,status:str|None=None,priority:str|None=None,paginated:bool=False,user=Depends(require_demo_admin_read('ticket:read'))):
    items=[t for t in list_tickets() if (status is None or t.status==status) and (priority is None or t.priority==priority)]; return _page(items,page,page_size,'id','desc',paginated)
@router.post('/tickets')
def ticket(payload: TicketCreate, user=Depends(require('ticket:create'))): return create_ticket(payload.conversation_id, payload.summary, payload.priority)
@router.post('/chat/tickets')
def chat_ticket(payload: TicketCreate, user=Depends(require_chat_access)):
    return create_ticket(payload.conversation_id, redact_ticket_summary(payload.summary), payload.priority)
@router.patch('/tickets/{ticket_id}')
def ticket_update(ticket_id: str, payload: TicketUpdate, user=Depends(require('ticket:update'))): return update_ticket(ticket_id, status=payload.status, priority=payload.priority, summary=payload.summary, assignee=payload.assignee, internal_note=payload.internal_note)
@router.get('/knowledge', response_model=list[KnowledgeArticle]|dict)
def knowledge(q: str|None=None,page:int=1,page_size:int=50,paginated:bool=False,user=Depends(require_demo_admin_read('knowledge:read'))): return _page(search_articles(q) if q is not None else list_articles(),page,page_size,'id','desc',paginated)
@router.post('/knowledge', response_model=KnowledgeArticle)
def knowledge_create(payload: KnowledgeArticleCreate, user=Depends(require('knowledge:write'))): return create_article(payload.title, payload.body, payload.tags)
@router.put('/knowledge/{article_id}', response_model=KnowledgeArticle)
def knowledge_update(article_id: str, payload: KnowledgeArticleUpdate, user=Depends(require('knowledge:write'))): return update_article(article_id, payload.title, payload.body, payload.tags)
@router.delete('/knowledge/{article_id}')
def knowledge_delete(article_id: str, user=Depends(require('knowledge:write'))): delete_article(article_id); return {'deleted': True}
@router.post('/knowledge/ingest', response_model=KnowledgeArticle)
async def knowledge_ingest(file: UploadFile = File(...), user=Depends(require('knowledge:write'))): return ingest_document(file.filename or 'document.txt', await file.read())
@router.get('/audit')
def audit(page:int=1,page_size:int=50,paginated:bool=False,user=Depends(require_demo_admin_read('audit:read'))): return _page(events(),page,page_size,'created_at','desc',paginated)
@router.get('/analytics')
def analytics(user=Depends(require_demo_admin_read('analytics:read'))): return analytics_summary()
@router.get('/plugins')
def plugins(user=Depends(require('settings:read'))): return plugin_catalog()
@router.get('/workflows', response_model=list[Workflow]|dict)
def workflows(page:int=1,page_size:int=50,paginated:bool=False,user=Depends(require('workflow:read'))): return _page(list_workflows(),page,page_size,'updated_at','desc',paginated)
@router.post('/workflows', response_model=Workflow)
def workflow_create(payload: WorkflowCreate, user=Depends(require('workflow:write'))): return create_workflow(payload)
@router.post('/workflows/{workflow_id}/execute', response_model=WorkflowExecution)
def workflow_execute(workflow_id: str, context: dict|None=None, user=Depends(require('workflow:write'))): return run_workflow(workflow_id, context)
@router.get('/workflows/{workflow_id}/executions', response_model=list[WorkflowExecution])
def workflow_executions(workflow_id: str, user=Depends(require('workflow:read'))): return execution_history(workflow_id)
@router.get('/feedback', response_model=list[FeedbackClassification]|dict)
def feedback(page:int=1,page_size:int=50,paginated:bool=False,user=Depends(require('analytics:read'))): return _page(list_classifications(),page,page_size,'created_at','desc',paginated)
@router.post('/feedback/conversations/{conversation_id}/classify', response_model=FeedbackClassification)
def feedback_classify(conversation_id: str, user=Depends(require('analytics:write'))): return classify_conversation(conversation_id)
@router.get('/feedback/conversations/{conversation_id}', response_model=FeedbackClassification)
def feedback_get(conversation_id: str, user=Depends(require('analytics:read'))): return get_classification(conversation_id)
@router.get('/roadmap', response_model=list[ProductItem]|dict)
def roadmap(type: str|None=None,page:int=1,page_size:int=50,paginated:bool=False,user=Depends(require('roadmap:read'))): return _page(list_product_items(type),page,page_size,'updated_at','desc',paginated)
@router.post('/roadmap', response_model=ProductItem)
def roadmap_create(payload: ProductItemCreate, user=Depends(require('roadmap:write'))): return create_product_item(payload)
@router.get('/roadmap/dashboard')
def roadmap_dash(user=Depends(require('roadmap:read'))): return product_dashboard()
@router.get('/analytics/insights')
def insights(user=Depends(require_demo_admin_read('analytics:read'))): return insights_dashboard()
@router.get('/marketplace', response_model=list[MarketplacePlugin])
def marketplace(user=Depends(require('marketplace:read'))): return list_marketplace()
@router.post('/marketplace/install', response_model=MarketplacePlugin)
def marketplace_install(payload: MarketplaceInstallRequest, user=Depends(require('marketplace:write'))): return install_plugin(payload)
@router.post('/assistant/internal', response_model=InternalAssistantResponse)
async def internal_assistant(payload: InternalAssistantRequest, agent: AgentOrchestrator = Depends(orchestrator), user=Depends(require('assistant:use'))): return await answer_internal(payload, agent)
@router.get('/settings', response_model=AppSettings)
def settings_get(user=Depends(require('settings:read'))): return get_app_settings()
@router.put('/settings', response_model=AppSettings)
def settings_put(payload: AppSettings, user=Depends(require('settings:write'))): return update_app_settings(payload)
@router.get('/admin/summary')
def admin_summary(user=Depends(require_demo_admin_read('admin:read'))):
    tickets = list_tickets(); audits=events(); convs=conversations(); analytics=analytics_summary()
    return {'open_tickets': len([t for t in tickets if t.status == 'open']), 'handoffs': len([t for t in tickets if t.priority in ('high','urgent')]), 'conversations': len(convs), 'audit_events': len(audits), 'knowledge_articles': len(list_articles()), **analytics}
@router.get('/health')
def health():
    s=get_app_settings(); degraded = s.active_ai_provider!='mock'
    return {'status': 'degraded' if degraded else 'ok', 'version':'v1.0.0', 'provider': s.active_ai_provider, 'persistence': active_backend()}

@router.get('/providers')
def providers(user=Depends(require('settings:read'))):
    from app.agent.llm import provider_catalog
    return provider_catalog()
@router.get('/providers/{provider_name}/health')
def provider_health(provider_name: str, user=Depends(require('settings:read'))):
    from app.agent.llm import provider_health as ph
    return ph(provider_name)
@router.post('/providers/route', response_model=ProviderRouteResponse)
def provider_route(payload: ProviderRouteRequest, user=Depends(require('settings:read'))):
    from app.agent.llm import route_provider
    return route_provider(payload)

@router.get('/memory', response_model=list[MemoryRecord])
def memory_list(scope: MemoryScope|None=None, key: str|None=None, user_id: str|None=None, user=Depends(require('conversation:read'))):
    from app.services.memory import list_memory_records
    return list_memory_records(scope, key, user_id)
@router.post('/memory', response_model=MemoryRecord)
def memory_put(payload: MemoryRecordCreate, user=Depends(require('conversation:read'))):
    from app.services.memory import upsert_memory_record
    return upsert_memory_record(payload)

@router.get('/actions', response_model=list[ActionDefinition])
def actions(user=Depends(require('settings:read'))):
    from app.services.action_runtime import list_actions
    return list_actions()
@router.post('/actions', response_model=ActionDefinition)
def action_register(payload: ActionDefinition, user=Depends(require('settings:write'))):
    from app.services.action_runtime import upsert_action
    return upsert_action(payload)
@router.post('/actions/{action_name}/run', response_model=ActionExecution)
def action_run(action_name: str, payload: ActionRunRequest, user=Depends(require('workflow:write'))):
    from app.services.action_runtime import run_action
    return run_action(action_name, payload)
@router.get('/actions/{action_name}/executions', response_model=list[ActionExecution])
def action_executions(action_name: str, user=Depends(require('workflow:read'))):
    from app.services.action_runtime import action_history
    return action_history(action_name)

@router.get('/prompts', response_model=list[PromptTemplate])
def prompts(category: str|None=None, user=Depends(require('settings:read'))):
    from app.services.prompt_runtime import list_prompts
    return list_prompts(category)
@router.post('/prompts', response_model=PromptTemplate)
def prompt_create(payload: PromptTemplateCreate, user=Depends(require('settings:write'))):
    from app.services.prompt_runtime import create_prompt
    return create_prompt(payload)
@router.delete('/prompts/{prompt_id}', response_model=PromptTemplate)
def prompt_retire(prompt_id: str, user=Depends(require('settings:write'))):
    from app.services.prompt_runtime import retire_prompt
    return retire_prompt(prompt_id)

@router.get('/events/registry')
def event_registry(user=Depends(require('settings:read'))):
    from app.services.event_runtime import registry
    return registry()
@router.get('/events/subscriptions', response_model=list[EventSubscription])
def event_subscriptions(user=Depends(require('settings:read'))):
    from app.services.event_runtime import list_subscriptions
    return list_subscriptions()
@router.post('/events/subscriptions', response_model=EventSubscription)
def event_subscribe(payload: EventSubscription, user=Depends(require('settings:write'))):
    from app.services.event_runtime import subscribe
    return subscribe(payload)
@router.post('/events/publish')
def event_publish(payload: EventPublishRequest, user=Depends(require('settings:write'))):
    from app.services.event_runtime import publish
    return publish(payload)

@router.get('/evaluations/datasets', response_model=list[EvaluationDataset])
def evaluation_datasets(user=Depends(require('analytics:read'))):
    from app.services.evaluation_runtime import list_datasets
    return list_datasets()
@router.post('/evaluations/datasets', response_model=EvaluationDataset)
def evaluation_dataset_create(payload: EvaluationDataset, user=Depends(require('analytics:write'))):
    from app.services.evaluation_runtime import create_dataset
    return create_dataset(payload)
@router.post('/evaluations/runs', response_model=EvaluationRun)
def evaluation_run(payload: EvaluationRunRequest, user=Depends(require('analytics:write'))):
    from app.services.evaluation_runtime import run_evaluation
    return run_evaluation(payload)
@router.get('/evaluations/runs', response_model=list[EvaluationRun])
def evaluation_runs(user=Depends(require('analytics:read'))):
    from app.services.evaluation_runtime import list_runs
    return list_runs()

@router.get('/observability/health')
def observability_health(user=Depends(require('analytics:read'))):
    from app.services.platform_runtime import platform_health
    return platform_health()
@router.get('/cost/usage')
def cost_usage(user=Depends(require('analytics:read'))):
    from app.services.platform_runtime import cost_usage
    return cost_usage()

@router.get('/connectors')
def connectors(user=Depends(require('settings:read'))):
    from app.services.connectors import connector_catalog
    return connector_catalog()
@router.get('/connectors/{connector_name}/health')
def connector_status(connector_name: str, user=Depends(require('settings:read'))):
    from app.services.connectors import connector_health
    return connector_health(connector_name)
@router.post('/connectors/{connector_name}/test')
def connector_test(connector_name: str, payload: dict|None=None, user=Depends(require('settings:write'))):
    from app.services.connectors import test_connector
    return test_connector(connector_name, payload)

@router.post('/rag/index', response_model=list[RagChunk])
def rag_index(user=Depends(require('knowledge:write'))):
    from app.services.rag_runtime import rebuild_index
    return rebuild_index()
@router.post('/rag/query', response_model=RagQueryResponse)
def rag_query(payload: RagQueryRequest, user=Depends(require('knowledge:read'))):
    from app.services.rag_runtime import query_rag
    return query_rag(payload)
@router.get('/rag/stats')
def rag_status(user=Depends(require('analytics:read'))):
    from app.services.rag_runtime import rag_stats
    return rag_stats()

@router.patch('/prompts/{prompt_id}/status', response_model=PromptTemplate)
def prompt_status(prompt_id: str, payload: PromptStatusUpdate, user=Depends(require('settings:write'))):
    from app.services.prompt_runtime import set_prompt_status
    return set_prompt_status(prompt_id, payload.status)
@router.post('/prompts/{name}/rollback/{version}', response_model=PromptTemplate)
def prompt_rollback(name: str, version: int, user=Depends(require('settings:write'))):
    from app.services.prompt_runtime import rollback_prompt
    return rollback_prompt(name, version)
@router.get('/prompts/{name}/history', response_model=list[PromptTemplate])
def prompt_versions(name: str, user=Depends(require('settings:read'))):
    from app.services.prompt_runtime import prompt_history
    return prompt_history(name)

@router.get('/enterprise/profile', response_model=EnterpriseProfile)
def enterprise_profile(user=Depends(require('settings:read'))):
    return EnterpriseProfile()
@router.post('/enterprise/secrets', response_model=SecretRecord)
def enterprise_secret(payload: SecretRecord, user=Depends(require('settings:write'))):
    from app.services.audit import log_event
    log_event('secret.upserted', {'name': payload.name, 'scope': payload.scope, 'workspace_id': payload.workspace_id, 'redacted': True})
    return SecretRecord(name=payload.name, value='[REDACTED_SECRET]', scope=payload.scope, workspace_id=payload.workspace_id)
@router.post('/privacy/export')
def privacy_export(payload: dict, user=Depends(require('admin:read'))):
    return {'status': 'queued', 'workflow': 'privacy_export', 'subject_id': payload.get('subject_id'), 'free_tier_demo': True}
@router.post('/privacy/delete')
def privacy_delete(payload: dict, user=Depends(require('admin:read'))):
    return {'status': 'queued', 'workflow': 'privacy_delete', 'subject_id': payload.get('subject_id'), 'requires_review': True}
