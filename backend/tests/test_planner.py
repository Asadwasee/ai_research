import pytest
import asyncio
from app.schemas.research import ResearchMode
from app.workflow.state import ResearchState
from app.workflow.nodes.planner import run_planner, PlannerError
from app.services.llm.base import LLMProvider, LLMProviderError

class MockSuccessLLM(LLMProvider):
    def __init__(self, response_text: str):
        self.response_text = response_text
    
    async def generate_text(self, prompt: str) -> str:
        return self.response_text

class MockFailLLM(LLMProvider):
    async def generate_text(self, prompt: str) -> str:
        raise LLMProviderError("Mocked LLM failure")

def get_initial_state() -> ResearchState:
    return {"query": "What is RAG?", "mode": ResearchMode.STANDARD, "plan": None, "error": None}

def test_planner_valid_json():
    valid_json = """{
        "original_query": "What is RAG?",
        "sub_questions": [{"id": "q1", "question": "Define RAG", "purpose": "Intro"}],
        "mode": "standard"
    }"""
    llm = MockSuccessLLM(valid_json)
    state = get_initial_state()
    
    result = asyncio.run(run_planner(state, llm))
    assert result["plan"] is not None
    assert len(result["plan"].sub_questions) == 1
    assert result["error"] is None

def test_planner_markdown_fenced_json():
    fenced_json = """```json\n{
        "original_query": "What is RAG?",
        "sub_questions": [{"id": "q1", "question": "Define RAG", "purpose": "Intro"}],
        "mode": "standard"
    }\n```"""
    llm = MockSuccessLLM(fenced_json)
    
    result = asyncio.run(run_planner(get_initial_state(), llm))
    assert result["plan"] is not None
    assert result["plan"].sub_questions[0].id == "q1"

def test_planner_invalid_json():
    bad_json = "{ invalid json..."
    llm = MockSuccessLLM(bad_json)
    
    with pytest.raises(PlannerError) as exc_info:
        asyncio.run(run_planner(get_initial_state(), llm))
    assert "Failed to parse LLM response as JSON" in str(exc_info.value)

def test_planner_invalid_schema():
    bad_schema_json = """{"original_query": "What is RAG?", "mode": "standard"}""" # Missing sub_questions
    llm = MockSuccessLLM(bad_schema_json)
    
    with pytest.raises(PlannerError) as exc_info:
        asyncio.run(run_planner(get_initial_state(), llm))
    assert "Failed to validate ResearchPlan schema" in str(exc_info.value)

def test_planner_llm_error():
    llm = MockFailLLM()
    
    with pytest.raises(PlannerError) as exc_info:
        asyncio.run(run_planner(get_initial_state(), llm))
    assert "LLM Provider failed during planning" in str(exc_info.value)