from datetime import datetime, timezone
from typing import Any
from app.services.security import sanitize
_EVENTS: list[dict[str, Any]] = []
_EVENTS_HYDRATED = False
def log_event(event_type: str, payload: dict[str, Any], actor: str | None = None) -> dict[str, Any]:
    event = {'event_type': event_type, 'payload': sanitize(payload), 'actor': actor or payload.get('actor') or 'system', 'created_at': datetime.now(timezone.utc).isoformat()}
    _EVENTS.append(event)
    try:
        from app.services.repository import get_repository
        get_repository().append('audit_logs', event)
    except Exception:
        pass
    return event
def _same_event(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return (
        left.get('event_type') == right.get('event_type')
        and left.get('created_at') == right.get('created_at')
        and left.get('payload') == right.get('payload')
    )
def events() -> list[dict[str, Any]]:
    global _EVENTS_HYDRATED
    if not _EVENTS_HYDRATED:
        try:
            from app.services.repository import get_repository
            persisted = get_repository().list('audit_logs')
            _EVENTS[:0] = [event for event in persisted if not any(_same_event(event, existing) for existing in _EVENTS)]
        except Exception:
            pass
        _EVENTS_HYDRATED = True
    return list(_EVENTS)
