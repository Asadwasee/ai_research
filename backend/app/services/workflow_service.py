import logging
from typing import AsyncGenerator
from app.schemas.research import ResearchRequest
from app.workflow.state import ResearchState
from app.workflow.graph import build_research_graph
from app.services.llm.gemini import get_llm_provider
from app.tools.research.web_search import TavilyWebSearchTool
from app.tools.research.academic_search import ArxivAcademicSearchTool
from app.schemas.workflow import WorkflowStatus

logger = logging.getLogger(__name__)

class WorkflowExecutionError(Exception):
    """Raised when the research workflow fails."""
    pass

async def run_research_workflow(request: ResearchRequest) -> ResearchState:
    """
    Entry point to execute the full LangGraph research workflow synchronously.
    """
    llm_provider = get_llm_provider()
    
    try:
        web_tool = TavilyWebSearchTool()
        academic_tool = ArxivAcademicSearchTool()
    except Exception as e:
        logger.exception("Failed to initialize research tools")
        raise WorkflowExecutionError("Failed to initialize research tools.") from e

    graph = build_research_graph(llm_provider, web_tool, academic_tool)

    initial_state: ResearchState = {
        "query": request.query,
        "mode": request.mode,
        "plan": None,
        "error": None,
        "status": WorkflowStatus.INITIALIZED,
        "sources": [],
        "findings": [],
        "errors": [],
        "report": None,
        "revision_count": 0,
        "feedback": None
    }

    try:
        final_state = await graph.ainvoke(initial_state)
        return final_state
    except Exception as e:
        logger.exception("Research workflow execution failed")
        raise WorkflowExecutionError("Research workflow execution failed.") from e

async def stream_research_workflow(request: ResearchRequest) -> AsyncGenerator[dict, None]:
    """
    Entry point to stream the LangGraph research workflow execution for real-time progress.
    """
    llm_provider = get_llm_provider()
    
    try:
        web_tool = TavilyWebSearchTool()
        academic_tool = ArxivAcademicSearchTool()
    except Exception as e:
        logger.exception("Failed to initialize research tools")
        raise WorkflowExecutionError("Failed to initialize research tools.") from e

    graph = build_research_graph(llm_provider, web_tool, academic_tool)

    initial_state: ResearchState = {
        "query": request.query,
        "mode": request.mode,
        "plan": None,
        "error": None,
        "status": WorkflowStatus.INITIALIZED,
        "sources": [],
        "findings": [],
        "errors": [],
        "report": None,
        "revision_count": 0,
        "feedback": None
    }

    try:
        # Yields node updates as they happen
        async for event in graph.astream(initial_state):
            yield event
    except Exception as e:
        logger.exception("Research workflow streaming failed")
        raise WorkflowExecutionError(f"Streaming failed: {str(e)}") from e