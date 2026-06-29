from fastapi import FastAPI, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.errors import error_middleware, http_exception_handler, validation_exception_handler
from app.middleware.rate_limit import rate_limit_middleware
from app.middleware.security_headers import security_headers_middleware
from app.services.repository import get_repository
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
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(',')], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
