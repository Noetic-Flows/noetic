import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from noetic_engine.runtime.cognitive import CognitiveSystem
from noetic_engine.knowledge import KnowledgeStore, WorldState
from noetic_engine.orchestration import Planner, AgentManager, AgentContext
from noetic_engine.skills import SkillRegistry, Skill
from noetic_engine.knowledge.schema import Fact, Event
from noetic_engine.conscience import Evaluator

class MockSkill(Skill):
    id = "skill.system.wait"
    description = "Mock Wait"
    schema = {}
    preconditions = {}
    postconditions = {"done": True}
    async def execute(self, context, **kwargs):
        return MagicMock(success=True)

@pytest.mark.asyncio
async def test_process_next_executes_plan():
    # Setup
    knowledge = KnowledgeStore()
    skills = MagicMock(spec=SkillRegistry)
    evaluator = Evaluator()
    planner = Planner(skills, evaluator)
    agent_manager = AgentManager()
    
    cognitive = CognitiveSystem(knowledge, skills, planner, agent_manager)
    
    # Register Agent
    agent = AgentContext(
        id="agent-1",
        system_prompt="Test",
        allowed_skills=["skill.system.wait"],
        principles=[]
    )
    agent_manager.register(agent)
    
    # Mock Skill
    mock_skill = MockSkill()
    mock_skill.execute = AsyncMock(return_value=MagicMock(success=True))
    
    # The planner calls get_skill to check if it exists during discovery
    def get_skill_side_effect(sid):
        if sid == "skill.system.wait":
            return mock_skill
        return None
    skills.get_skill.side_effect = get_skill_side_effect
    
    # Setup State with Event
    state = WorldState(
        tick=0, 
        entities={}, 
        facts=[], 
        event_queue=[
            Event(id=uuid.uuid4(), type="test-event", timestamp=datetime.utcnow())
        ]
    )
    
    # We need to monkeypatch the Goal creation in process_next or make it deterministic
    # CognitiveSystem.process_next creates Goal(description=..., target_state={})
    # If target_state is {}, it's already satisfied.
    # Wait, if target_state is {}, Planner might return empty plan.
    # Let's ensure Goal in process_next is handled or the test expectations match.
    
    # Execute
    await cognitive.process_next(state)
    
    # Assert
    # Verify execution
    mock_skill.execute.assert_called()
