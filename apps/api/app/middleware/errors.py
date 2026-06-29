from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def error_response(code: str, message: str, details: dict | None = None) -> dict:
    return {"code": code, "message": message, "details": details or {}}


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response("validation_error", "Request validation failed", {"errors": exc.errors()}),
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, dict) else {"reason": str(exc.detail)}
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response("http_error", str(detail.get("reason", "Request failed")), detail),
    )


async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as exc:
        return await http_exception_handler(request, exc)
    except Exception as exc:
        if exc.__class__.__name__ == "ExceptionGroup":
            for nested in getattr(exc, "exceptions", []):
                if isinstance(nested, HTTPException):
                    return await http_exception_handler(request, nested)
        return JSONResponse(
            status_code=500,
            content=error_response(
                "internal_error",
                "Unexpected server error",
                {"type": exc.__class__.__name__},
            ),
        )
