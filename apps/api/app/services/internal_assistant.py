from app.models.schemas import InternalAssistantRequest, InternalAssistantResponse
from app.services.knowledge import search_articles
from app.services.memory import history
from app.services.tickets import list_tickets

async def answer_internal(payload: InternalAssistantRequest, agent) -> InternalAssistantResponse:
    q = payload.query.lower(); sources=[]
    if payload.conversation_id:
        sources += [f"conversation:{m.id}" for m in history(payload.conversation_id)[-5:]]
    articles = search_articles(payload.query)[:3]; sources += [f"knowledge:{a.id}" for a in articles]
    ticket_bits = [t.summary for t in list_tickets() if payload.conversation_id is None or t.conversation_id == payload.conversation_id][:3]
    context = "\n".join([a.body for a in articles] + ticket_bits)
    task = "Draft a customer reply" if "draft" in q or "reply" in q else "Answer the internal team question"
    response = await agent.llm.complete(f"{task}: {payload.query}\nContext:\n{context}")
    return InternalAssistantResponse(answer=response, sources=sources, suggested_actions=["search_knowledge", "summarize_tickets", "draft_reply"])
