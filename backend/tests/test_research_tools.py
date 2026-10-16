import asyncio
import httpx
import pytest

from unittest.mock import patch, AsyncMock

from app.core.config import settings
from app.schemas.source import SourceType
from app.tools.research.base import (
    ResearchTool,
    ResearchToolConfigurationError,
    ResearchToolProviderError,
    ResearchToolValidationError,
)
from app.tools.research.web_search import TavilyWebSearchTool
from app.tools.research.academic_search import ArxivAcademicSearchTool


class DummyTool(ResearchTool):
    async def search(self, query: str, max_results: int = 5):
        self.validate_params(query, max_results)
        return []


@pytest.fixture
def mock_tavily_settings(monkeypatch):
    monkeypatch.setattr(settings, "TAVILY_API_KEY", "fake-tavily-key")
    monkeypatch.setattr(settings, "TAVILY_MAX_RESULTS", 5)


# ============================================================
# BASE VALIDATION TESTS
# ============================================================

def test_validation_empty_query():
    tool = DummyTool()

    with pytest.raises(ResearchToolValidationError) as exc:
        asyncio.run(tool.search("   ", 5))

    assert "cannot be empty" in str(exc.value)


def test_validation_max_results_zero():
    tool = DummyTool()

    with pytest.raises(ResearchToolValidationError):
        asyncio.run(tool.search("Test", 0))


def test_validation_max_results_negative():
    tool = DummyTool()

    with pytest.raises(ResearchToolValidationError):
        asyncio.run(tool.search("Test", -5))


def test_validation_max_results_exceeds():
    tool = DummyTool()

    with pytest.raises(ResearchToolValidationError):
        asyncio.run(tool.search("Test", 25))


def test_validation_valid():
    tool = DummyTool()

    assert asyncio.run(tool.search("Test", 5)) == []


def test_generate_source_id_deterministic():
    tool = DummyTool()

    id1 = tool.generate_source_id("https://example.com")
    id2 = tool.generate_source_id("https://example.com")
    id3 = tool.generate_source_id("https://example.com/other")

    assert id1 == id2
    assert id1 != id3
    assert id1.startswith("src_")


# ============================================================
# TAVILY TESTS
# ============================================================

def test_tavily_missing_api_key(monkeypatch):
    monkeypatch.setattr(settings, "TAVILY_API_KEY", None)

    with pytest.raises(ResearchToolConfigurationError):
        TavilyWebSearchTool()


def test_tavily_success(mock_tavily_settings):
    with patch(
        "app.tools.research.web_search.AsyncTavilyClient"
    ) as MockClient:

        mock_instance = MockClient.return_value

        mock_instance.search = AsyncMock(
            return_value={
                "results": [
                    {
                        "title": "Test Web",
                        "url": "https://example.com",
                        "published_date": "2024-01-01T00:00:00Z",
                        "content": "Useful web snippet.",
                    }
                ]
            }
        )

        tool = TavilyWebSearchTool()

        results = asyncio.run(
            tool.search("AI", 1)
        )

        assert len(results) == 1
        assert results[0].source_type == SourceType.WEB
        assert results[0].title == "Test Web"
        assert str(results[0].url) == "https://example.com/"
        assert results[0].content == "Useful web snippet."


def test_tavily_malformed_results(mock_tavily_settings):
    with patch(
        "app.tools.research.web_search.AsyncTavilyClient"
    ) as MockClient:

        mock_instance = MockClient.return_value

        mock_instance.search = AsyncMock(
            return_value={
                "results": [
                    {
                        "title": "No URL"
                    }
                ]
            }
        )

        tool = TavilyWebSearchTool()

        results = asyncio.run(
            tool.search("Test", 5)
        )

        assert len(results) == 0


def test_tavily_timeout(mock_tavily_settings):
    with patch(
        "app.tools.research.web_search.AsyncTavilyClient"
    ) as MockClient:

        mock_instance = MockClient.return_value

        mock_instance.search = AsyncMock(
            side_effect=asyncio.TimeoutError("Timeout")
        )

        tool = TavilyWebSearchTool()

        with pytest.raises(ResearchToolProviderError) as exc:
            asyncio.run(
                tool.search("Test", 5)
            )

        assert "timed out" in str(exc.value)


def test_tavily_provider_error(mock_tavily_settings):
    with patch(
        "app.tools.research.web_search.AsyncTavilyClient"
    ) as MockClient:

        mock_instance = MockClient.return_value

        mock_instance.search = AsyncMock(
            side_effect=Exception("API Crash")
        )

        tool = TavilyWebSearchTool()

        with pytest.raises(ResearchToolProviderError):
            asyncio.run(
                tool.search("Test", 5)
            )


# ============================================================
# ARXIV HELPERS
# ============================================================

