import hashlib
from abc import ABC, abstractmethod
from app.schemas.source import ResearchSource

class ResearchToolError(Exception):
    """Base exception for research tool errors."""
    pass

class ResearchToolConfigurationError(ResearchToolError):
    """Raised when a tool is missing required configuration (e.g., API keys)."""
    pass

class ResearchToolProviderError(ResearchToolError):
    """Raised when the external provider fails, times out, or returns invalid data."""
    pass

class ResearchToolValidationError(ResearchToolError):
    """Raised when input parameters to a research tool are invalid."""
    pass

class ResearchTool(ABC):
    """
    Abstract base class for all research tools (Web, Academic).
    Ensures a consistent interface returning normalized ResearchSource objects.
    """
    
    def validate_params(self, query: str, max_results: int):
        """Validates standard search parameters."""
        if not query or not str(query).strip():
            raise ResearchToolValidationError("Search query cannot be empty.")
        if not isinstance(max_results, int):
            raise ResearchToolValidationError("max_results must be an integer.")
        if max_results <= 0:
            raise ResearchToolValidationError("max_results must be greater than 0.")
        if max_results > 20:
            raise ResearchToolValidationError("max_results cannot exceed 20.")
            
    def generate_source_id(self, url: str) -> str:
        """
        Generates a deterministic, stable source ID based on the URL using SHA-256.
        Ensures the same URL always yields the same ID.
        """
        if not url or not str(url).strip():
            raise ResearchToolValidationError("URL cannot be empty for deterministic ID generation.")
        return f"src_{hashlib.sha256(url.encode('utf-8')).hexdigest()[:16]}"

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[ResearchSource]:
        """Executes a search and returns normalized ResearchSource objects."""
        pass