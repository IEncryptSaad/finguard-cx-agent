from app.core.config import get_settings
from app.models.schemas import AppSettings
from app.services.prompts import prompt_manager

_SETTINGS: AppSettings | None = None

def get_app_settings() -> AppSettings:
    global _SETTINGS
    if _SETTINGS is None:
        env = get_settings()
        _SETTINGS = AppSettings(active_ai_provider=env.llm_provider, rate_limit_per_minute=env.rate_limit_per_minute)
    return _SETTINGS

def update_app_settings(payload: AppSettings) -> AppSettings:
    global _SETTINGS
    _SETTINGS = payload
    prompt_manager.upsert("system", payload.system_prompt)
    return _SETTINGS
