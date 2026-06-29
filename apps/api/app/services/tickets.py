from uuid import uuid4
from app.models.schemas import Ticket
from app.services.audit import log_event
_TICKETS: dict[str, Ticket] = {}
def create_ticket(conversation_id: str, summary: str, priority: str = "normal") -> Ticket:
    ticket = Ticket(id=str(uuid4()), conversation_id=conversation_id, summary=summary, priority=priority)
    _TICKETS[ticket.id] = ticket
    log_event("ticket.created", {"ticket_id": ticket.id, "conversation_id": conversation_id, "priority": priority})
    return ticket
def list_tickets() -> list[Ticket]:
    return list(_TICKETS.values())
def update_ticket(ticket_id: str, *, status: str | None = None, priority: str | None = None, summary: str | None = None) -> Ticket:
    ticket = _TICKETS[ticket_id]
    if status: ticket.status = status
    if priority: ticket.priority = priority
    if summary: ticket.summary = summary
    log_event("ticket.updated", {"ticket_id": ticket_id, "status": ticket.status, "priority": ticket.priority})
    return ticket
