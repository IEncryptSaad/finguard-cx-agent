from abc import ABC, abstractmethod
class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str) -> str: ...
class MockLLMProvider(LLMProvider):
    async def complete(self, prompt: str) -> str:
        return "I can help with that. I have noted the details securely and will guide you through the next support step."
def provider_from_name(name: str) -> LLMProvider:
    if name != "mock":
        raise ValueError(f"Provider '{name}' is not configured. Use mock mode or add an adapter.")
    return MockLLMProvider()
