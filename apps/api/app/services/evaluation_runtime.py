from datetime import datetime, timezone
from uuid import uuid4
from app.models.schemas import EvaluationDataset, EvaluationRunRequest, EvaluationRun
from app.services.audit import log_event
_DATASETS: dict[str, EvaluationDataset] = {}
_RUNS: list[EvaluationRun] = []
def _now(): return datetime.now(timezone.utc).isoformat()
def create_dataset(ds: EvaluationDataset):
    saved = ds.model_copy(update={'id': ds.id or str(uuid4()), 'created_at': ds.created_at or _now()}); _DATASETS[saved.id]=saved; log_event('evaluation.dataset_created', {'dataset_id': saved.id}); return saved
def list_datasets(): return list(_DATASETS.values())
def run_evaluation(req: EvaluationRunRequest):
    ds = _DATASETS.get(req.dataset_id)
    total = len(ds.items) if ds else 0
    passed = 0
    for item in (ds.items if ds else []):
        expected = item.get('expected')
        actual = item.get('actual') if item.get('actual') is not None else item.get('input', '')
        if isinstance(expected, str) and isinstance(actual, str) and expected in actual:
            passed += 1
    score = round(passed / total, 2) if total else 0
    run = EvaluationRun(id=str(uuid4()), dataset_id=req.dataset_id, status='completed', score=score, metrics={'total': total, 'passed': passed}, created_at=_now())
    _RUNS.append(run); log_event('evaluation.completed', {'dataset_id': req.dataset_id, 'score': score}); return run
def list_runs(): return _RUNS
