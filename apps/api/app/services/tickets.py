from uuid import uuid4
from fastapi import HTTPException, status as http_status
from app.models.schemas import Ticket
from app.services.audit import log_event
_TICKETS: dict[str, Ticket] = {}

def _persist(ticket: Ticket):
    try:
        from app.services.repository import get_repository
        get_repository().put('tickets', ticket.id, ticket.model_dump())
    except Exception: pass

def _hydrate():
    try:
        from app.services.repository import get_repository
        for t in get_repository().list('tickets'): _TICKETS[t['id']] = Ticket(**t)
    except Exception: pass
_hydrate()
def create_ticket(conversation_id: str, summary: str, priority: str = "normal") -> Ticket:
    ticket = Ticket(id=str(uuid4()), conversation_id=conversation_id, summary=summary, priority=priority)
    _TICKETS[ticket.id] = ticket; _persist(ticket)
    log_event("ticket.created", {"ticket_id": ticket.id, "conversation_id": conversation_id, "priority": priority})
    return ticket
def list_tickets() -> list[Ticket]:
    return list(_TICKETS.values())
def update_ticket(ticket_id: str, *, status: str | None = None, priority: str | None = None, summary: str | None = None, assignee: str | None = None, internal_note: str | None = None) -> Ticket:
    ticket = _TICKETS.get(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if status: ticket.status = status
    if priority: ticket.priority = priority
    if summary: ticket.summary = summary
    if assignee is not None: ticket.assignee = assignee
    if internal_note: ticket.internal_notes = [*ticket.internal_notes, internal_note]
    _persist(ticket)
    log_event("ticket.updated", {"ticket_id": ticket_id, "status": ticket.status, "priority": ticket.priority, "assignee": ticket.assignee, "internal_note_added": bool(internal_note)})
    return ticket
