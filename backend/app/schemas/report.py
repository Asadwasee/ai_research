from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.research import ResearchMode
from app.schemas.source import ResearchSource

class Claim(BaseModel):
    claim_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

class ReportSection(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    claim_ids: list[str] = Field(default_factory=list)

class ResearchReport(BaseModel):
    report_id: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    mode: ResearchMode
    executive_summary: str = Field(..., min_length=1)
    sections: list[ReportSection] = Field(..., min_length=1)
    claims: list[Claim] = Field(default_factory=list)
    sources: list[ResearchSource] = Field(default_factory=list)
    generated_at: datetime