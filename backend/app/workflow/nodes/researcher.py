import logging
from typing import Dict, Any
from app.workflow.state import ResearchState
from app.schemas.workflow import WorkflowError
from app.tools.research.base import ResearchTool, ResearchToolError

logger = logging.getLogger(__name__)

async def run_researcher(
    state: ResearchState,
    web_tool: ResearchTool,
    academic_tool: ResearchTool
) -> Dict[str, Any]:
    """
    Orchestrates research tools based on the planner's output.
    """
    plan = state.get("plan")
    if not plan:
        error = WorkflowError(
            message="No research plan found in state.",
            details="Planner node did not produce a valid research plan."
        )
        return {"errors": state.get("errors", []) + [error]}

    mode = state.get("mode")
    
    all_sources = list(state.get("sources") or [])
    all_errors = list(state.get("errors") or [])

    for sq in plan.sub_questions:
        # Strictly following schema contract (Pydantic attribute access)
        query = sq.question
        
        try:
            web_sources = await web_tool.search(query=query, max_results=3)
            all_sources.extend(web_sources)
        except ResearchToolError as e:
            logger.warning(f"Web tool failed for query '{query}': {e}")
            all_errors.append(WorkflowError(message=f"Web search failed for: {query}", details=str(e)))
        except Exception as e:
            logger.error(f"Unexpected error in web search: {e}")
            all_errors.append(WorkflowError(message=f"Unexpected web search error for: {query}", details=str(e)))

        if mode and mode.value == "deep":
            try:
                acad_sources = await academic_tool.search(query=query, max_results=2)
                all_sources.extend(acad_sources)
            except ResearchToolError as e:
                logger.warning(f"Academic tool failed for query '{query}': {e}")
                all_errors.append(WorkflowError(message=f"Academic search failed for: {query}", details=str(e)))
            except Exception as e:
                logger.error(f"Unexpected error in academic search: {e}")
                all_errors.append(WorkflowError(message=f"Unexpected academic search error for: {query}", details=str(e)))

    # Deduplicate sources deterministically by source_id
    unique_sources = {}
    for source in all_sources:
        if source.source_id not in unique_sources:
            unique_sources[source.source_id] = source

    return {
        "sources": list(unique_sources.values()),
        "errors": all_errors
    }