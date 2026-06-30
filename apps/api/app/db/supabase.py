from __future__ import annotations

import json
from typing import Any
from urllib import request

from app.core.config import Settings
from app.services.repository import AppRepository, RepositoryError


class SupabaseRepository(AppRepository):
    """Repository backed by Supabase PostgREST using the service role key."""

    backend = 'supabase'

    def __init__(self, settings: Settings):
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise RepositoryError('SupabaseRepository requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY')
        self.base_url = settings.supabase_url.rstrip('/') + '/rest/v1'
        self.service_role_key = settings.supabase_service_role_key

    def _headers(self) -> dict[str, str]:
        return {
            'apikey': self.service_role_key,
            'Authorization': f'Bearer {self.service_role_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal,resolution=merge-duplicates',
        }

    def _request(self, method: str, table: str, body: Any | None = None, query: str = '') -> Any:
        data = None if body is None else json.dumps(body, default=lambda o: o.model_dump() if hasattr(o, 'model_dump') else o).encode()
        req = request.Request(f'{self.base_url}/{table}{query}', data=data, headers=self._headers(), method=method)
        try:
            with request.urlopen(req, timeout=10) as resp:
                payload = resp.read().decode()
        except Exception as exc:
            raise RepositoryError(f'Supabase request failed for {table}: {exc}') from exc
        return json.loads(payload) if payload else None

    def list(self, table: str) -> list[Any]:
        return self._request('GET', table, query='?select=*') or []

    def put(self, table: str, key: str, value: Any) -> None:
        payload = value.model_dump() if hasattr(value, 'model_dump') else dict(value)
        payload['id'] = key
        self._request('POST', table, payload, query='?on_conflict=id')

    def append(self, table: str, value: Any) -> None:
        self._request('POST', table, value.model_dump() if hasattr(value, 'model_dump') else value)

    def delete(self, table: str, key: str) -> None:
        self._request('DELETE', table, query=f'?id=eq.{key}')
