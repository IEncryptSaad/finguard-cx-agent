from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.agent.llm import provider_from_name
from app.agent.orchestrator import AgentOrchestrator
from app.core.config import get_settings, Settings
from app.models.schemas import ChatRequest, ChatResponse, KnowledgeArticle, KnowledgeArticleCreate, KnowledgeArticleUpdate
from app.services.audit import events
from app.services.knowledge import create_article, delete_article, list_articles, update_article
from app.services.memory import conversations, history
from app.services.tickets import create_ticket, list_tickets
router = APIRouter(prefix="/api/v1")
def orchestrator(settings: Settings = Depends(get_settings)) -> AgentOrchestrator:
    return AgentOrchestrator(provider_from_name(settings.llm_provider))
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
def ticket(payload: dict): return create_ticket(payload.get("conversation_id", "manual"), payload.get("summary", "Manual ticket"), payload.get("priority", "normal"))
@router.get("/knowledge", response_model=list[KnowledgeArticle])
def knowledge(): return list_articles()
@router.post("/knowledge", response_model=KnowledgeArticle)
def knowledge_create(payload: KnowledgeArticleCreate): return create_article(payload.title, payload.body, payload.tags)
@router.put("/knowledge/{article_id}", response_model=KnowledgeArticle)
def knowledge_update(article_id: str, payload: KnowledgeArticleUpdate): return update_article(article_id, payload.title, payload.body, payload.tags)
@router.delete("/knowledge/{article_id}")
def knowledge_delete(article_id: str): delete_article(article_id); return {"deleted": True}
@router.get("/audit")
def audit(): return events()
@router.get("/admin/summary")
def admin_summary():
    tickets = list_tickets(); audits=events(); convs=conversations()
    return {"open_tickets": len([t for t in tickets if t.status == "open"]), "handoffs": len(tickets), "conversations": len(convs), "audit_events": len(audits), "knowledge_articles": len(list_articles())}
@router.get("/health")
def health(): return {"status": "ok", "version": "v1"}
