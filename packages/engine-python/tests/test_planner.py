import pytest
from noetic_engine.cognition.planner import Planner
from noetic_lang.core.stanza import StanzaDefinition, Step
from noetic_knowledge.working.stack import MemoryStack

@pytest.mark.asyncio
async def test_planner_basic_steps():
    # Define a Stanza
    stanza = StanzaDefinition(
        id="test_stanza",
        description="A simple task",
        steps=[
            Step(id="step1", instruction="Say hello"),
            Step(id="step2", instruction="Say goodbye")
        ]
    )
    
    stack = MemoryStack()
    stack.push_frame("Test Goal")
    
    planner = Planner()
    
    # Mock LLM or logic inside planner?
    # For now, let's assume the planner simply iterates steps if they are explicit.
    # In a real agentic loop, it would generate thoughts.
    
    # We will test the 'plan' method which should return a list of executable actions/steps
    plan = await planner.create_plan(stanza, stack)
    
    assert len(plan.steps) == 2
    assert plan.steps[0].instruction == "Say hello"
    assert plan.steps[1].instruction == "Say goodbye"
