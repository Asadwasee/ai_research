import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from app.core.config import settings
from app.services.llm.base import LLMConfigurationError, LLMProviderError
from app.services.llm.gemini import GeminiLLMProvider

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "fake-test-key")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-3.8-flash")

def test_missing_api_key(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)
    with pytest.raises(LLMConfigurationError):
        GeminiLLMProvider()

def test_gemini_generate_text_mocked(mock_settings):
    with patch("app.services.llm.gemini.genai.Client") as MockClient:
        mock_client_instance = MockClient.return_value
        
        mock_response = MagicMock()
        mock_response.text = "Mocked Gemini Output"
        
        mock_generate_content = AsyncMock(return_value=mock_response)
        mock_client_instance.aio.models.generate_content = mock_generate_content
        
        provider = GeminiLLMProvider()
        
        result = asyncio.run(provider.generate_text("Test prompt"))
        
        assert result == "Mocked Gemini Output"
        mock_generate_content.assert_called_once_with(
            model="gemini-3.8-flash",
            contents="Test prompt"
        )

def test_gemini_provider_error_raised(mock_settings):
    with patch("app.services.llm.gemini.genai.Client") as MockClient:
        mock_client_instance = MockClient.return_value
        
        # Mock the API call to raise a generic internal exception
        mock_generate_content = AsyncMock(side_effect=Exception("Raw internal API error with sensitive data"))
        mock_client_instance.aio.models.generate_content = mock_generate_content
        
        provider = GeminiLLMProvider()
        
        with pytest.raises(LLMProviderError) as exc_info:
            asyncio.run(provider.generate_text("Test prompt"))
        
        error_msg = str(exc_info.value)
        assert "LLM generation failed due to a provider error." in error_msg
        assert "fake-test-key" not in error_msg
        assert "Raw internal API error" not in error_msg