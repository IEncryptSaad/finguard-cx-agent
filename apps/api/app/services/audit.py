from datetime import datetime, timezone
from typing import Any
from app.services.security import sanitize
_EVENTS: list[dict[str, Any]] = []
def log_event(event_type: str, payload: dict[str, Any], actor: str | None = None) -> dict[str, Any]:
    event = {'event_type': event_type, 'payload': sanitize(payload), 'actor': actor or payload.get('actor') or 'system', 'created_at': datetime.now(timezone.utc).isoformat()}
    _EVENTS.append(event)
    try:
        from app.services.repository import get_repository
        get_repository().append('audit_logs', event)
    except Exception:
        pass
    return event
def events() -> list[dict[str, Any]]:
    return list(_EVENTS)
