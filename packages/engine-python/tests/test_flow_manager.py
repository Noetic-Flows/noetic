import pytest
from typing import Dict, Any
from noetic_lang.core.flow import FlowDefinition, FlowState
from noetic_engine.runtime.flow_manager import FlowManager

@pytest.fixture
def simple_flow_def():
    return FlowDefinition(
        id="flow.test.simple",
        start_at="Step1",
        states={
            "Step1": FlowState(
                type="Task",
                params={"msg": "hello"},
                next="Step2"
            ),
            "Step2": FlowState(
                type="Task",
                params={"msg": "world"},
                end=True
            )
        }
    )

def test_manager_registration(simple_flow_def):
    manager = FlowManager()
    manager.register(simple_flow_def.model_dump())
    
    assert manager.get_flow("flow.test.simple") is not None

def test_execution_creation(simple_flow_def):
    manager = FlowManager()
    manager.register(simple_flow_def.model_dump())
    
    execution_id = manager.start_flow("flow.test.simple", {"user": "test"})
    assert execution_id is not None
    
    executor = manager.get_executor(execution_id)
    assert executor is not None
    assert executor.current_state_name == "Step1"
    assert executor.context["user"] == "test"

@pytest.mark.asyncio
async def test_execution_stepping(simple_flow_def):
    manager = FlowManager()
    manager.register(simple_flow_def.model_dump())
    execution_id = manager.start_flow("flow.test.simple")
    executor = manager.get_executor(execution_id)
    
    # Step 1 -> Step 2
    # We need a tick mechanism. For now simulating a step calling.
    await executor.step() 
    assert executor.current_state_name == "Step2"
    assert not executor.is_complete
    
    # Step 2 -> End
    await executor.step()
    assert executor.is_complete
    assert executor.current_state_name is None
