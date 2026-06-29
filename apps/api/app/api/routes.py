from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from app.agent.llm import provider_from_name
from app.agent.orchestrator import AgentOrchestrator
from app.core.config import get_settings, Settings
from app.models.schemas import AppSettings, ChatRequest, ChatResponse, KnowledgeArticle, KnowledgeArticleCreate, KnowledgeArticleUpdate, TicketCreate, TicketUpdate
from app.plugins.registry import plugin_catalog
from app.services.analytics import analytics_summary
from app.services.audit import events
from app.services.knowledge import create_article, delete_article, ingest_document, list_articles, search_articles, update_article
from app.services.memory import conversations, history
from app.services.settings import get_app_settings, update_app_settings
from app.services.tickets import create_ticket, list_tickets, update_ticket
router = APIRouter(prefix="/api/v1")
def orchestrator(settings: Settings = Depends(get_settings)) -> AgentOrchestrator:
    return AgentOrchestrator(provider_from_name(get_app_settings().active_ai_provider or settings.llm_provider))
@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, agent: AgentOrchestrator = Depends(orchestrator)):
    return await agent.handle_chat(payload.message, payload.conversation_id, payload.user_id)
@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest, agent: AgentOrchestrator = Depends(orchestrator)):
    async def gen():
        res = await agent.handle_chat(payload.message, payload.conversation_id, payload.user_id)
        yield f"data: {res.model_dump_json()}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
@router.get("/conversations")
def list_conversations(): return conversations()
@router.get("/conversations/{conversation_id}/messages")
def conversation_messages(conversation_id: str): return history(conversation_id)
@router.get("/tickets")
def tickets(): return list_tickets()
@router.post("/tickets")
def ticket(payload: TicketCreate): return create_ticket(payload.conversation_id, payload.summary, payload.priority)
@router.patch("/tickets/{ticket_id}")
def ticket_update(ticket_id: str, payload: TicketUpdate): return update_ticket(ticket_id, status=payload.status, priority=payload.priority, summary=payload.summary)
@router.get("/knowledge", response_model=list[KnowledgeArticle])
def knowledge(q: str | None = None): return search_articles(q) if q is not None else list_articles()
@router.post("/knowledge", response_model=KnowledgeArticle)
def knowledge_create(payload: KnowledgeArticleCreate): return create_article(payload.title, payload.body, payload.tags)
@router.put("/knowledge/{article_id}", response_model=KnowledgeArticle)
def knowledge_update(article_id: str, payload: KnowledgeArticleUpdate): return update_article(article_id, payload.title, payload.body, payload.tags)
@router.delete("/knowledge/{article_id}")
def knowledge_delete(article_id: str): delete_article(article_id); return {"deleted": True}
@router.post("/knowledge/ingest", response_model=KnowledgeArticle)
async def knowledge_ingest(file: UploadFile = File(...)): return ingest_document(file.filename or "document.txt", await file.read())
@router.get("/audit")
def audit(): return events()
@router.get("/analytics")
def analytics(): return analytics_summary()
@router.get("/plugins")
def plugins(): return plugin_catalog()
@router.get("/settings", response_model=AppSettings)
def settings_get(): return get_app_settings()
@router.put("/settings", response_model=AppSettings)
def settings_put(payload: AppSettings): return update_app_settings(payload)
@router.get("/admin/summary")
def admin_summary():
    tickets = list_tickets(); audits=events(); convs=conversations(); analytics=analytics_summary()
    return {"open_tickets": len([t for t in tickets if t.status == "open"]), "handoffs": len([t for t in tickets if t.priority in ("high", "urgent")]), "conversations": len(convs), "audit_events": len(audits), "knowledge_articles": len(list_articles()), **analytics}
@router.get("/health")
def health(): return {"status": "ok", "version": "v1", "provider": get_app_settings().active_ai_provider}
