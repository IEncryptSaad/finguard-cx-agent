from __future__ import annotations

import json
from typing import Any
from urllib import request
from uuid import UUID

from app.core.config import Settings
from app.services.repository import AppRepository, RepositoryError


_TABLE_COLUMNS: dict[str, set[str]] = {
    'conversations': {'id', 'user_id', 'status', 'created_at', 'updated_at', 'workspace_id'},
    'conversation_messages': {'id', 'conversation_id', 'role', 'content', 'created_at'},
    'tickets': {'id', 'conversation_id', 'summary', 'status', 'priority', 'assignee', 'internal_notes', 'created_at'},
    'audit_logs': {'id', 'event_type', 'payload', 'created_at'},
    'knowledge_articles': {'id', 'title', 'body', 'tags', 'created_at', 'updated_at'},
    'memory_records': {'id', 'scope', 'key', 'value', 'user_id', 'session_id', 'workspace_id', 'created_at', 'updated_at'},
    'feedback_classifications': {'id', 'conversation_id', 'category', 'sentiment', 'summary', 'recommended_action', 'confidence_score', 'created_at'},
    'product_items': {'id', 'type', 'title', 'description', 'status', 'priority', 'labels', 'owner', 'linked_conversations', 'attachments', 'ai_summary', 'ai_priority_suggestion', 'duplicate_of', 'created_at', 'updated_at'},
    'workflows': {'id', 'name', 'trigger', 'conditions', 'actions', 'retry_policy', 'status', 'created_at', 'updated_at'},
    'workflow_executions': {'id', 'workflow_id', 'status', 'started_at', 'finished_at', 'attempts', 'input', 'output', 'error'},
    'prompt_templates': {'id', 'name', 'category', 'template', 'config', 'status', 'evaluation_hooks', 'version', 'created_at', 'updated_at'},
    'action_definitions': {'name', 'category', 'description', 'schema', 'output_schema', 'permissions', 'enabled', 'lifecycle', 'side_effect', 'requires_approval'},
    'action_executions': {'id', 'action', 'status', 'input', 'output', 'error', 'started_at', 'finished_at', 'attempts', 'side_effect', 'approval_required'},
    'rag_chunks': {'id', 'source_id', 'source_type', 'chunk_index', 'text', 'metadata', 'permissions', 'created_at'},
    'event_subscriptions': {'id', 'event_type', 'target', 'enabled', 'created_at'},
    'evaluation_datasets': {'id', 'name', 'items', 'created_at'},
    'evaluation_runs': {'id', 'dataset_id', 'status', 'score', 'metrics', 'created_at'},
}
_UUID_COLUMNS: dict[str, set[str]] = {
    'conversations': {'user_id'},
}


def _to_payload(value: Any) -> dict[str, Any]:
    return value.model_dump() if hasattr(value, 'model_dump') else dict(value)


def _is_uuid(value: Any) -> bool:
    try:
        UUID(str(value))
        return True
    except (TypeError, ValueError):
        return False


class SupabaseRepository(AppRepository):
    """Repository backed by Supabase PostgREST using the service role key."""

    backend = 'supabase'

    def __init__(self, settings: Settings):
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise RepositoryError('SupabaseRepository requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY')
        self.base_url = settings.supabase_url.rstrip('/') + '/rest/v1'
        self.service_role_key = settings.supabase_service_role_key

    def _headers(self, *, upsert: bool = False) -> dict[str, str]:
        headers = {
            'apikey': self.service_role_key,
            'Authorization': f'Bearer {self.service_role_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal',
        }
        if upsert:
            headers['Prefer'] = 'return=minimal,resolution=merge-duplicates'
        return headers

    def _clean_payload(self, table: str, payload: dict[str, Any]) -> dict[str, Any]:
        columns = _TABLE_COLUMNS.get(table)
        cleaned = {k: v for k, v in payload.items() if columns is None or k in columns}
        for column in _UUID_COLUMNS.get(table, set()):
            if cleaned.get(column) is not None and not _is_uuid(cleaned[column]):
                cleaned[column] = None
        return cleaned

    def _request(self, method: str, table: str, body: Any | None = None, query: str = '', *, upsert: bool = False) -> Any:
        data = None if body is None else json.dumps(body, default=lambda o: o.model_dump() if hasattr(o, 'model_dump') else o).encode()
        req = request.Request(f'{self.base_url}/{table}{query}', data=data, headers=self._headers(upsert=upsert), method=method)
        try:
            with request.urlopen(req, timeout=10) as resp:
                payload = resp.read().decode()
        except Exception as exc:
            raise RepositoryError(f'Supabase request failed for {table}: {exc}') from exc
        return json.loads(payload) if payload else None

    def list(self, table: str) -> list[Any]:
        return self._request('GET', table, query='?select=*') or []

    def put(self, table: str, key: str, value: Any) -> None:
        payload = _to_payload(value)
        payload['id'] = key
        payload = self._clean_payload(table, payload)
        self._request('POST', table, payload, query='?on_conflict=id', upsert=True)

    def append(self, table: str, value: Any) -> None:
        self._request('POST', table, self._clean_payload(table, _to_payload(value)))

    def delete(self, table: str, key: str) -> None:
        self._request('DELETE', table, query=f'?id=eq.{key}')
