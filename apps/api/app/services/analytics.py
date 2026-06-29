from datetime import datetime
from app.services.audit import events
from app.services.memory import conversations
from app.services.tickets import list_tickets

def analytics_summary() -> dict:
    ev = events(); tickets = list_tickets(); convs = conversations()
    response_times = [e["payload"].get("response_time_ms", 0) for e in ev if e["event_type"] == "chat.responded"]
    provider_usage: dict[str, int] = {}
    for e in ev:
        if e["event_type"] == "ai.provider_used":
            provider = e["payload"].get("provider", "unknown")
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
    return {
        "total_conversations": len(convs),
        "resolved_tickets": len([t for t in tickets if t.status in ("resolved", "closed")]),
        "escalated_tickets": len([t for t in tickets if t.status == "escalated" or t.priority in ("high", "urgent")]),
        "average_response_time_ms": round(sum(response_times) / len(response_times), 2) if response_times else 0,
        "ai_provider_usage": provider_usage or {"mock": 0},
        "knowledge_searches": len([e for e in ev if e["event_type"] == "knowledge.searched"]),
        "recent_audit_events": ev[-10:],
    }
