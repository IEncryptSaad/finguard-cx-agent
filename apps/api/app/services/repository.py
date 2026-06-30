from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, Iterable
from app.core.config import get_settings

class RepositoryError(RuntimeError): pass

class AppRepository:
    def list(self, table: str) -> list[Any]: raise NotImplementedError
    def put(self, table: str, key: str, value: Any) -> None: raise NotImplementedError
    def append(self, table: str, value: Any) -> None: raise NotImplementedError
    def delete(self, table: str, key: str) -> None: raise NotImplementedError

class JsonRepository(AppRepository):
    backend = 'json'
    def __init__(self, path: str | None = None):
        self.path = Path(path or os.getenv('FINGUARD_DATA_FILE', '.finguard-data.json'))
        self.data: dict[str, Any] = {}
        if self.path.exists():
            self.data = json.loads(self.path.read_text() or '{}')
    def _save(self):
        self.path.write_text(json.dumps(self.data, default=lambda o: o.model_dump() if hasattr(o,'model_dump') else o, indent=2, sort_keys=True))
    def list(self, table: str) -> list[Any]: return list(self.data.get(table, {}).values()) if isinstance(self.data.get(table, {}), dict) else list(self.data.get(table, []))
    def put(self, table: str, key: str, value: Any) -> None:
        self.data.setdefault(table, {})[key] = value; self._save()
    def append(self, table: str, value: Any) -> None:
        self.data.setdefault(table, []).append(value); self._save()
    def delete(self, table: str, key: str) -> None:
        self.data.setdefault(table, {}).pop(key, None); self._save()

class InMemoryRepository(JsonRepository):
    backend = 'memory'
    def __init__(self): self.data = {}
    def _save(self): pass

_REPO: AppRepository | None = None

def get_repository() -> AppRepository:
    global _REPO
    if _REPO is None:
        s = get_settings()
        if s.app_env == 'production' and not (s.supabase_url and s.supabase_service_role_key):
            raise RepositoryError('Production persistence requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY')
        if s.supabase_url and s.supabase_service_role_key:
            from app.db.supabase import SupabaseRepository
            _REPO = SupabaseRepository(s)
        elif os.getenv('FINGUARD_REPOSITORY','json') == 'memory':
            _REPO = InMemoryRepository()
        else:
            _REPO = JsonRepository()
    return _REPO

def active_backend() -> str:
    return getattr(get_repository(), 'backend', get_repository().__class__.__name__.lower())


def paginate(items: Iterable[Any], page:int=1, page_size:int=50, sort:str|None=None, order:str='desc') -> dict[str, Any]:
    data=list(items); page=max(1,page); page_size=min(max(1,page_size),100)
    if sort:
        data=sorted(data, key=lambda x: getattr(x, sort, '') if not isinstance(x,dict) else x.get(sort,''), reverse=order!='asc')
    total=len(data); start=(page-1)*page_size
    return {'items': data[start:start+page_size], 'page': page, 'page_size': page_size, 'total': total}
