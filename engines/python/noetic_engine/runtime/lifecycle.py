import asyncio
import time
import logging

logger = logging.getLogger(__name__)

class LifecycleManager:
    def __init__(self, engine):
        self.engine = engine
        self.state = "AWAKE"
        self.last_interaction = time.monotonic()
        self.maintenance_task = None
        
        # Configuration (seconds)
        self.idle_timeout = 5 * 60  # 5 minutes
        self.rem_timeout = 30 * 60  # 30 minutes
        
    async def notify_interaction(self):
        """Called when a user input event occurs."""
        self.last_interaction = time.monotonic()
        
        if self.state == "REM":
            await self.wake_up()
        elif self.state == "IDLE":
            self.state = "AWAKE"
            logger.info("Lifecycle: Transitioned IDLE -> AWAKE")

    async def tick(self):
        """Called every frame/tick to check state."""
        now = time.monotonic()
        elapsed = now - self.last_interaction
        
        if self.state == "AWAKE":
            if elapsed > self.idle_timeout:
                self.state = "IDLE"
                logger.info("Lifecycle: Transitioned AWAKE -> IDLE")
        
        elif self.state == "IDLE":
            if elapsed > self.rem_timeout:
                await self.enter_rem_sleep()

    async def enter_rem_sleep(self):
        logger.info("💤 Entering REM Sleep (Maintenance Mode)...")
        self.state = "REM"
        
        # Start the background maintenance task
        if hasattr(self.engine.knowledge, 'run_sleep_cycle'):
             self.maintenance_task = asyncio.create_task(
                self.engine.knowledge.run_sleep_cycle()
            )
        else:
            logger.warning("Knowledge store does not implement run_sleep_cycle")

    async def wake_up(self):
        if self.state == "REM":
            logger.info("⚡ Waking up due to User Interrupt!")
            
            # 1. Cancel the sleep cycle immediately
            if self.maintenance_task:
                self.maintenance_task.cancel()
                try:
                    await self.maintenance_task
                except asyncio.CancelledError:
                    logger.info("Maintenance paused.")
            
            # 2. Reset State
            self.state = "AWAKE"
            self.last_interaction = time.monotonic()
