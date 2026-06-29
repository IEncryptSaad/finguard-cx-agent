from datetime import datetime, timezone
from uuid import uuid4
from app.models.schemas import Workflow, WorkflowCreate, WorkflowExecution
from app.services.audit import log_event

_WORKFLOWS: dict[str, Workflow] = {}
_EXECUTIONS: list[WorkflowExecution] = []
def _now() -> str: return datetime.now(timezone.utc).isoformat()
def create_workflow(payload: WorkflowCreate) -> Workflow:
    wf = Workflow(id=str(uuid4()), name=payload.name, trigger=payload.trigger, conditions=payload.conditions, actions=payload.actions, retry_policy=payload.retry_policy, status=payload.status, created_at=_now(), updated_at=_now())
    _WORKFLOWS[wf.id] = wf; log_event("workflow.created", {"workflow_id": wf.id, "trigger": wf.trigger}); return wf
def list_workflows() -> list[Workflow]: return list(_WORKFLOWS.values())
def run_workflow(workflow_id: str, context: dict | None = None) -> WorkflowExecution:
    wf = _WORKFLOWS[workflow_id]
    execution = WorkflowExecution(id=str(uuid4()), workflow_id=workflow_id, status="succeeded" if wf.status == "active" else "skipped", started_at=_now(), finished_at=_now(), attempts=1, input=context or {}, output={"actions": [a.get("type") for a in wf.actions]})
    _EXECUTIONS.append(execution); log_event("workflow.executed", {"workflow_id": workflow_id, "status": execution.status}); return execution
def execution_history(workflow_id: str | None = None) -> list[WorkflowExecution]: return [e for e in _EXECUTIONS if workflow_id is None or e.workflow_id == workflow_id]
