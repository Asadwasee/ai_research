from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.source import ResearchSource

class WorkflowStatus(str, Enum):
    INITIALIZED = "initialized"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ResearchFinding(BaseModel):
    """Simple structure to store a finding extracted from a source."""
    content: str = Field(..., description="The extracted fact or finding.")
    source_id: str = Field(..., description="ID of the source where this finding was found.")

class WorkflowError(BaseModel):
    """Structured error information to preserve details without leaking stack traces."""
    message: str = Field(..., description="Simple, safe error message.")
    details: str | None = Field(default=None, description="Optional technical context for debugging.")

class ResearchWorkflowState(BaseModel):
    """
    Minimal data contract/state model for the research workflow.
    Designed to be used by LangGraph nodes in future steps.
    """
    query: str
    status: WorkflowStatus = Field(default=WorkflowStatus.INITIALIZED)
    sources: list[ResearchSource] = Field(default_factory=list)
    findings: list[ResearchFinding] = Field(default_factory=list)
    errors: list[WorkflowError] = Field(default_factory=list)