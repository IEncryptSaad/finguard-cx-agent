from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_env: str = "local"
    llm_provider: str = "mock"
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    cors_origins: str = "http://localhost:3000"
    rate_limit_per_minute: int = 60
    auth_required: bool = False
    public_customer_chat: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
@lru_cache
def get_settings() -> Settings:
    return Settings()
