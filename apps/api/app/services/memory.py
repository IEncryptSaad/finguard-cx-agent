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
        repo = get_repository()
        for c in repo.list('conversations'):
            _CONVERSATIONS[c['id']] = Conversation(**c)
        existing_message_ids = {m.id for m in _MESSAGES}
        for m in repo.list('conversation_messages'):
            if m['id'] not in existing_message_ids:
                _MESSAGES.append(ConversationMessage(**m))
                existing_message_ids.add(m['id'])
    except Exception: pass
_hydrate()

def conversation_exists(conversation_id: str) -> bool:
    _hydrate()
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
    _hydrate()
    return [m for m in _MESSAGES if m.conversation_id == conversation_id]

def conversations() -> list[Conversation]:
    _hydrate()
    return list(_CONVERSATIONS.values())

# Generic memory runtime: scoped key/value records with a provider-compatible shape.
from app.models.schemas import MemoryRecord, MemoryRecordCreate, MemoryScope
from app.services.policy import sanitize_sensitive
_MEMORY_RECORDS: dict[str, MemoryRecord] = {}

def upsert_memory_record(payload: MemoryRecordCreate) -> MemoryRecord:
    now = datetime.now(timezone.utc).isoformat()
    rid = f"{payload.scope}:{payload.workspace_id}:{payload.user_id or payload.session_id or 'global'}:{payload.key}"
    existing = _MEMORY_RECORDS.get(rid)
    record = MemoryRecord(id=rid, scope=payload.scope, key=payload.key, value=sanitize_sensitive(payload.value), user_id=payload.user_id, session_id=payload.session_id, workspace_id=payload.workspace_id, created_at=existing.created_at if existing else now, updated_at=now)
    _MEMORY_RECORDS[rid] = record
    try:
        from app.services.repository import get_repository
        get_repository().put('memory_records', rid, record.model_dump())
    except Exception: pass
    return record

def list_memory_records(scope: MemoryScope|None=None, key: str|None=None, user_id: str|None=None) -> list[MemoryRecord]:
    if not _MEMORY_RECORDS:
        try:
            from app.services.repository import get_repository
            for r in get_repository().list('memory_records'):
                rec=MemoryRecord(**r); _MEMORY_RECORDS[rec.id or rec.key]=rec
        except Exception: pass
    return [r for r in _MEMORY_RECORDS.values() if (scope is None or r.scope == scope) and (key is None or r.key == key) and (user_id is None or r.user_id == user_id)]
