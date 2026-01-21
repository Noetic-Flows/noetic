import os
import pytest
from noetic_engine.loader import NoeticLoader
from noetic_engine.runtime.engine import NoeticEngine

def test_load_codex():
    # Setup
    engine = NoeticEngine()
    loader = NoeticLoader()
    codex_path = os.path.join(os.path.dirname(__file__), "test_codex.noetic")
    
    # Execute
    loader.load(engine, codex_path)
    
    # Assert Agents
    agent = engine.agent_manager.get("agent-1")
    assert agent is not None
    assert agent.system_prompt == "You are a helpful assistant."
    assert "skill.system.wait" in agent.allowed_skills
    
    # Assert Canvas
    assert engine.reflex.root_component is not None
    assert engine.reflex.root_component.id == "root"
    assert engine.reflex.root_component.type == "Box"

    # Assert Flows
    assert engine.flow_manager.get_executor("flow.test") is not None

    # Assert Skills
    assert engine.skills.get_skill("skill.custom.test") is not None
    assert engine.skills.get_skill("skill.custom.test").description == "A custom test skill"
