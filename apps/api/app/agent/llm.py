import os
from app.plugins.base import AIProvider, PluginMetadata

class ProviderConfigurationError(RuntimeError): pass

class LLMProvider(AIProvider): pass

class MockLLMProvider(LLMProvider):
    metadata = PluginMetadata(name="mock", enabled=True, description="Deterministic free mock provider")
    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str:
        return "I can help with that. I have noted the details securely and will guide you through the next support step."

class DisabledHTTPProvider(LLMProvider):
    def __init__(self, name: str, env_key: str, endpoint_env: str | None = None):
        self.metadata = PluginMetadata(name=name, enabled=bool(os.getenv(env_key)), description=f"{name} adapter plugin")
        self.env_key = env_key; self.endpoint_env = endpoint_env
    async def complete(self, prompt: str, *, system_prompt: str | None = None) -> str:
        if not os.getenv(self.env_key):
            raise ProviderConfigurationError(f"{self.metadata.name} provider is disabled. Set {self.env_key} to enable it.")
        # Production boundary: real HTTP clients can be installed by plugin packages without changing orchestrator code.
        return f"{self.metadata.name} provider is configured but no transport plugin is installed."

PROVIDER_FACTORIES = {
    "mock": lambda: MockLLMProvider(),
    "openai": lambda: DisabledHTTPProvider("openai", "OPENAI_API_KEY"),
    "anthropic": lambda: DisabledHTTPProvider("anthropic", "ANTHROPIC_API_KEY"),
    "gemini": lambda: DisabledHTTPProvider("gemini", "GEMINI_API_KEY"),
    "groq": lambda: DisabledHTTPProvider("groq", "GROQ_API_KEY"),
    "ollama": lambda: DisabledHTTPProvider("ollama", "OLLAMA_BASE_URL", "OLLAMA_BASE_URL"),
    "openrouter": lambda: DisabledHTTPProvider("openrouter", "OPENROUTER_API_KEY"),
}

def provider_from_name(name: str) -> LLMProvider:
    key = (name or "mock").lower()
    if key not in PROVIDER_FACTORIES:
        raise ValueError(f"Unknown provider '{name}'. Available: {', '.join(PROVIDER_FACTORIES)}")
    provider = PROVIDER_FACTORIES[key]()
    if key != "mock" and not provider.metadata.enabled:
        raise ProviderConfigurationError(f"Provider '{key}' is installed but disabled; configure its environment variables.")
    return provider
