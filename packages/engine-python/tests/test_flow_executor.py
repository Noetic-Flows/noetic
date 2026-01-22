import pytest
from unittest.mock import AsyncMock, MagicMock
from noetic_engine.runtime.executors.flow_executor import FlowExecutor
from noetic_lang.core.flow import FlowDefinition, FlowState

@pytest.mark.asyncio
async def test_flow_navigation():
    # Define Flow
    flow = FlowDefinition(
        id="test_flow",
        start_at="state1",
        states={
            "state1": FlowState(name="state1", next="state2"),
            "state2": FlowState(name="state2", next=None) # End
        }
    )
    
    # Mock Interpreter (Stanza Executor)
    interpreter = MagicMock()
    # We assume the flow executor calls the interpreter for skills/stanzas associated with states
    # For this simple test, we just check navigation logic.
    interpreter.execute_stanza = AsyncMock(return_value="Done")
    
    executor = FlowExecutor(interpreter)
    
    # Run
    final_state = await executor.run_flow(flow)
    
    assert final_state == "state2"
