import logging
import asyncio
from tavily import AsyncTavilyClient
from app.core.config import settings
from app.schemas.source import ResearchSource, SourceType
from app.tools.research.base import (
    ResearchTool, ResearchToolConfigurationError,
    ResearchToolProviderError
)

logger = logging.getLogger(__name__)

class TavilyWebSearchTool(ResearchTool):
    def __init__(self):
        if not settings.TAVILY_API_KEY:
            raise ResearchToolConfigurationError("TAVILY_API_KEY is not configured.")
        try:
            self.client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
        except Exception as e:
            logger.error("Failed to initialize Tavily client.")
            raise ResearchToolConfigurationError("Invalid Tavily configuration.") from e

    async def search(self, query: str, max_results: int = 5) -> list[ResearchSource]:
        self.validate_params(query, max_results)
            
        try:
            # Enforce strict timeout using asyncio.wait_for
            response = await asyncio.wait_for(
                self.client.search(
                    query=query,
                    max_results=max_results,
                    search_depth="advanced"
                ),
                timeout=settings.RESEARCH_TOOL_TIMEOUT
            )
            
            sources = []
            for item in response.get("results", []):
                url = item.get("url")
                if not url:
                    continue
                    
                title = item.get("title")
                if not title:
                    title = "Untitled Web Page"
                    
                # Tavily sometimes provides published_date
                published_at = item.get("published_date")
                
                source = ResearchSource(
                    source_id=self.generate_source_id(url),
                    title=title,
                    url=url,
                    source_type=SourceType.WEB,
                    publisher=None,
                    authors=[],
                    published_at=published_at,
                    content=item.get("content")  # ADDED: Preserving retrieved textual content
                )
                sources.append(source)
                
            return sources
            
        except asyncio.TimeoutError as e:
            logger.error("Tavily web search timed out.")
            raise ResearchToolProviderError("Web search provider timed out.") from e
        except Exception as e:
            logger.error(f"Tavily web search failed: {type(e).__name__}")
            raise ResearchToolProviderError(f"Web search provider failed: {type(e).__name__}") from e