from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException, status
from app.models.schemas import ActionDefinition, ActionRunRequest, ActionExecution
from app.services.audit import log_event

_ACTIONS: dict[str, ActionDefinition] = {}
_EXECUTIONS: list[ActionExecution] = []

def _now(): return datetime.now(timezone.utc).isoformat()

def register_builtin_actions():
    if _ACTIONS: return
    for name, category, perms in [
        ('notify_admin','notification',['workflow:write']),
        ('create_ticket','support',['ticket:create']),
        ('summarize_text','ai',['assistant:use']),
    ]:
        _ACTIONS[name] = ActionDefinition(name=name, category=category, description=f'Built-in {name} action', permissions=perms, enabled=True)
register_builtin_actions()

def list_actions(): return list(_ACTIONS.values())
def upsert_action(action: ActionDefinition):
    _ACTIONS[action.name]=action; log_event('action.registered', {'name': action.name}); return action

def run_action(name: str, request: ActionRunRequest):
    action = _ACTIONS.get(name)
    if not action: raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Action not found')
    if not action.enabled: status_value, error, output = 'skipped', 'Action disabled', {}
    elif action.schema and any(k not in request.payload for k in action.schema.get('required', [])): status_value, error, output = 'failed', 'Missing required action payload fields', {}
    else: status_value, error, output = 'succeeded', None, {'echo': request.payload, 'action': name}
    ex = ActionExecution(id=str(uuid4()), action=name, status=status_value, input=request.payload, output=output, error=error, started_at=_now(), finished_at=_now(), attempts=1)
    _EXECUTIONS.append(ex); log_event('action.executed', {'name': name, 'status': status_value}); return ex

def action_history(name: str|None=None): return [e for e in _EXECUTIONS if name is None or e.action == name]
