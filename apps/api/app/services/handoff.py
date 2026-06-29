from app.services.tickets import create_ticket
def request_handoff(conversation_id: str, summary: str):
    return create_ticket(conversation_id, summary, priority="high")
