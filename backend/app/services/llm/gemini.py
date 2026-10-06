import logging
from google import genai
from app.core.config import settings
from app.services.llm.base import LLMProvider, LLMConfigurationError, LLMProviderError

logger = logging.getLogger(__name__)

class GeminiLLMProvider(LLMProvider):
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise LLMConfigurationError("GEMINI_API_KEY is missing from configuration.")
        
        self.model_name = settings.GEMINI_MODEL
        try:
            # Initialize the modern google-genai client
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Client: {type(e).__name__} - {str(e)}")
            raise LLMConfigurationError("Gemini client initialization failed. Check credentials.") from e

    async def generate_text(self, prompt: str) -> str:
        try:
            # Using the official async API mechanism
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            # Improved debugging: Log the exact error type and message safely
            # SDK exceptions do not contain the API key in the string representation
            logger.error(f"Gemini API Error [Model: {self.model_name}]: {type(e).__name__} - {str(e)}")
            
            # Wrapping exception to prevent exposing internal API details/keys to frontend/users
            raise LLMProviderError("LLM generation failed due to a provider error.") from e

def get_llm_provider() -> LLMProvider:
    """Dependency injection provider for the LLM service."""
    return GeminiLLMProvider()