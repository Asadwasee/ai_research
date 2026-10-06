import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from app.schemas.research import ResearchRequest, ResearchMode
from app.workflow.state import ResearchState
from app.schemas.workflow import WorkflowStatus
from app.services.workflow_service import run_research_workflow, WorkflowExecutionError

def test_workflow_service_success():
    request = ResearchRequest(query="Test workflow query", mode=ResearchMode.STANDARD)
    
    mock_final_state: ResearchState = {
        "query": "Test workflow query",
        "mode": ResearchMode.STANDARD,
        "plan": MagicMock(),
        "error": None,
        "status": WorkflowStatus.COMPLETED,
        "sources": [],
        "findings": [],
        "errors": []
    }
    
    with patch("app.services.workflow_service.get_llm_provider") as mock_get_llm, \
         patch("app.services.workflow_service.TavilyWebSearchTool") as mock_web, \
         patch("app.services.workflow_service.ArxivAcademicSearchTool") as mock_acad, \
         patch("app.services.workflow_service.build_research_graph") as mock_build_graph:
        
        mock_graph_instance = MagicMock()
        mock_graph_instance.ainvoke = AsyncMock(return_value=mock_final_state)
        mock_build_graph.return_value = mock_graph_instance
        
        result = asyncio.run(run_research_workflow(request))
        
        assert result == mock_final_state
        mock_get_llm.assert_called_once()
        mock_web.assert_called_once()
        mock_acad.assert_called_once()
        mock_build_graph.assert_called_once()
        
        initial_state_arg = mock_graph_instance.ainvoke.call_args[0][0]
        assert initial_state_arg["query"] == "Test workflow query"
        assert initial_state_arg["mode"] == ResearchMode.STANDARD
        assert initial_state_arg["plan"] is None
        assert initial_state_arg["status"] == WorkflowStatus.INITIALIZED

def test_workflow_service_failure():
    request = ResearchRequest(query="Test failure query", mode=ResearchMode.DEEP)
    
    with patch("app.services.workflow_service.get_llm_provider"), \
         patch("app.services.workflow_service.TavilyWebSearchTool"), \
         patch("app.services.workflow_service.ArxivAcademicSearchTool"), \
         patch("app.services.workflow_service.build_research_graph") as mock_build_graph:
        
        mock_graph_instance = MagicMock()
        mock_graph_instance.ainvoke = AsyncMock(side_effect=Exception("Internal graph execution failed"))
        mock_build_graph.return_value = mock_graph_instance
        
        with pytest.raises(WorkflowExecutionError) as exc_info:
            asyncio.run(run_research_workflow(request))
            
        assert "Research workflow execution failed." in str(exc_info.value)