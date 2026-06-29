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


def insights_dashboard() -> dict:
    ev = events(); base = analytics_summary(); tickets = list_tickets(); convs = conversations()
    complaints = [e for e in ev if e["event_type"] == "feedback.classified" and e["payload"].get("category") in ("Complaint", "Bug", "Fraud", "Dispute")]
    return {
        "conversation_trends": {"total": len(convs), "recent": len(convs[-10:])},
        "feature_request_trends": {"recent_created": len([e for e in ev if e["event_type"] == "product.item_created"])},
        "top_complaints": [e["payload"].get("category") for e in complaints[-10:]],
        "knowledge_gaps": [e["payload"] for e in ev if e["event_type"] == "knowledge.searched"][-10:],
        "agent_performance": {"resolved_tickets": base["resolved_tickets"], "open_tickets": len([t for t in tickets if t.status == "open"])},
        "ai_provider_usage": base["ai_provider_usage"],
        "resolution_rate": round(base["resolved_tickets"] / len(tickets), 2) if tickets else 0,
        "response_latency": base["average_response_time_ms"],
        "handoff_rate": round(base["escalated_tickets"] / len(convs), 2) if convs else 0,
    }
