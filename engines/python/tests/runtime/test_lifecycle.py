import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from noetic_engine.runtime.lifecycle import LifecycleManager

# Mock constants for faster tests
IDLE_TIMEOUT = 0.1
REM_TIMEOUT = 0.2

class MockEngine:
    def __init__(self):
        self.knowledge = MagicMock()
        self.knowledge.run_sleep_cycle = AsyncMock()

@pytest.fixture
def lifecycle_manager():
    engine = MockEngine()
    manager = LifecycleManager(engine)
    # Override timeouts for testing
    manager.idle_timeout = IDLE_TIMEOUT
    manager.rem_timeout = REM_TIMEOUT
    return manager

@pytest.mark.asyncio
async def test_initial_state(lifecycle_manager):
    assert lifecycle_manager.state == "AWAKE"

@pytest.mark.asyncio
async def test_idleness_transition(lifecycle_manager):
    # Simulate time passing without interaction
    await asyncio.sleep(IDLE_TIMEOUT + 0.05)
    await lifecycle_manager.tick()
    
    assert lifecycle_manager.state == "IDLE"

@pytest.mark.asyncio
async def test_rem_transition(lifecycle_manager):
    # Go to IDLE first
    lifecycle_manager.state = "IDLE"
    # Reset interaction timer logic implicitly or explicitly depending on implementation
    # Assuming tick checks (now - last_interaction)
    
    # Wait enough for REM
    await asyncio.sleep(REM_TIMEOUT + 0.05)
    await lifecycle_manager.tick()
    
    assert lifecycle_manager.state == "REM"
    # Verify sleep cycle was called
    assert lifecycle_manager.engine.knowledge.run_sleep_cycle.called or lifecycle_manager.maintenance_task is not None

@pytest.mark.asyncio
async def test_wake_interrupt(lifecycle_manager):
    # Start in REM
    await lifecycle_manager.enter_rem_sleep()
    assert lifecycle_manager.state == "REM"
    assert lifecycle_manager.maintenance_task is not None
    
    # Simulate interaction
    await lifecycle_manager.notify_interaction()
    
    assert lifecycle_manager.state == "AWAKE"
    assert lifecycle_manager.maintenance_task.cancelled() or lifecycle_manager.maintenance_task.done()

@pytest.mark.asyncio
async def test_interaction_resets_timer(lifecycle_manager):
    # Wait a bit
    await asyncio.sleep(IDLE_TIMEOUT / 2)
    await lifecycle_manager.notify_interaction()
    
    # Wait another bit (total > IDLE_TIMEOUT if not reset)
    await asyncio.sleep(IDLE_TIMEOUT / 2 + 0.05)
    await lifecycle_manager.tick()
    
    # Should still be AWAKE because timer was reset
    assert lifecycle_manager.state == "AWAKE"
