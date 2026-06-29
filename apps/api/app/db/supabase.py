from app.core.config import Settings
class SupabaseRepository:
    """Supabase-ready repository boundary; uses in-memory services until credentials are configured."""
    def __init__(self, settings: Settings):
        self.settings = settings
    @property
    def enabled(self) -> bool:
        return bool(self.settings.supabase_url and self.settings.supabase_service_role_key)
