from fastapi import HTTPException, Request, status
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def error_response(code: str, message: str, details: dict | None = None) -> dict:
    return {"code": code, "message": message, "details": details or {}}


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(error_response("validation_error", "Request validation failed", {"errors": exc.errors()})),
    )


async def http_exception_handler(request: Request, exc: HTTPException | StarletteHTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {"reason": str(exc.detail)}
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response("http_error", str(detail.get("reason", "Request failed")), detail),
        headers=getattr(exc, "headers", None),
    )


async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except (HTTPException, StarletteHTTPException) as exc:
        return await http_exception_handler(request, exc)
    except Exception as exc:
        if exc.__class__.__name__ == "ExceptionGroup":
            for nested in getattr(exc, "exceptions", []):
                if isinstance(nested, (HTTPException, StarletteHTTPException)):
                    return await http_exception_handler(request, nested)
        return JSONResponse(
            status_code=500,
            content=error_response(
                "internal_error",
                "Unexpected server error",
                {"type": exc.__class__.__name__},
            ),
        )
