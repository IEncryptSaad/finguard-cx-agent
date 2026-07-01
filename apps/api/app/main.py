from fastapi import FastAPI, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from app.middleware.cors import LoggingCORSMiddleware
from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.errors import error_middleware, http_exception_handler, validation_exception_handler
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.security_headers import security_headers_middleware
from app.services.repository import get_repository

CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]
LOCALHOST_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


def parse_cors_origins(cors_origins: str, app_env: str) -> list[str]:
    origins = [origin.strip().rstrip("/") for origin in cors_origins.split(",") if origin.strip()]
    if app_env != "production":
        origins.extend(LOCALHOST_ORIGINS)
    return list(dict.fromkeys(origins))


configure_logging(); settings = get_settings()
if settings.app_env == "production" and ("*" in settings.cors_origins or not settings.cors_origins.strip()):
    raise RuntimeError("Production CORS must be an explicit allow-list")
get_repository()
app = FastAPI(title="FinGuard CX Agent API", version="1.0.0-rc1", openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs")
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.middleware("http")(error_middleware)
app.middleware("http")(security_headers_middleware)
app.middleware("http")(rate_limit_middleware(settings.rate_limit_per_minute, 60))
app.add_middleware(
    LoggingCORSMiddleware,
    allow_origins=parse_cors_origins(settings.cors_origins, settings.app_env),
    allow_credentials=True,
    allow_methods=CORS_METHODS,
    allow_headers=CORS_HEADERS,
)
app.include_router(router)
