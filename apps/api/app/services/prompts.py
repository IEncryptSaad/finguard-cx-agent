DEFAULT_SYSTEM_PROMPT = "You are FinGuard, a careful financial services customer support assistant. Be concise, compliant, and avoid requesting sensitive PII."
class PromptTemplateManager:
    def __init__(self): self._templates = {"system": DEFAULT_SYSTEM_PROMPT, "chat": "{message}"}
    def get(self, name: str) -> str: return self._templates[name]
    def render(self, name: str, **values: str) -> str: return self.get(name).format(**values)
    def upsert(self, name: str, template: str) -> None: self._templates[name] = template
prompt_manager = PromptTemplateManager()
