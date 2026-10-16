import pytest
import asyncio
import json

from app.workflow.graph import build_research_graph
from app.schemas.research import ResearchMode
from app.schemas.source import ResearchSource, SourceType
from app.services.llm.base import LLMProvider
from app.tools.research.base import ResearchTool


# ==========================================
# MOCKS
# ==========================================

class MockSequenceLLM(LLMProvider):
    """Mocks LLM responses sequentially to simulate multi-step workflows like Planner -> Writer(Fail) -> Writer(Success)."""
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.call_count = 0
        self.prompts = []

    async def generate_text(self, prompt: str) -> str:
        self.prompts.append(prompt)
        idx = min(self.call_count, len(self.responses) - 1)
        self.call_count += 1
        return self.responses[idx]

class MockDummyTool(ResearchTool):
    """Mocks a research tool returning grounded content."""
    async def search(self, query: str, max_results: int = 5) -> list[ResearchSource]:
        return [
            ResearchSource(
                source_id="src_123",
                title="Test Source",
                url="http://example.com",
                source_type=SourceType.WEB,
                content="This is the mock content. Flying cars are real and AI exists."
            )
        ]


# ==========================================
# TESTS
# ==========================================

def test_full_workflow_execution():
    """Happy path integration test (No retries)."""
    planner_json = json.dumps({
        "original_query": "Test AI",
        "mode": "standard",
        "sub_questions": [
            {
                "id": "sq_1",
                "question": "What is AI?",
                "purpose": "To understand AI."
            }
        ]
    })

    writer_json = json.dumps({
        "executive_summary": "Summary",
        "sections": [{"title": "Intro", "content": "Text", "claim_ids": ["c1"]}],
        "claims": [{"claim_id": "c1", "text": "AI exists", "evidence_ids": ["e1"], "confidence": 0.9}],
        "evidences": [{"evidence_id": "e1", "source_id": "src_123", "quote": "AI exists", "relevance_score": 1.0}]
    })

    llm = MockSequenceLLM([planner_json, writer_json])
    tool = MockDummyTool()
    graph = build_research_graph(llm, tool, tool)

    initial_state = {
        "query": "Test AI",
        "mode": ResearchMode.STANDARD,
        "plan": None,
        "error": None,
        "sources": [],
        "errors": [],
        "report": None,
        "revision_count": 0,
        "feedback": None
    }

    final_state = asyncio.run(graph.ainvoke(initial_state))
    report = final_state.get("report")

    assert report is not None
    assert len(final_state.get("errors")) == 0
    assert final_state.get("revision_count") == 0

    # NEW ASSERTIONS: Source grounding validation
    source_ids = [s.source_id for s in report.sources]
    assert "src_123" in source_ids

    source_map = {s.source_id: s for s in report.sources}
    assert report.evidences  # ADDED: Ensure evidences list is not empty before looping
    for ev in report.evidences:
        assert ev.source_id in source_map
        source_content = source_map[ev.source_id].content
        assert source_content is not None

        # Whitespace normalization and case-insensitive comparison
        norm_quote = " ".join(ev.quote.split()).lower()
        norm_content = " ".join(source_content.split()).lower()
        assert norm_quote in norm_content


def test_workflow_retry_loop_execution():
    """
    Tests the actual compiled LangGraph conditional edge.
    Ensures that a recoverable writer error loops back to the writer node with feedback.
    """
    # 1st Call: Planner runs successfully
    planner_json = json.dumps({
        "original_query": "Test AI",
        "mode": "standard",
        "sub_questions": [
            {
                "id": "sq_1",
                "question": "What is AI?",
                "purpose": "To understand AI."
            }
        ]
    })

    # 2nd Call: Writer runs but returns invalid JSON (triggers feedback loop)
    writer_invalid_json = "This is not valid json, causing a JSONDecodeError."

    # 3rd Call: Writer retries with feedback and succeeds
    writer_valid_json = json.dumps({
        "executive_summary": "Summary after retry",
        "sections": [{"title": "Intro", "content": "Text", "claim_ids": ["c1"]}],
        "claims": [{"claim_id": "c1", "text": "AI exists", "evidence_ids": ["e1"], "confidence": 0.9}],
        "evidences": [{"evidence_id": "e1", "source_id": "src_123", "quote": "AI exists", "relevance_score": 1.0}]
    })

    llm = MockSequenceLLM([planner_json, writer_invalid_json, writer_valid_json])
    tool = MockDummyTool()
    graph = build_research_graph(llm, tool, tool)

    initial_state = {
        "query": "Test AI",
        "mode": ResearchMode.STANDARD,
        "plan": None,
        "error": None,
        "sources": [],
        "errors": [],
        "report": None,
        "revision_count": 0,
        "feedback": None
    }

    final_state = asyncio.run(graph.ainvoke(initial_state))
    report = final_state.get("report")

    # Assertions to prove graph routing works correctly:
    assert llm.call_count == 3
    assert "CRITICAL FEEDBACK FROM PREVIOUS ATTEMPT" in llm.prompts[2]
    assert "Expecting value" in llm.prompts[2]

    assert report is not None
    assert report.executive_summary == "Summary after retry"
    assert final_state.get("feedback") is None
    assert final_state.get("revision_count") == 1

    # NEW ASSERTIONS: Source grounding validation on Retry Loop
    source_ids = [s.source_id for s in report.sources]
    assert "src_123" in source_ids

    source_map = {s.source_id: s for s in report.sources}
    assert report.evidences  # ADDED: Ensure evidences list is not empty before looping
    for ev in report.evidences:
        assert ev.source_id in source_map
        source_content = source_map[ev.source_id].content
        assert source_content is not None

        # Whitespace normalization and case-insensitive comparison
        norm_quote = " ".join(ev.quote.split()).lower()
        norm_content = " ".join(source_content.split()).lower()
        assert norm_quote in norm_content