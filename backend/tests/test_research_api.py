import asyncio
from fastapi.testclient import TestClient
from main import app
from app.schemas.research import ResearchRequest, ResearchMode
from app.services.research_service import ResearchService

client = TestClient(app)

def test_research_endpoint_success():
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

def test_research_service_unit():
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