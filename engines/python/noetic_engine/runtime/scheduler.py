import time
import asyncio

class Scheduler:
    """
    Precise timing mechanism for the Reflex Loop.
    """
    def __init__(self, target_fps: int = 60):
        self.target_dt = 1.0 / target_fps
    
    async def sleep_until_next_tick(self, start_time: float):
        elapsed = time.monotonic() - start_time
        sleep_time = max(0.0, self.target_dt - elapsed)
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
