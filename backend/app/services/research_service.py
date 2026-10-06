import uuid
from datetime import datetime, timezone
from app.schemas.research import ResearchRequest
from app.schemas.report import ResearchReport, ReportSection, Claim
from app.schemas.source import ResearchSource, SourceType
from app.schemas.evidence import Evidence

class ResearchService:
    """
    Service responsible for orchestrating the AI research workflow.
    Currently implements a deterministic mock for architectural validation.
    """
    
    async def generate_report(self, request: ResearchRequest) -> ResearchReport:
        """
        Generates a research report based on the provided request.
        Future implementation will trigger the LangGraph workflow here.
        """
        # Deterministic mock generation
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
        
        # Conceptually linking Evidence to Source
        mock_evidence = Evidence(
            evidence_id="ev_mock_1",
            source_id=mock_source.source_id,
            quote=f"A definitive quote demonstrating concepts related to: {request.query}",
            context="Extracted from the methodology overview.",
            relevance_score=0.95
        )
        
        # Conceptually linking Claim to Evidence
        mock_claim = Claim(
            claim_id="clm_mock_1",
            text=f"This is a mock claim verifying the concept of: {request.query}",
            evidence_ids=[mock_evidence.evidence_id],
            confidence=0.95
        )
        
        section1 = ReportSection(
            title="Introduction & Overview",
            content=f"This report addresses the query: '{request.query}'. It explores the foundational concepts associated with the request.",
            claim_ids=[mock_claim.claim_id]
        )
        
        section2 = ReportSection(
            title="Methodology",
            content=f"Research was conducted using the {request.mode.value} mode. The system is currently returning deterministic mock data to validate the API contract.",
            claim_ids=[]
        )
        
        return ResearchReport(
            report_id=report_id,
            query=request.query, # Normalized query from Pydantic
            mode=request.mode,
            executive_summary=f"Executive summary for research on: {request.query}",
            sections=[section1, section2],
            claims=[mock_claim],
            sources=[mock_source],
            generated_at=datetime.now(timezone.utc)
        )

def get_research_service() -> ResearchService:
    """Dependency provider for ResearchService."""
    return ResearchService()