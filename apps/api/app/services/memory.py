from datetime import datetime, timezone
from uuid import uuid4
from app.models.schemas import Conversation, ConversationMessage
_CONVERSATIONS: dict[str, Conversation] = {}
_MESSAGES: list[ConversationMessage] = []

def _persist():
    try:
        from app.services.repository import get_repository
        repo=get_repository()
        for c in _CONVERSATIONS.values(): repo.put('conversations', c.id, c.model_dump())
        # keep messages keyed by id for idempotence
        for m in _MESSAGES: repo.put('conversation_messages', m.id, m.model_dump())
    except Exception: pass

def _hydrate():
    try:
        from app.services.repository import get_repository
        for c in get_repository().list('conversations'): _CONVERSATIONS[c['id']] = Conversation(**c)
        _MESSAGES.extend(ConversationMessage(**m) for m in get_repository().list('conversation_messages'))
    except Exception: pass
_hydrate()

def conversation_exists(conversation_id: str) -> bool:
    return conversation_id in _CONVERSATIONS

def get_or_create_conversation(conversation_id: str | None = None, user_id: str | None = None) -> Conversation:
    cid = conversation_id or str(uuid4())
    conv = _CONVERSATIONS.get(cid)
    if not conv:
        now = datetime.now(timezone.utc).isoformat()
        conv = Conversation(id=cid, user_id=user_id, status="open", created_at=now, updated_at=now)
        _CONVERSATIONS[cid] = conv; _persist()
    return conv

def add_message(conversation_id: str, role: str, content: str) -> ConversationMessage:
    msg = ConversationMessage(id=str(uuid4()), conversation_id=conversation_id, role=role, content=content, created_at=datetime.now(timezone.utc).isoformat())
    _MESSAGES.append(msg)
    if conversation_id in _CONVERSATIONS: _CONVERSATIONS[conversation_id].updated_at = msg.created_at
    _persist()
    return msg

def history(conversation_id: str) -> list[ConversationMessage]:
    return [m for m in _MESSAGES if m.conversation_id == conversation_id]

def conversations() -> list[Conversation]: return list(_CONVERSATIONS.values())
