import pytest
import asyncio
from app.workflow.state import ResearchState
from app.schemas.research import ResearchMode, ResearchPlan
from app.workflow.nodes.researcher import run_researcher
from app.schemas.source import ResearchSource, SourceType
from app.tools.research.base import ResearchTool, ResearchToolProviderError

class MockWebTool(ResearchTool):
    async def search(self, query: str, max_results: int = 5):
        return [ResearchSource(
            source_id=f"web_{query}", 
            title=f"Web: {query}", 
            url="http://web", 
            source_type=SourceType.WEB, 
            publisher=None, 
            authors=[], 
            published_at=None
        )]

class MockAcademicTool(ResearchTool):
    async def search(self, query: str, max_results: int = 5):
        return [ResearchSource(
            source_id=f"acad_{query}", 
            title=f"Acad: {query}", 
            url="http://acad", 
            source_type=SourceType.ACADEMIC, 
            publisher="arXiv", 
            authors=[], 
            published_at=None
        )]

class ErrorTool(ResearchTool):
    async def search(self, query: str, max_results: int = 5):
        raise ResearchToolProviderError("Mocked failure")

def get_test_state(mode: ResearchMode, plan_questions: list[str]) -> ResearchState:
    # Proper generation of test data via actual Pydantic schema validation
    plan_data = {
        "original_query": "test query",
        "sub_questions": [
            {"id": str(i), "question": q, "purpose": "test"}
            for i, q in enumerate(plan_questions)
        ],
        "mode": mode.value
    }
    plan = ResearchPlan.model_validate(plan_data)
    
    return {
        "query": "test query",
        "mode": mode,
        "plan": plan,
        "error": None,
        "sources": [],
        "errors": []
    }

def test_researcher_standard_mode():
    state = get_test_state(ResearchMode.STANDARD, ["Q1"])
    result = asyncio.run(run_researcher(state, MockWebTool(), MockAcademicTool()))
    
    assert len(result["sources"]) == 1
    assert result["sources"][0].source_type == SourceType.WEB
    assert len(result["errors"]) == 0

def test_researcher_deep_mode():
    state = get_test_state(ResearchMode.DEEP, ["Q1"])
    result = asyncio.run(run_researcher(state, MockWebTool(), MockAcademicTool()))
    
    assert len(result["sources"]) == 2
    assert len(result["errors"]) == 0

def test_researcher_tool_failure():
    state = get_test_state(ResearchMode.STANDARD, ["Q1"])
    result = asyncio.run(run_researcher(state, ErrorTool(), MockAcademicTool()))
    
    assert len(result.get("sources", [])) == 0
    assert len(result["errors"]) == 1
    assert "Mocked failure" in result["errors"][0].details

def test_researcher_no_plan():
    state = {
        "query": "test query",
        "mode": ResearchMode.STANDARD,
        "plan": None,
        "error": None,
        "sources": [],
        "errors": []
    }
    result = asyncio.run(run_researcher(state, MockWebTool(), MockAcademicTool()))
    
    assert len(result.get("sources", [])) == 0
    assert len(result["errors"]) == 1
    assert "No research plan found" in result["errors"][0].message