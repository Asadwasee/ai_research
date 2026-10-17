import logging
from fastapi import HTTPException
from app.schemas.research import ResearchRequest
from app.schemas.report import ResearchReport
from app.services.workflow_service import run_research_workflow, WorkflowExecutionError

logger = logging.getLogger(__name__)

class ResearchService:
    """
    Service responsible for orchestrating the AI research workflow.
    Connects the FastAPI route to the LangGraph execution engine.
    """
    
    async def generate_report(self, request: ResearchRequest) -> ResearchReport:
        """
        Executes the LangGraph research workflow and returns the generated report.
        Raises HTTPException if the workflow fails or returns no report.
        """
        try:
            # Trigger the actual LangGraph workflow
            final_state = await run_research_workflow(request)
            
            report = final_state.get("report")
            
            # Check if workflow failed to generate a report (e.g., retries exhausted)
            if not report:
                errors = final_state.get("errors", [])
                error_msg = errors[-1].message if errors else "Workflow failed to generate a report."
                logger.error(f"Research failed: {error_msg}")
                raise HTTPException(status_code=500, detail=error_msg)
                
            return report
            
        except WorkflowExecutionError as e:
            logger.error(f"Workflow execution error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Unexpected error in research service")
            raise HTTPException(status_code=500, detail="An unexpected error occurred during research.")

def get_research_service() -> ResearchService:
    """Dependency provider for ResearchService."""
    return ResearchService()