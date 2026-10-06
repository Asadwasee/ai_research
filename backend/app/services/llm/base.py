from abc import ABC, abstractmethod

class LLMConfigurationError(Exception):
    """Raised when the LLM provider is misconfigured (e.g., missing API keys)."""
    pass

class LLMProviderError(Exception):
    """Raised when the LLM provider fails to generate text or communicate with the API."""
    pass

class LLMProvider(ABC):
    """
    Abstract interface for LLM providers.
    Ensures the application is agnostic to specific models/SDKs (Gemini, OpenAI, etc.).
    """
    
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """
        Takes a prompt and returns the generated text asynchronously.
        """
        pass