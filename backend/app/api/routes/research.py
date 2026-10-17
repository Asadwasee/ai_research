from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.schemas.research import ResearchRequest
from app.schemas.report import ResearchReport
from app.services.research_service import ResearchService, get_research_service

router = APIRouter(
    prefix="/research",
    tags=["Research"]
)

@router.post("", response_model=ResearchReport)
async def create_research_report(
    request: ResearchRequest,
    service: ResearchService = Depends(get_research_service)
):
    """
    Accepts a research query and generates a structured, evidence-grounded research report.
    (Waits for the full workflow to finish).
    """
    return await service.generate_report(request)


@router.post("/stream")
async def stream_research_report(
    request: ResearchRequest,
    service: ResearchService = Depends(get_research_service)
):
    """
    Streams the research workflow progress using Server-Sent Events (SSE).
    Provides real-time updates on LangGraph node execution for the frontend.
    """
    return StreamingResponse(
        service.stream_report_events(request),
        media_type="text/event-stream"
    )