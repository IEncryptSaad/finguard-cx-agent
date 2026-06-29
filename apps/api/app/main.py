from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.errors import error_middleware
from app.middleware.rate_limit import rate_limit_middleware
configure_logging(); settings = get_settings()
app = FastAPI(title="FinGuard CX Agent API", version="0.2.0", openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs")
app.middleware("http")(error_middleware)
app.middleware("http")(rate_limit_middleware(settings.rate_limit_per_minute, 60))
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(',')], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
