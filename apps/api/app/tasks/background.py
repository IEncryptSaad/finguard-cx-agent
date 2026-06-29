from collections import deque
from dataclasses import dataclass
from typing import Callable, Awaitable, Any
@dataclass
class BackgroundTaskRecord:
    name: str
    status: str = "queued"
_TASKS: deque[BackgroundTaskRecord] = deque()
def enqueue(name: str) -> BackgroundTaskRecord:
    record = BackgroundTaskRecord(name=name); _TASKS.append(record); return record
def list_tasks() -> list[BackgroundTaskRecord]: return list(_TASKS)
