import pytest
from unittest.mock import AsyncMock, MagicMock
from noetic_engine.runtime.interpreter import Interpreter
from noetic_engine.cognition.planner import Planner
from noetic_lang.core.stanza import StanzaDefinition
from noetic_knowledge.working.stack import MemoryStack
from noetic_lang.core import Plan, PlanStep

@pytest.mark.asyncio
async def test_interpreter_lifecycle():
    # Mocks
    stack = MemoryStack()
    planner = MagicMock()
    planner.create_plan = AsyncMock(return_value=Plan(
        steps=[PlanStep(skill_id="s1", params={}, cost=1)],
        total_cost=1
    ))
    
    executor = MagicMock()
    executor.execute_step = AsyncMock(return_value="Step Result")
    
    interpreter = Interpreter(stack, planner, executor)
    
    stanza = StanzaDefinition(
        id="test_stanza",
        description="Desc",
        steps=[]
    )
    
    # Run
    await interpreter.execute_stanza(stanza)
    
    # Assertions
    # 1. Stack should have a frame for the stanza
    # (Since execute_stanza pops at the end, we check if it was used properly or check side effects)
    # Ideally, we mock the stack to spy on push/pop.
    
    planner.create_plan.assert_called_once()
    executor.execute_step.assert_called_once()
