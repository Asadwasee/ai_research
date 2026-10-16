import logging
import httpx
import xml.etree.ElementTree as ET
from app.core.config import settings
from app.schemas.source import ResearchSource, SourceType
from app.tools.research.base import ResearchTool, ResearchToolProviderError

logger = logging.getLogger(__name__)

class ArxivAcademicSearchTool(ResearchTool):
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.timeout = settings.RESEARCH_TOOL_TIMEOUT

    async def search(self, query: str, max_results: int = 5) -> list[ResearchSource]:
        self.validate_params(query, max_results)
            
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
            return self._parse_arxiv_xml(response.text)
            
        except httpx.TimeoutException as e:
            logger.error("ArXiv API request timed out.")
            raise ResearchToolProviderError("Academic search timed out.") from e
        except httpx.RequestError as e:
            logger.error(f"ArXiv network error: {type(e).__name__}")
            raise ResearchToolProviderError("Academic search network error.") from e
        except httpx.HTTPStatusError as e:
            logger.error(f"ArXiv HTTP error: {e.response.status_code}")
            raise ResearchToolProviderError(f"Academic search returned HTTP error.") from e
        except ResearchToolProviderError:
            # FIX: Explicitly re-raise to prevent double-wrapping of domain errors (like Malformed XML)
            raise
        except Exception as e:
            logger.error(f"ArXiv academic search failed: {type(e).__name__}")
            raise ResearchToolProviderError(f"Academic search provider failed: {type(e).__name__}") from e

    def _parse_arxiv_xml(self, xml_data: str) -> list[ResearchSource]:
        sources = []
        try:
            root = ET.fromstring(xml_data)
            namespaces = {'atom': 'http://www.w3.org/2005/Atom'}
            
            for entry in root.findall('atom:entry', namespaces):
                id_elem = entry.find('atom:id', namespaces)
                if id_elem is None or not id_elem.text:
                    continue
                url = id_elem.text.strip()
                
                title_elem = entry.find('atom:title', namespaces)
                title = title_elem.text.replace('\n', ' ').strip() if title_elem is not None and title_elem.text else "Untitled Paper"
                
                published_elem = entry.find('atom:published', namespaces)
                published = published_elem.text.strip() if published_elem is not None and published_elem.text else None

                summary_elem = entry.find('atom:summary', namespaces)
                content = summary_elem.text.replace('\n', ' ').strip() if summary_elem is not None and summary_elem.text else None
                
                authors = []
                for author in entry.findall('atom:author', namespaces):
                    name_elem = author.find('atom:name', namespaces)
                    if name_elem is not None and name_elem.text:
                        authors.append(name_elem.text.strip())
                
                source = ResearchSource(
                    source_id=self.generate_source_id(url),
                    title=title,
                    url=url,
                    source_type=SourceType.ACADEMIC,
                    publisher="arXiv",
                    authors=authors,
                    published_at=published,
                    content=content  # ADDED
                )
                sources.append(source)
                
            return sources
        except ET.ParseError as e:
            logger.error("Failed to parse ArXiv XML response.")
            raise ResearchToolProviderError("Failed to parse academic search results (Malformed XML).") from e
        except Exception as e:
            logger.error(f"Unexpected parsing error: {e}")
            raise ResearchToolProviderError("Unexpected error during parsing.") from e