from langgraph.graph import StateGraph, START, END
from app.workflow.state import ResearchState
from app.workflow.nodes.planner import run_planner
from app.workflow.nodes.researcher import run_researcher
from app.workflow.nodes.writer import run_writer
from app.services.llm.base import LLMProvider
from app.tools.research.base import ResearchTool

def route_after_writer(state: ResearchState) -> str:
    """Deterministic python router for quality gate."""
    if state.get("report") is not None:
        return END
    if state.get("feedback") is not None:
        return "writer"
    # Reached here if report is None and feedback is None (Fatal error or Retries Exhausted)
    return END

def build_research_graph(
    llm_provider: LLMProvider,
    web_tool: ResearchTool,
    academic_tool: ResearchTool
):
    workflow = StateGraph(ResearchState)

    async def planner_node(state: ResearchState):
        return await run_planner(state, llm_provider)

    async def researcher_node(state: ResearchState):
        return await run_researcher(state, web_tool, academic_tool)

    async def writer_node(state: ResearchState):
        return await run_writer(state, llm_provider)

    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("writer", writer_node)

    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "writer")

    # Conditional routing instead of direct END
    workflow.add_conditional_edges(
        "writer",
        route_after_writer,
        {"writer": "writer", END: END}
    )
    return workflow.compile()