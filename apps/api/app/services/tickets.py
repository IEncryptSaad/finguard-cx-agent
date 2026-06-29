from uuid import uuid4
from app.models.schemas import Ticket
_TICKETS: dict[str, Ticket] = {}
def create_ticket(conversation_id: str, summary: str, priority: str = "normal") -> Ticket:
    ticket = Ticket(id=str(uuid4()), conversation_id=conversation_id, summary=summary, priority=priority)
    _TICKETS[ticket.id] = ticket
    return ticket
def list_tickets() -> list[Ticket]:
    return list(_TICKETS.values())
