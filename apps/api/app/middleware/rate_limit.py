import time
from collections import defaultdict, deque
from fastapi import Request
from fastapi.responses import JSONResponse
_BUCKETS: dict[str, deque[float]] = defaultdict(deque)
def rate_limit_middleware(limit: int, window_seconds: int):
    async def middleware(request: Request, call_next):
        key = request.client.host if request.client else "unknown"; now=time.time(); bucket=_BUCKETS[key]
        while bucket and now-bucket[0] > window_seconds: bucket.popleft()
        if len(bucket) >= limit: return JSONResponse(status_code=429, content={"code":"rate_limited","message":"Too many requests"})
        bucket.append(now); return await call_next(request)
    return middleware
