from fastapi import Request
from fastapi.responses import JSONResponse
async def error_middleware(request: Request, call_next):
    try: return await call_next(request)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"code":"internal_error","message":"Unexpected server error","details":{"type":exc.__class__.__name__}})
