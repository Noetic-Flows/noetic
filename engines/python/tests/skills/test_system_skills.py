import pytest
import time
from unittest.mock import MagicMock
from noetic_engine.skills.library.system.control import WaitSkill, LogSkill
from noetic_engine.skills import SkillContext

@pytest.mark.asyncio
async def test_wait_skill():
    skill = WaitSkill()
    context = SkillContext(agent_id="test-agent")
    
    start = time.monotonic()
    result = await skill.execute(context, seconds=0.1)
    duration = time.monotonic() - start
    
    assert result.success is True
    assert result.data["waited"] == 0.1
    # Check if it actually waited (approx)
    assert duration >= 0.1

@pytest.mark.asyncio
async def test_log_skill():
    skill = LogSkill()
    context = SkillContext(agent_id="test-agent")
    
    result = await skill.execute(context, message="Hello", level="info")
    
    assert result.success is True
    # We can't easily capture stdout without capsys fixture, 
    # but we verify the result object is correct.
    assert result.latency_ms >= 0
