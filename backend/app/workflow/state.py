from typing import TypedDict
from app.schemas.research import ResearchMode, ResearchPlan
from app.schemas.source import ResearchSource
from app.schemas.workflow import WorkflowStatus, ResearchFinding, WorkflowError
from app.schemas.report import ResearchReport

class ResearchState(TypedDict):
    query: str
    mode: ResearchMode
    plan: ResearchPlan | None
    error: str | None
    status: WorkflowStatus
    sources: list[ResearchSource]
    findings: list[ResearchFinding]
    errors: list[WorkflowError]
    report: ResearchReport | None
    revision_count: int
    feedback: str | None