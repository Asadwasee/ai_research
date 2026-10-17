import asyncio
import uuid
from datetime import datetime, timezone
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from app.schemas.research import ResearchRequest, ResearchMode
from app.schemas.report import ResearchReport, ReportSection, Claim
from app.schemas.source import ResearchSource, SourceType
from app.schemas.evidence import Evidence
from app.services.research_service import ResearchService

client = TestClient(app)

# Helper function to generate a mock LangGraph state for testing
def get_mock_workflow_state(query: str, mode: str):
    report_id = f"rep_{uuid.uuid4().hex[:8]}"
    
    mock_source = ResearchSource(
        source_id="src_mock_1",
        title="Mock Architectural Foundation Guide",
        url="https://example.com/mock-guide",
        source_type=SourceType.WEB,
        publisher="Mock Publisher",
        authors=["AI Assistant"],
        published_at=datetime.now(timezone.utc)
    )
    
    mock_evidence = Evidence(
        evidence_id="ev_mock_1",
        source_id=mock_source.source_id,
        quote="A definitive quote demonstrating concepts.",
        context="Extracted from the methodology overview.",
        relevance_score=0.95
    )
    
    mock_claim = Claim(
        claim_id="clm_mock_1",
        text="This is a mock claim verifying the concept.",
        evidence_ids=[mock_evidence.evidence_id],
        confidence=0.95
    )
    
    section1 = ReportSection(title="Intro", content="Content", claim_ids=[mock_claim.claim_id])
    section2 = ReportSection(title="Method", content="Content", claim_ids=[])
    
    report = ResearchReport(
        report_id=report_id,
        query=query,
        mode=mode,
        executive_summary=f"Executive summary for {query}",
        sections=[section1, section2],
        claims=[mock_claim],
        evidences=[mock_evidence],
        sources=[mock_source],
        generated_at=datetime.now(timezone.utc)
    )
    
    return {
        "report": report,
        "errors": []
    }


@patch("app.services.research_service.run_research_workflow")
def test_research_endpoint_success(mock_run_workflow):
    # Instruct the mock to return our fake state instead of hitting the LLM
    mock_state = get_mock_workflow_state("Compare RAG and fine-tuning", "standard")
    mock_run_workflow.return_value = mock_state
    
    payload = {
        "query": "Compare RAG and fine-tuning",
        "mode": "standard"
    }
    response = client.post("/api/v1/research", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Contract Verification
    assert "report_id" in data
    assert data["query"] == "Compare RAG and fine-tuning"
    assert data["mode"] == "standard"
    assert "executive_summary" in data
    assert len(data["sections"]) >= 2
    
    # Linkage verification
    assert len(data["claims"]) >= 1
    assert len(data["claims"][0]["evidence_ids"]) >= 1
    assert data["claims"][0]["evidence_ids"][0] == "ev_mock_1"
    
    assert len(data["sources"]) >= 1
    assert "generated_at" in data


def test_research_endpoint_invalid_query():
    payload = {
        "query": "   ",  # Fails min_length after whitespace stripping
        "mode": "standard"
    }
    response = client.post("/api/v1/research", json=payload)
    assert response.status_code == 422


def test_research_endpoint_invalid_mode():
    payload = {
        "query": "Valid query",
        "mode": "invalid_fake_mode"
    }
    response = client.post("/api/v1/research", json=payload)
    assert response.status_code == 422


@patch("app.services.research_service.run_research_workflow")
def test_research_service_unit(mock_run_workflow):
    # Instruct the mock to return our fake state
    mock_state = get_mock_workflow_state("Unit test query", "quick")
    mock_run_workflow.return_value = mock_state
    
    # Unit test without starting the full HTTP server
    service = ResearchService()
    request = ResearchRequest(query="Unit test query", mode=ResearchMode.QUICK)
    
    # Run async method in standard asyncio event loop
    report = asyncio.run(service.generate_report(request))
    
    assert report.query == "Unit test query"
    assert report.mode == ResearchMode.QUICK
    assert len(report.sections) == 2
    assert report.executive_summary.startswith("Executive summary for")
    
    # Linkage verification at service level
    assert len(report.claims) >= 1
    assert report.claims[0].evidence_ids[0] == "ev_mock_1"


@patch("app.services.research_service.stream_research_workflow")
def test_research_stream_endpoint(mock_stream_workflow):
    """Verifies that the /stream endpoint correctly formats Server-Sent Events (SSE)."""
    
    # Mocking the async generator yielded by LangGraph's astream
    async def mock_stream(*args, **kwargs):
        yield {"planner": {"plan": "mock_plan"}}
        yield {"researcher": {"sources": []}}
        yield {"writer": {"report": get_mock_workflow_state("Test streaming", "quick")["report"]}}
        
    mock_stream_workflow.return_value = mock_stream()
    
    payload = {
        "query": "Test streaming",
        "mode": "quick"
    }
    
    # httpx TestClient requires using 'stream' context manager for streaming responses
    with client.stream("POST", "/api/v1/research/stream", json=payload) as response:
        assert response.status_code == 200
        content = response.read().decode("utf-8")
        
        # Verify SSE format and expected real-time states
        assert "data: " in content
        assert "running" in content
        assert "planner" in content
        assert "completed" in content
        assert "report_id" in content