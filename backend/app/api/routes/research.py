from fastapi import APIRouter, Depends
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
    """
    return await service.generate_report(request)