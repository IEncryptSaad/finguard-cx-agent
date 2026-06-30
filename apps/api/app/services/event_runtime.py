from datetime import datetime, timezone
from uuid import uuid4
from app.models.schemas import EventSubscription, EventPublishRequest
from app.services.audit import log_event, events
_SUBS: dict[str, EventSubscription] = {}
def _now(): return datetime.now(timezone.utc).isoformat()
def subscribe(sub: EventSubscription):
    sid = sub.id or str(uuid4()); saved = sub.model_copy(update={'id': sid, 'created_at': sub.created_at or _now()}); _SUBS[sid]=saved; log_event('event.subscription_created', {'subscription_id': sid, 'event_type': sub.event_type}); return saved
def list_subscriptions(): return list(_SUBS.values())
def publish(req: EventPublishRequest):
    event = log_event(req.event_type, req.payload)
    matches=[s for s in _SUBS.values() if s.enabled and (s.event_type == req.event_type or s.event_type == '*')]
    for s in matches: log_event('event.delivered', {'subscription_id': s.id, 'event_type': req.event_type})
    return {'event': event, 'matched_subscriptions': len(matches), 'queued': req.async_processing}
def registry():
    names=sorted(set(e['event_type'] for e in events()) | {'chat.responded','workflow.executed','action.executed','knowledge.created','prompt.created'})
    return [{'event_type': n, 'description': f'{n} platform event'} for n in names]
