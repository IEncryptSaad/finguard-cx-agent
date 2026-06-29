from datetime import datetime, timezone
from typing import Any
_EVENTS: list[dict[str, Any]] = []
def log_event(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    event = {"event_type": event_type, "payload": payload, "created_at": datetime.now(timezone.utc).isoformat()}
    _EVENTS.append(event)
    return event
def events() -> list[dict[str, Any]]:
    return list(_EVENTS)
