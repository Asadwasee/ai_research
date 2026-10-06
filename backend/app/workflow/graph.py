from langgraph.graph import StateGraph, START, END
from app.workflow.state import ResearchState
from app.workflow.nodes.planner import run_planner
from app.workflow.nodes.researcher import run_researcher
from app.services.llm.base import LLMProvider
from app.tools.research.base import ResearchTool

def build_research_graph(
    llm_provider: LLMProvider,
    web_tool: ResearchTool,
    academic_tool: ResearchTool
):
    """
    Constructs and compiles the LangGraph workflow for the research agent.
    """
    workflow = StateGraph(ResearchState)

    # Wrappers to inject dependencies
    async def planner_node(state: ResearchState):
        return await run_planner(state, llm_provider)

    async def researcher_node(state: ResearchState):
        return await run_researcher(state, web_tool, academic_tool)

    # Add Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)

    # Define Edges (Routing)
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", END)

    # Compile the graph
    return workflow.compile()