import pytest
from noetic_engine.runtime.engine import NoeticEngine

def test_engine_initialization():
    engine = NoeticEngine()
    
    assert engine.running is False
    assert engine.knowledge is not None
    assert engine.skills is not None
    assert engine.planner is not None
    assert engine.agent_manager is not None
    assert engine.reflex is not None
    assert engine.cognitive is not None
    assert engine.scheduler is not None
    assert engine.lifecycle is not None

def test_core_skills_registered():
    engine = NoeticEngine()
    
    assert engine.skills.get_skill("skill.system.wait") is not None
    assert engine.skills.get_skill("skill.debug.log") is not None

@pytest.mark.asyncio
async def test_engine_lifecycle():
    engine = NoeticEngine()
    
    # We can't await start() because it loops forever.
    # But we can verify running state changes if we could simulate the loop.
    # For now, let's just manually set running and check stop.
    
    engine.running = True
    await engine.stop()
    assert engine.running is False
