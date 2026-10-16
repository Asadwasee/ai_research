import pytest
import asyncio
import json
from datetime import datetime

from app.workflow.state import ResearchState
from app.schemas.research import ResearchMode
from app.schemas.source import ResearchSource, SourceType
from app.workflow.nodes.writer import run_writer
from app.services.llm.base import LLMProvider

class MockWriterLLM(LLMProvider):
    def __init__(self, response_texts: list[str] | str, should_raise: bool = False):
        if isinstance(response_texts, str):
            self.response_texts = [response_texts]
        else:
            self.response_texts = response_texts
        self.should_raise = should_raise
        self.last_prompt = ""
        self.call_count = 0
        
    async def generate_text(self, prompt: str) -> str:
        self.last_prompt = prompt
        self.call_count += 1
        if self.should_raise:
            raise Exception("LLM crash")
        idx = min(self.call_count - 1, len(self.response_texts) - 1)
        return self.response_texts[idx]

def get_writer_state(sources_count: int = 1, rev_count: int = 0) -> ResearchState:
    sources = []
    for i in range(sources_count):
        sources.append(ResearchSource(
            source_id=f"src_{i}",
            title=f"Source {i}",
            url=f"http://example.com/{i}",
            source_type=SourceType.WEB,
            content=f"Content {i}. AI exists. Q Q1 Q2."
        ))
    return {
        "query": "Test query",
        "mode": ResearchMode.STANDARD,
        "plan": None,
        "error": None,
        "sources": sources,
        "errors": [],
        "report": None,
        "revision_count": rev_count,
        "feedback": None
    }

# 1. Success
def test_writer_success_with_evidences():
    valid_json = json.dumps({
        "executive_summary": "Summary",
        "sections": [{"title": "Intro", "content": "Text", "claim_ids": ["c1"]}],
        "claims": [{"claim_id": "c1", "text": "AI exists", "evidence_ids": ["e1"], "confidence": 0.9}],
        "evidences": [{"evidence_id": "e1", "source_id": "src_0", "quote": "AI exists", "relevance_score": 1.0}]
    })
    llm = MockWriterLLM(valid_json)
    state = get_writer_state(1)
    
    result = asyncio.run(run_writer(state, llm))
    assert result.get("report") is not None
    assert result.get("feedback") is None

# 2. Invalid Source ID (Recoverable -> Feedback)
def test_invalid_source_id():
    bad_json = json.dumps({
        "executive_summary": "S",
        "sections": [{"title": "T", "content": "C", "claim_ids": []}],
        "claims": [],
        "evidences": [{"evidence_id": "e1", "source_id": "FAKE_SRC", "quote": "Q", "relevance_score": 1.0}]
    })
    llm = MockWriterLLM(bad_json)
    result = asyncio.run(run_writer(get_writer_state(1), llm))
    assert result.get("report") is None
    assert "unknown source_id" in result["feedback"]
    assert result["revision_count"] == 1

# 3. Invalid Evidence ID (Recoverable -> Feedback)
def test_invalid_evidence_id():
    bad_json = json.dumps({
        "executive_summary": "S",
        "sections": [{"title": "T", "content": "C", "claim_ids": ["c1"]}],
        "claims": [{"claim_id": "c1", "text": "C", "evidence_ids": ["FAKE_EVID"], "confidence": 0.9}],
        "evidences": [{"evidence_id": "e1", "source_id": "src_0", "quote": "Q", "relevance_score": 1.0}]
    })
    result = asyncio.run(run_writer(get_writer_state(1), MockWriterLLM(bad_json)))
    assert result.get("report") is None
    assert "unknown evidence_id" in result["feedback"]

# 4. Duplicate Evidence ID (Recoverable -> Feedback)
def test_duplicate_evidence_id():
    bad_json = json.dumps({
        "executive_summary": "S",
        "sections": [{"title": "T", "content": "C", "claim_ids": []}],
        "claims": [],
        "evidences": [
            {"evidence_id": "e1", "source_id": "src_0", "quote": "Q1", "relevance_score": 1.0},
            {"evidence_id": "e1", "source_id": "src_0", "quote": "Q2", "relevance_score": 1.0}
        ]
    })
    result = asyncio.run(run_writer(get_writer_state(1), MockWriterLLM(bad_json)))
    assert result.get("report") is None
    assert "Duplicate evidence IDs" in result["feedback"]

# 5. Duplicate Claim ID (Recoverable -> Feedback)
def test_duplicate_claim_id():
    bad_json = json.dumps({
        "executive_summary": "S",
        "sections": [{"title": "T", "content": "C", "claim_ids": []}],
        "claims": [
            {"claim_id": "c1", "text": "C1", "evidence_ids": [], "confidence": 0.9},
            {"claim_id": "c1", "text": "C2", "evidence_ids": [], "confidence": 0.9}
        ],
        "evidences": []
    })
    result = asyncio.run(run_writer(get_writer_state(1), MockWriterLLM(bad_json)))
    assert result.get("report") is None
    assert "Duplicate claim IDs" in result["feedback"]

# 6. Invalid Section Claim ID (Recoverable -> Feedback)
def test_invalid_section_claim_id():
    bad_json = json.dumps({
        "executive_summary": "S",
        "sections": [{"title": "T", "content": "C", "claim_ids": ["FAKE_CLAIM"]}],
        "claims": [],
        "evidences": []
    })
    result = asyncio.run(run_writer(get_writer_state(1), MockWriterLLM(bad_json)))
    assert result.get("report") is None
    assert "unknown claim_id" in result["feedback"]

# 7. Invalid Grounding (Recoverable -> Feedback)
def test_invalid_evidence_quote_grounding():
    bad_json = json.dumps({
        "executive_summary": "S",
        "sections": [{"title": "T", "content": "C", "claim_ids": []}],
        "claims": [],
        "evidences": [{"evidence_id": "e1", "source_id": "src_0", "quote": "Flying cars are real", "relevance_score": 1.0}]
    })
    result = asyncio.run(run_writer(get_writer_state(1), MockWriterLLM(bad_json)))
    assert result.get("report") is None
    assert "not grounded in source" in result["feedback"]

# 8. Empty sources (Fatal Error -> No Retry)
def test_writer_empty_sources():
    result = asyncio.run(run_writer(get_writer_state(0), MockWriterLLM("{}")))
    assert result.get("report") is None
    assert result.get("feedback") is None
    assert len(result["errors"]) == 1
    assert "No sources available" in result["errors"][0].message

# 9. LLM Crash (Fatal Error -> No Retry)
def test_writer_llm_crash():
    result = asyncio.run(run_writer(get_writer_state(1), MockWriterLLM("", should_raise=True)))
    assert result.get("report") is None
    assert result.get("feedback") is None
    assert len(result["errors"]) == 1
    assert "Writer node failed" in result["errors"][0].message

# 10. Max Retries Exhausted (Fatal Error -> No Retry)
def test_writer_max_retries_exhausted():
    bad_json = json.dumps({"executive_summary": "S"}) # Missing sections causes validation error
    llm = MockWriterLLM(bad_json)
    
    # Pass rev_count = 2 (which simulates that MAX_WRITER_RETRIES has been reached)
    state = get_writer_state(1, rev_count=2)
    
    result = asyncio.run(run_writer(state, llm))
    assert result.get("report") is None
    assert result.get("feedback") is None
    assert len(result["errors"]) == 1
    assert "maximum retries" in result["errors"][0].message