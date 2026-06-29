from datetime import datetime, timezone
from uuid import uuid4
from app.models.schemas import Conversation, ConversationMessage
_CONVERSATIONS: dict[str, Conversation] = {}
_MESSAGES: list[ConversationMessage] = []

def conversation_exists(conversation_id: str) -> bool:
    return conversation_id in _CONVERSATIONS

def get_or_create_conversation(conversation_id: str | None = None, user_id: str | None = None) -> Conversation:
    cid = conversation_id or str(uuid4())
    conv = _CONVERSATIONS.get(cid)
    if not conv:
        now = datetime.now(timezone.utc).isoformat()
        conv = Conversation(id=cid, user_id=user_id, status="open", created_at=now, updated_at=now)
        _CONVERSATIONS[cid] = conv
    return conv

def add_message(conversation_id: str, role: str, content: str) -> ConversationMessage:
    msg = ConversationMessage(id=str(uuid4()), conversation_id=conversation_id, role=role, content=content, created_at=datetime.now(timezone.utc).isoformat())
    _MESSAGES.append(msg)
    if conversation_id in _CONVERSATIONS: _CONVERSATIONS[conversation_id].updated_at = msg.created_at
    return msg

def history(conversation_id: str) -> list[ConversationMessage]:
    return [m for m in _MESSAGES if m.conversation_id == conversation_id]

def conversations() -> list[Conversation]: return list(_CONVERSATIONS.values())
