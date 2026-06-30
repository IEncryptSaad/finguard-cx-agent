from datetime import datetime, timezone
from uuid import uuid4
from fastapi import HTTPException, status
from app.models.schemas import PromptTemplate, PromptTemplateCreate
from app.services.audit import log_event

_PROMPTS: dict[str, PromptTemplate] = {}
def _now(): return datetime.now(timezone.utc).isoformat()
def seed_prompts():
    if _PROMPTS: return
    create_prompt(PromptTemplateCreate(name='support.default', category='customer_support', template='Answer safely and concisely: {{message}}', config={'temperature':0.2}, status='active'))

def create_prompt(payload: PromptTemplateCreate):
    existing = [p.version for p in _PROMPTS.values() if p.name == payload.name]
    version = (max(existing) + 1) if existing else 1
    p = PromptTemplate(id=str(uuid4()), version=version, created_at=_now(), updated_at=_now(), **payload.model_dump())
    _PROMPTS[p.id]=p; log_event('prompt.created', {'prompt_id': p.id, 'name': p.name, 'version': p.version}); return p

def list_prompts(category: str|None=None):
    seed_prompts(); return [p for p in _PROMPTS.values() if category is None or p.category == category]

def get_prompt(prompt_id: str):
    seed_prompts();
    if prompt_id not in _PROMPTS: raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Prompt not found')
    return _PROMPTS[prompt_id]

def retire_prompt(prompt_id: str):
    p=get_prompt(prompt_id); p.status='retired'; p.updated_at=_now(); log_event('prompt.retired', {'prompt_id': prompt_id}); return p

def set_prompt_status(prompt_id: str, status: str):
    p=get_prompt(prompt_id)
    if status == 'active':
        for other in _PROMPTS.values():
            if other.name == p.name and other.id != p.id and other.status == 'active':
                other.status = 'archived'; other.updated_at = _now()
    p.status=status; p.updated_at=_now(); log_event('prompt.status_changed', {'prompt_id': prompt_id, 'name': p.name, 'version': p.version, 'status': status}); return p

def rollback_prompt(name: str, version: int):
    seed_prompts()
    match=next((p for p in _PROMPTS.values() if p.name == name and p.version == version), None)
    if not match: raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Prompt version not found')
    return set_prompt_status(match.id, 'active')

def prompt_history(name: str):
    seed_prompts(); return sorted([p for p in _PROMPTS.values() if p.name == name], key=lambda p:p.version, reverse=True)
