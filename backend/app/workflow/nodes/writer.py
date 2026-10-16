import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from pydantic import ValidationError

from app.workflow.state import ResearchState
from app.schemas.report import ResearchReport, ReportSection, Claim
from app.schemas.evidence import Evidence
from app.schemas.workflow import WorkflowError
from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)

MAX_WRITER_RETRIES = 2

async def run_writer(state: ResearchState, llm_provider: LLMProvider) -> Dict[str, Any]:
    query = state.get("query")
    sources = state.get("sources", [])
    rev_count = state.get("revision_count", 0)
    feedback = state.get("feedback")
    
    if not sources:
        error = WorkflowError(
            message="No sources available for report generation.",
            details="Writer node requires at least one valid source to construct a report."
        )
        # Fatal error: Does not trigger retry
        return {"errors": state.get("errors", []) + [error], "feedback": None, "report": None}

    # Build controlled context with CONTENT
    context_lines = []
    valid_source_ids = set()
    for s in sources:
        valid_source_ids.add(s.source_id)
        publisher_info = f", Publisher: {s.publisher}" if s.publisher else ""
        content_info = f"\nContent/Snippet: {s.content}" if s.content else "\nContent/Snippet: (Unavailable)"
        context_lines.append(f"- [{s.source_id}] Title: {s.title} (URL: {s.url}{publisher_info}){content_info}")
    context_str = "\n".join(context_lines)

    feedback_prompt = ""
    if feedback:
        feedback_prompt = f"\n\nCRITICAL FEEDBACK FROM PREVIOUS ATTEMPT:\nYour previous report generation failed deterministic validation. Fix ONLY the reported problems while still following all report/evidence requirements.\nValidation Error:\n{feedback}"

    prompt = f"""
    You are an expert technical researcher. Generate a comprehensive research report for the following query: "{query}"
    
    Use ONLY the following sources. Do NOT invent source IDs.
    {context_str}
    {feedback_prompt}
    
    Return ONLY valid JSON matching this exact structure (no markdown formatting, no comments):
    {{
        "executive_summary": "string",
        "sections": [
            {{
                "title": "string",
                "content": "string",
                "claim_ids": []
            }}
        ],
        "claims": [
            {{
                "claim_id": "string",
                "text": "string",
                "evidence_ids": [],
                "confidence": 0.9
            }}
        ],
        "evidences": [
            {{
                "evidence_id": "string",
                "source_id": "string",
                "quote": "string",
                "context": "string",
                "relevance_score": 0.9
            }}
        ]
    }}
    """

    try:
        raw_response = await llm_provider.generate_text(prompt)
        
        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        
        parsed_data = json.loads(clean_json.strip())
        
        parsed_evidences = [Evidence(**e) for e in parsed_data.get("evidences", [])]
        parsed_claims = [Claim(**c) for c in parsed_data.get("claims", [])]
        parsed_sections = [ReportSection(**s) for s in parsed_data.get("sections", [])]

        # ==========================================
        # DETERMINISTIC INTEGRITY VALIDATIONS
        # ==========================================
        source_map = {s.source_id: s for s in sources}

        # 1. Evidence ID Integrity
        evidence_ids = [e.evidence_id for e in parsed_evidences]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("Duplicate evidence IDs generated.")
        valid_evidence_ids = set(evidence_ids)

        # 2. Source & Grounding Integrity
        for e in parsed_evidences:
            if e.source_id not in valid_source_ids:
                raise ValueError(f"Evidence {e.evidence_id} references unknown source_id {e.source_id}")
            
            source_content = source_map[e.source_id].content
            if source_content and e.quote:
                norm_quote = " ".join(e.quote.split()).lower()
                norm_content = " ".join(source_content.split()).lower()
                if norm_quote not in norm_content:
                    raise ValueError(f"Evidence {e.evidence_id} quote is not grounded in source {e.source_id} content.")

        # 3. Claim ID Integrity
        claim_ids = [c.claim_id for c in parsed_claims]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("Duplicate claim IDs generated.")
        valid_claim_ids = set(claim_ids)

        # 4. Claim -> Evidence Integrity
        for c in parsed_claims:
            for eid in c.evidence_ids:
                if eid not in valid_evidence_ids:
                    raise ValueError(f"Claim {c.claim_id} references unknown evidence_id {eid}")

        # 5. Section -> Claim Integrity
        for s in parsed_sections:
            for cid in s.claim_ids:
                if cid not in valid_claim_ids:
                    raise ValueError(f"Section references unknown claim_id {cid}")

        report = ResearchReport(
            report_id=f"rep_{uuid.uuid4().hex[:8]}",
            query=query,
            mode=state.get("mode"),
            executive_summary=parsed_data.get("executive_summary", ""),
            sections=parsed_sections,
            claims=parsed_claims,
            evidences=parsed_evidences,
            sources=sources,
            generated_at=datetime.now(timezone.utc)
        )
        
        return {"report": report, "feedback": None, "errors": state.get("errors", [])}
        
    except (json.JSONDecodeError, ValueError, ValidationError) as e:
        error_msg = str(e)
        logger.warning(f"Writer validation failed: {error_msg}")
        
        if rev_count >= MAX_WRITER_RETRIES:
            logger.error("Writer max retries exhausted.")
            error = WorkflowError(
                message="Writer failed to generate valid report after maximum retries.",
                details=error_msg
            )
            return {"errors": state.get("errors", []) + [error], "feedback": None, "report": None}
        else:
            return {"feedback": error_msg, "revision_count": rev_count + 1, "report": None}
            
    except Exception as e:
        logger.error(f"Writer fatal execution failed: {e}")
        error = WorkflowError(message="Writer node failed during report generation.", details=str(e))
        return {"errors": state.get("errors", []) + [error], "feedback": None, "report": None}