import asyncio
from app.workflow.graph import build_research_graph
from app.workflow.state import ResearchState
from app.schemas.research import ResearchMode
from app.schemas.workflow import WorkflowStatus
from app.services.llm.base import LLMProvider
from app.tools.research.base import ResearchTool

class MockWorkflowLLM(LLMProvider):
    async def generate_text(self, prompt: str) -> str:
        return """{
            "original_query": "Graph Test",
            "sub_questions": [{"id": "q1", "question": "Test", "purpose": "Test"}],
            "mode": "quick"
        }"""

class DummyTool(ResearchTool):
    async def search(self, query: str, max_results: int = 5):
        return []

def test_full_workflow_execution():
    llm_provider = MockWorkflowLLM()
    web_tool = DummyTool()
    acad_tool = DummyTool()
    
    graph = build_research_graph(llm_provider, web_tool, acad_tool)
    
    initial_state: ResearchState = {
        "query": "Graph Test",
        "mode": ResearchMode.QUICK,
        "plan": None,
        "error": None,
        "status": WorkflowStatus.INITIALIZED,
        "sources": [],
        "findings": [],
        "errors": []
    }
    
    final_state = asyncio.run(graph.ainvoke(initial_state))
    
    assert final_state["query"] == "Graph Test"
    assert final_state["mode"] == ResearchMode.QUICK
    assert final_state["plan"] is not None
    assert len(final_state["plan"].sub_questions) == 1
    assert final_state["error"] is None