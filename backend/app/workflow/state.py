from typing import TypedDict
from app.schemas.research import ResearchMode, ResearchPlan
from app.schemas.source import ResearchSource
from app.schemas.workflow import WorkflowStatus, ResearchFinding, WorkflowError

class ResearchState(TypedDict):
    """
    Maintains the state of the research workflow as it progresses through the graph.
    """
    query: str
    mode: ResearchMode
    plan: ResearchPlan | None
    error: str | None
    
    status: WorkflowStatus
    sources: list[ResearchSource]
    findings: list[ResearchFinding]
    errors: list[WorkflowError]