def make_arxiv_xml(
    arxiv_id: str,
    title: str,
    published: str | None = None,
    author: str | None = None,
    summary: str | None = None,
) -> str:
    """
    Build valid Atom XML without writing literal angle brackets.

    This avoids copy/paste/rendering issues where <feed>, <entry>,
    <id>, etc. can accidentally disappear.
    """

    lt = chr(60)
    gt = chr(62)

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'{lt}feed xmlns="http://www.w3.org/2005/Atom"{gt}'
        f'{lt}entry{gt}'
        f'{lt}id{gt}{arxiv_id}{lt}/id{gt}'
        f'{lt}title{gt}{title}{lt}/title{gt}'
    )

    if summary is not None:
        xml += (
            f'{lt}summary{gt}'
            f'{summary}'
            f'{lt}/summary{gt}'
        )

    if published is not None:
        xml += (
            f'{lt}published{gt}'
            f'{published}'
            f'{lt}/published{gt}'
        )

    if author is not None:
        xml += (
            f'{lt}author{gt}'
            f'{lt}name{gt}'
            f'{author}'
            f'{lt}/name{gt}'
            f'{lt}/author{gt}'
        )

    xml += (
        f'{lt}/entry{gt}'
        f'{lt}/feed{gt}'
    )

    return xml


# ============================================================
# ARXIV TESTS
# ============================================================

def test_arxiv_success():
    valid_xml = make_arxiv_xml(
        arxiv_id="http://arxiv.org/abs/2401.00001",
        title="Attention Is All You Need",
        published="2024-01-01T00:00:00Z",
        author="Ashish Vaswani",
        summary="This is the paper abstract.",
    )

    with patch(
        "app.tools.research.academic_search.httpx.AsyncClient"
    ) as MockClient:

        mock_client_instance = (
            MockClient.return_value.__aenter__.return_value
        )

        mock_response = AsyncMock()
        mock_response.text = valid_xml
        mock_response.raise_for_status = lambda: None

        mock_client_instance.get = AsyncMock(
            return_value=mock_response
        )

        tool = ArxivAcademicSearchTool()

        results = asyncio.run(
            tool.search("Transformers", 1)
        )

        assert len(results) == 1
        assert results[0].source_type == SourceType.ACADEMIC
        assert results[0].title == "Attention Is All You Need"
        assert len(results[0].authors) == 1
        assert "Ashish Vaswani" in results[0].authors
        assert results[0].publisher == "arXiv"
        assert str(results[0].url) == (
            "http://arxiv.org/abs/2401.00001"
        )
        assert results[0].published_at is not None
        assert results[0].source_id != ""
        assert results[0].content == "This is the paper abstract."


def test_arxiv_missing_fields_handled():
    missing_fields_xml = make_arxiv_xml(
        arxiv_id="http://arxiv.org/abs/test-missing",
        title="Missing Optional Fields Paper",
    )

    with patch(
        "app.tools.research.academic_search.httpx.AsyncClient"
    ) as MockClient:

        mock_client_instance = (
            MockClient.return_value.__aenter__.return_value
        )

        mock_response = AsyncMock()
        mock_response.text = missing_fields_xml
        mock_response.raise_for_status = lambda: None

        mock_client_instance.get = AsyncMock(
            return_value=mock_response
        )

        tool = ArxivAcademicSearchTool()

        results = asyncio.run(
            tool.search("Test", 1)
        )

        assert len(results) == 1
        assert str(results[0].url) == (
            "http://arxiv.org/abs/test-missing"
        )
        assert results[0].title == (
            "Missing Optional Fields Paper"
        )
        assert results[0].authors == []
        assert results[0].published_at is None
        assert results[0].publisher == "arXiv"
        assert results[0].source_type == SourceType.ACADEMIC
        assert results[0].content is None


def test_arxiv_malformed_xml():
    with patch(
        "app.tools.research.academic_search.httpx.AsyncClient"
    ) as MockClient:

        mock_client_instance = (
            MockClient.return_value.__aenter__.return_value
        )

        mock_response = AsyncMock()
        mock_response.text = "unclosed"
        mock_response.raise_for_status = lambda: None

        mock_client_instance.get = AsyncMock(
            return_value=mock_response
        )

        tool = ArxivAcademicSearchTool()

        with pytest.raises(ResearchToolProviderError) as exc:
            asyncio.run(
                tool.search("Test", 1)
            )

        assert "Malformed XML" in str(exc.value)


def test_arxiv_timeout():
    with patch(
        "app.tools.research.academic_search.httpx.AsyncClient"
    ) as MockClient:

        mock_client_instance = (
            MockClient.return_value.__aenter__.return_value
        )

        mock_request = httpx.Request(
            "GET",
            "http://export.arxiv.org/api/query",
        )

        mock_client_instance.get = AsyncMock(
            side_effect=httpx.TimeoutException(
                "Timeout",
                request=mock_request,
            )
        )

        tool = ArxivAcademicSearchTool()

        with pytest.raises(ResearchToolProviderError) as exc:
            asyncio.run(
                tool.search("Test", 1)
            )

        assert "Academic search timed out" in str(
            exc.value
        )


def test_arxiv_http_error():
    with patch(
        "app.tools.research.academic_search.httpx.AsyncClient"
    ) as MockClient:

        mock_client_instance = (
            MockClient.return_value.__aenter__.return_value
        )

        mock_request = httpx.Request(
            "GET",
            "http://export.arxiv.org/api/query",
        )

        mock_client_instance.get = AsyncMock(
            side_effect=httpx.RequestError(
                "Network dropped",
                request=mock_request,
            )
        )

        tool = ArxivAcademicSearchTool()

        with pytest.raises(ResearchToolProviderError) as exc:
            asyncio.run(
                tool.search("Test", 1)
            )

        assert "Academic search network error" in str(
            exc.value
        )