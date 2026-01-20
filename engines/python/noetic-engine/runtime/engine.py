import asyncio
import time
from typing import Optional
from noetic-engine.knowledge import KnowledgeStore
from noetic-engine.skills import SkillRegistry
from noetic-engine.skills.library.system.control import WaitSkill, LogSkill

class NoeticEngine:
    def __init__(self, db_url: str = "sqlite:///:memory:"):
        self.running = False
        self.knowledge = KnowledgeStore(db_url=db_url)
        self.skills = SkillRegistry()
        
        # Register core skills
        self.skills.register(WaitSkill())
        self.skills.register(LogSkill())
        
        # TODO: Initialize Reflex and Cognitive systems

    async def start(self):
        self.running = True
        print("Noetic Engine Starting...")
        await self.run_loop()

    async def stop(self):
        self.running = False
        print("Noetic Engine Stopping...")

    async def run_loop(self):
        """
        The main 60Hz loop.
        """
        while self.running:
            start_time = time.monotonic()

            # 1. Reflex Phase (UI, Inputs)
            # events = self.reflex.tick() 
            
            # 2. Cognitive Phase (Planning)
            # if events:
            #     asyncio.create_task(self.cognitive.process(events))

            # 3. Sleep to maintain 60Hz
            elapsed = time.monotonic() - start_time
            sleep_time = max(0, 0.016 - elapsed)
            await asyncio.sleep(sleep_time)
