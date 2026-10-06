from pydantic import BaseModel, Field

class Evidence(BaseModel):
    evidence_id: str = Field(..., min_length=1)
    source_id: str = Field(..., min_length=1)
    quote: str = Field(..., min_length=1, max_length=10000)
    context: str | None = None
    relevance_score: float | None = Field(default=None, ge=0.0, le=1.0)