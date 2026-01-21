import asyncio
import time
from typing import Optional
from noetic_engine.knowledge import KnowledgeStore
from noetic_engine.skills import SkillRegistry
from noetic_engine.skills.library.system.control import WaitSkill, LogSkill
from noetic_engine.orchestration import Planner, AgentManager, FlowManager
from .reflex import ReflexSystem
from .cognitive import CognitiveSystem
from .scheduler import Scheduler

class NoeticEngine:
    def __init__(self, db_url: str = "sqlite:///:memory:"):
        self.running = False
        
        # 1. Initialize Core Subsystems
        self.knowledge = KnowledgeStore(db_url=db_url)
        self.skills = SkillRegistry()
        self.planner = Planner()
        self.agent_manager = AgentManager()
        self.flow_manager = FlowManager()
        self.latest_ui = None
        
        # 2. Register core skills
        self.skills.register(WaitSkill())
        self.skills.register(LogSkill())
        
        # 3. Initialize Loops
        self.reflex = ReflexSystem()
        self.cognitive = CognitiveSystem(
            self.knowledge, 
            self.skills, 
            self.planner, 
            self.agent_manager
        )
        self.scheduler = Scheduler(target_fps=60)

    async def start(self):
        self.running = True
        print("Noetic Engine Starting...")
        await self.run_loop()

    async def stop(self):
        self.running = False
        print("Noetic Engine Stopping...")

    async def run_loop(self):
        """
        The main Bi-Cameral Execution Loop.
        """
        while self.running:
            start_time = time.monotonic()

            # --- 1. REFLEX PHASE (Fast) ---
            world_state = self.knowledge.get_world_state()
            events = self.skills.poll_inputs()
            
            # Update UI
            self.latest_ui = self.reflex.tick(events, world_state)

            # --- 2. COGNITIVE PHASE (Async Check) ---
            if world_state.event_queue:
                asyncio.create_task(self.cognitive.process_next(world_state))

            # --- 3. SLEEP ---
            await self.scheduler.sleep_until_next_tick(start_time)