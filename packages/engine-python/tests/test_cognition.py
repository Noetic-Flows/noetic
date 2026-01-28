import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from noetic_engine.cognition.adk_adapter import ADKAdapter
from noetic_engine.runtime.mesh import MeshOrchestrator
from noetic_conscience.contracts import AgenticIntentContract

@pytest.fixture
def mock_orchestrator():
    orchestrator = MagicMock(spec=MeshOrchestrator)
    orchestrator.route_intent = AsyncMock()
    return orchestrator

@pytest.mark.asyncio
async def test_actor_critic_loop_processing(mock_orchestrator):
    # Setup
    adapter = ADKAdapter(mock_orchestrator, agent_definition={})
    
    # Simulate an "Actor" proposal (usually this comes from ADK, we simulate it internally or via a hook)
    # For now, we will test a method `_process_proposal` which represents the Critic step.
    
    proposal = {
        "action": "tool_call",
        "tool_name": "debug_log",
        "params": {"msg": "Hello World"}
    }
    
    # Execute the step
    # We expect this to:
    # 1. Be "Criticized" (Allowed)
    # 2. Be "Executed" (routed to orchestrator)
    
    await adapter._process_proposal(proposal)
    
    # Verify Orchestrator was called
    mock_orchestrator.route_intent.assert_called_once()
    call_args = mock_orchestrator.route_intent.call_args
    assert call_args.kwargs['agent_id'] == "self" # or whatever default
    assert call_args.kwargs['tool'] == "debug_log"

@pytest.mark.asyncio
async def test_brain_loop_lifecycle():
    # Test that start/stop works without error
    orchestrator = MagicMock(spec=MeshOrchestrator)
    adapter = ADKAdapter(orchestrator, {})
    
    await adapter.start()
    assert adapter.running
    assert adapter.current_task is not None
    
    await adapter.stop()
    assert not adapter.running
