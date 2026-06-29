from datetime import datetime, timezone
from uuid import uuid4
from app.models.schemas import Workflow, WorkflowCreate, WorkflowExecution
from app.services.audit import log_event

_WORKFLOWS: dict[str, Workflow] = {}
_EXECUTIONS: list[WorkflowExecution] = []


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()



def _retry_attempts(retry_policy: dict) -> tuple[int, str | None]:
    max_attempts = retry_policy.get("max_attempts", 1) or 1
    if isinstance(max_attempts, bool):
        return 1, "Invalid retry_policy.max_attempts"

    try:
        attempts = int(max_attempts)
    except (TypeError, ValueError):
        return 1, "Invalid retry_policy.max_attempts"

    if attempts != max_attempts and str(attempts) != str(max_attempts):
        return 1, "Invalid retry_policy.max_attempts"
    if attempts < 0 or attempts > 10:
        return 1, "Invalid retry_policy.max_attempts"

    return attempts, None

def create_workflow(payload: WorkflowCreate) -> Workflow:
    now = _now()
    wf = Workflow(
        id=str(uuid4()),
        name=payload.name,
        trigger=payload.trigger,
        conditions=payload.conditions,
        actions=payload.actions,
        retry_policy=payload.retry_policy,
        status=payload.status,
        created_at=now,
        updated_at=now,
    )
    _WORKFLOWS[wf.id] = wf
    log_event("workflow.created", {"workflow_id": wf.id, "trigger": wf.trigger})
    return wf


def list_workflows() -> list[Workflow]:
    return list(_WORKFLOWS.values())


def run_workflow(workflow_id: str, context: dict | None = None) -> WorkflowExecution:
    wf = _WORKFLOWS.get(workflow_id)
    if wf is None:
        execution = WorkflowExecution(
            id=str(uuid4()),
            workflow_id=workflow_id,
            status="failed",
            started_at=_now(),
            finished_at=_now(),
            attempts=1,
            input=context or {},
            output={},
            error="Workflow not found",
        )
        _EXECUTIONS.append(execution)
        log_event("workflow.failed", {"workflow_id": workflow_id, "reason": "not_found"})
        return execution

    attempts, retry_error = _retry_attempts(wf.retry_policy)
    if retry_error is not None:
        status = "failed"
        error = retry_error
    elif wf.status != "active":
        status = "skipped"
        error = None
    elif any(not isinstance(action, dict) or "type" not in action for action in wf.actions):
        status = "failed"
        error = "Workflow action is missing a type"
    else:
        status = "succeeded"
        error = None

    execution = WorkflowExecution(
        id=str(uuid4()),
        workflow_id=workflow_id,
        status=status,
        started_at=_now(),
        finished_at=_now(),
        attempts=1 if status != "failed" else attempts,
        input=context or {},
        output={"actions": [a.get("type") for a in wf.actions if isinstance(a, dict)]} if status != "failed" else {},
        error=error,
    )
    _EXECUTIONS.append(execution)
    log_event("workflow.executed", {"workflow_id": workflow_id, "status": execution.status})
    return execution


def execution_history(workflow_id: str | None = None) -> list[WorkflowExecution]:
    return [e for e in _EXECUTIONS if workflow_id is None or e.workflow_id == workflow_id]
