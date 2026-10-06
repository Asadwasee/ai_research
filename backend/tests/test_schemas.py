import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas import (
    ResearchRequest, ResearchPlan, ResearchSubQuestion, ResearchMode,
    ResearchSource, SourceType, Evidence, Claim, ResearchReport, ReportSection
)

def test_valid_research_request():
    req = ResearchRequest(query="  Compare RAG and fine-tuning  ")
    assert req.query == "Compare RAG and fine-tuning" # Stripped whitespace
    assert req.mode == ResearchMode.STANDARD

def test_empty_query_rejected():
    with pytest.raises(ValidationError):
        ResearchRequest(query="   ") # Only spaces
    with pytest.raises(ValidationError):
        ResearchRequest(query="") # Empty string

def test_query_too_long_rejected():
    with pytest.raises(ValidationError):
        ResearchRequest(query="A" * 4001)

def test_research_plan_validation():
    sub_q = ResearchSubQuestion(id="q1", question="What is RAG?", purpose="Intro")
    
    # Valid Plan
    plan = ResearchPlan(original_query="AI", sub_questions=[sub_q], mode=ResearchMode.QUICK)
    assert len(plan.sub_questions) == 1
    
    # Empty sub_questions rejected
    with pytest.raises(ValidationError):
        ResearchPlan(original_query="AI", sub_questions=[], mode=ResearchMode.QUICK)

def test_valid_research_source_datetime():
    # Explicitly test datetime conversion from string
    source = ResearchSource(
        source_id="src_1",
        title="LangChain Docs",
        url="https://python.langchain.com",
        source_type=SourceType.WEB,
        published_at="2026-10-04T12:00:00Z"
    )
    assert str(source.url) == "https://python.langchain.com/"
    assert isinstance(source.published_at, datetime)

def test_evidence_relevance_score():
    # Valid score
    ev = Evidence(evidence_id="e1", source_id="s1", quote="AI is good", relevance_score=0.85)
    assert ev.relevance_score == 0.85

    # Valid boundaries explicitly tested
    ev_min = Evidence(evidence_id="e2", source_id="s2", quote="quote", relevance_score=0.0)
    assert ev_min.relevance_score == 0.0
    
    ev_max = Evidence(evidence_id="e3", source_id="s3", quote="quote", relevance_score=1.0)
    assert ev_max.relevance_score == 1.0
    
    # Above max
    with pytest.raises(ValidationError):
        Evidence(evidence_id="e4", source_id="s1", quote="AI", relevance_score=1.1)
        
    # Below min
    with pytest.raises(ValidationError):
        Evidence(evidence_id="e5", source_id="s1", quote="AI", relevance_score=-0.1)

def test_claim_confidence_validation():
    # Valid boundaries explicitly tested
    c_min = Claim(claim_id="c1", text="AI", confidence=0.0)
    assert c_min.confidence == 0.0

    c_max = Claim(claim_id="c2", text="AI", confidence=1.0)
    assert c_max.confidence == 1.0

    # Invalid values
    with pytest.raises(ValidationError):
        Claim(claim_id="c3", text="AI", confidence=1.5)
    
    with pytest.raises(ValidationError):
        Claim(claim_id="c4", text="AI", confidence=-0.5)

def test_valid_research_report_and_datetime():
    # Explicit valid construction test and datetime verification
    section = ReportSection(title="Methodology", content="We used RAG.")
    report = ResearchReport(
        report_id="r1",
        query="AI vs Human",
        mode=ResearchMode.DEEP,
        executive_summary="Summary text",
        sections=[section],
        generated_at="2026-10-04T14:30:00+00:00"
    )
    
    assert len(report.sections) == 1
    assert report.sections[0].title == "Methodology"
    assert isinstance(report.generated_at, datetime)

def test_research_report_requires_sections():
    with pytest.raises(ValidationError):
        ResearchReport(
            report_id="r1",
            query="AI",
            mode=ResearchMode.STANDARD,
            executive_summary="Summary",
            sections=[], # Empty sections array
            generated_at=datetime.now()
        )