import json
import logging
from fastapi import HTTPException
from app.schemas.research import ResearchRequest
from app.schemas.report import ResearchReport
from app.services.workflow_service import run_research_workflow, stream_research_workflow, WorkflowExecutionError

logger = logging.getLogger(__name__)

class ResearchService:
    """
    Service responsible for orchestrating the AI research workflow.
    """
    
    async def generate_report(self, request: ResearchRequest) -> ResearchReport:
        """Executes the workflow and returns the final report (Synchronous mapping)."""
        try:
            final_state = await run_research_workflow(request)
            report = final_state.get("report")
            
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

    async def stream_report_events(self, request: ResearchRequest):
        """
        Generator that yields Server-Sent Events (SSE) for the research workflow.
        """
        try:
            async for event in stream_research_workflow(request):
                # LangGraph event is a dict: {'node_name': state_update}
                for node_name, state_update in event.items():
                    
                    if node_name == "writer" and state_update.get("report"):
                        # Final report generated successfully
                        report_dict = state_update["report"].model_dump(mode='json')
                        yield f"data: {json.dumps({'status': 'completed', 'node': node_name, 'report': report_dict})}\n\n"
                    
                    elif node_name == "writer" and state_update.get("feedback"):
                        # Retry loop triggered
                        yield f"data: {json.dumps({'status': 'retrying', 'node': node_name, 'feedback': state_update['feedback']})}\n\n"
                    
                    else:
                        # Standard progress update
                        yield f"data: {json.dumps({'status': 'running', 'node': node_name})}\n\n"
                        
        except WorkflowExecutionError as e:
            yield f"data: {json.dumps({'status': 'error', 'detail': str(e)})}\n\n"
        except Exception as e:
            logger.exception("Unexpected error during streaming")
            yield f"data: {json.dumps({'status': 'error', 'detail': 'An unexpected error occurred.'})}\n\n"


def get_research_service() -> ResearchService:
    """Dependency provider for ResearchService."""
    return ResearchService()