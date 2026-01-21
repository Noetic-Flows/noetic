import pytest
from unittest.mock import MagicMock, patch
from noetic_engine.orchestration.flows import FlowExecutor
from noetic_engine.knowledge import WorldState

# Minimal flow definition
SIMPLE_FLOW = {
    "id": "flow.simple",
    "start_at": "Step1",
    "states": {
        "Step1": {
            "type": "Interaction", # Uses a skill
            "skill": "skill.debug.log",
            "params": {"message": "Step 1 Executed"},
            "next": "Step2"
        },
        "Step2": {
            "type": "Interaction",
            "skill": "skill.debug.log",
            "params": {"message": "Step 2 Executed"},
            "end": True
        }
    }
}

@pytest.fixture
def mock_world_state():
    return WorldState(tick=0, entities={}, facts=[])

def test_flow_executor_init(mock_world_state):
    # This test verifies that the graph is built without errors
    # We mock StateGraph to avoid needing the actual library if complex
    # but let's try to use the real one if imported, or skip if ImportError logic in class handles it.
    
    executor = FlowExecutor(SIMPLE_FLOW)
    
    # We can't easily assert the internal graph structure of LangGraph 
    # without intimate knowledge of its object, but we can check if runnable is created.
    # Note: FlowExecutor currently requires LangGraph installed.
    
    assert executor.runnable is not None

def test_flow_execution_step(mock_world_state):
    executor = FlowExecutor(SIMPLE_FLOW)
    if not executor.runnable:
        pytest.skip("LangGraph not available")
        
    # We want to verify that the steps are executed.
    # Since we can't easily spy on the internal node execution which calls skills 
    # (skills are not injected into FlowExecutor yet, it just builds the graph),
    # we need to define how the nodes "work".
    
    # The current FlowExecutor stub doesn't define what the nodes DO.
    # It just builds an empty StateGraph(dict).
    # So this test is expected to fail or do nothing interesting until we implement logic.
    
    result = executor.step({"trace": []}, mock_world_state)
    assert result is not None
    
    # Verify execution order
    assert result.get("trace") == ["Step1", "Step2"]
    
    # Verify the last state's params were merged (simple behavior)
    assert result.get("message") == "Step 2 Executed"
