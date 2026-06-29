from fastapi import APIRouter, Depends
from app.agent.llm import provider_from_name
from app.agent.orchestrator import AgentOrchestrator
from app.core.config import get_settings, Settings
from app.models.schemas import ChatRequest, ChatResponse
from app.services.audit import events
from app.services.tickets import list_tickets
router = APIRouter(prefix="/api/v1")
def orchestrator(settings: Settings = Depends(get_settings)) -> AgentOrchestrator:
    return AgentOrchestrator(provider_from_name(settings.llm_provider))
@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, agent: AgentOrchestrator = Depends(orchestrator)):
    return await agent.handle_chat(payload.message, payload.conversation_id)
@router.get("/admin/summary")
def admin_summary():
    tickets = list_tickets()
    return {"open_tickets": len([t for t in tickets if t.status == "open"]), "handoffs": len(tickets), "conversations": len({e["payload"].get("conversation_id") for e in events() if e["payload"].get("conversation_id")})}
@router.get("/health")
def health(): return {"status": "ok"}
