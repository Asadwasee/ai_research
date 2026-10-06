import pytest
from pydantic import ValidationError
from app.schemas.workflow import (
    ResearchWorkflowState, 
    WorkflowStatus, 
    ResearchFinding, 
    WorkflowError
)
from app.schemas.source import ResearchSource, SourceType

def test_initial_workflow_state():
    """Verify that a valid initial research state can be created."""
    state = ResearchWorkflowState(query="What are AI Agents?")
    
    assert state.query == "What are AI Agents?"
    assert state.status == WorkflowStatus.INITIALIZED
    assert state.sources == []
    assert state.findings == []
    assert state.errors == []

def test_workflow_state_stores_sources():
    """Verify that ResearchSource objects can be correctly stored."""
    source = ResearchSource(
        source_id="src_123",
        title="Test Source",
        url="https://example.com",
        source_type=SourceType.WEB,
        publisher="Test Pub",
        authors=[],
        published_at=None
    )
    state = ResearchWorkflowState(query="Test", sources=[source])
    
    assert len(state.sources) == 1
    assert state.sources[0].source_id == "src_123"
    assert state.sources[0].source_type == SourceType.WEB

def test_workflow_state_stores_findings():
    """Verify that structured findings can be stored."""
    finding = ResearchFinding(content="AI agents use LangGraph.", source_id="src_123")
    state = ResearchWorkflowState(query="Test", findings=[finding])
    
    assert len(state.findings) == 1
    assert state.findings[0].content == "AI agents use LangGraph."
    assert state.findings[0].source_id == "src_123"

def test_workflow_state_stores_errors():
    """Verify that structured errors can be stored."""
    error = WorkflowError(message="Network timeout", details="Tavily API took too long")
    state = ResearchWorkflowState(query="Test", errors=[error])
    
    assert len(state.errors) == 1
    assert state.errors[0].message == "Network timeout"
    assert state.errors[0].details == "Tavily API took too long"

def test_workflow_status_validation():
    """Verify that status only accepts valid intended values."""
    # Valid status transition
    state = ResearchWorkflowState(query="Test", status=WorkflowStatus.IN_PROGRESS)
    assert state.status == WorkflowStatus.IN_PROGRESS
    
    # Invalid status should raise validation error
    with pytest.raises(ValidationError):
        ResearchWorkflowState(query="Test", status="INVALID_STATE_STRING")