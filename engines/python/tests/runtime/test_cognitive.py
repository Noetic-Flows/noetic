import pytest
from unittest.mock import AsyncMock, MagicMock
from noetic_engine.runtime.cognitive import CognitiveSystem
from noetic_engine.knowledge import KnowledgeStore, WorldState
from noetic_engine.orchestration import Planner, AgentManager, AgentContext
from noetic_engine.skills import SkillRegistry, Skill
from noetic_engine.knowledge.schema import Fact

class MockSkill(Skill):
    id = "skill.system.wait"
    description = "Mock Wait"
    schema = {}
    async def execute(self, context, **kwargs):
        return MagicMock(success=True)

@pytest.mark.asyncio
async def test_process_next_executes_plan():
    # Setup
    knowledge = KnowledgeStore()
    planner = Planner()
    agent_manager = AgentManager()
    skills = MagicMock(spec=SkillRegistry)
    
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
    skills.get_skill.return_value = mock_skill
    
    # Setup State with Event
    # Event is just a Fact in queue or similar?
    # In cognitive.py: event = state.event_queue[0]
    # WorldState schema needs check.
    
    # Let's import WorldState and check if we can populate event_queue
    # WorldState is defined in knowledge/models.py or schema.py?
    # cognitive.py imports WorldState from noetic_engine.knowledge
    
    state = WorldState(tick=0, entities={}, facts=[], event_queue=[MagicMock(type="test-event")])
    
    # Execute
    await cognitive.process_next(state)
    
    # Assert
    skills.get_skill.assert_called_with("skill.system.wait")
    mock_skill.execute.assert_called_once()
    assert mock_skill.execute.call_args.kwargs['seconds'] == 1.0
