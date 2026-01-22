import asyncio
import time
from typing import Optional
from noetic_engine.knowledge import KnowledgeStore
from noetic_engine.skills import SkillRegistry
from noetic_engine.skills.library.system.control import WaitSkill, LogSkill
from noetic_engine.skills.library.memory import MemorizeSkill, RecallSkill
from noetic_engine.orchestration import Planner, AgentManager, FlowManager
from noetic_engine.conscience import Evaluator
from .reflex import ReflexSystem
from .cognitive import CognitiveSystem
from .scheduler import Scheduler
from .lifecycle import LifecycleManager

class NoeticEngine:
    def __init__(self, db_url: str = "sqlite:///:memory:"):
        self.running = False
        
        # 1. Initialize Core Subsystems
        self.knowledge = KnowledgeStore(db_url=db_url)
        self.skills = SkillRegistry()
        self.agent_manager = AgentManager()
        self.flow_manager = FlowManager()
        self.evaluator = Evaluator()
        
        # Planner requires skills and principles
        self.planner = Planner(self.skills, self.evaluator)
        
        self.latest_ui = None
        
        # 2. Register core skills
        self.skills.register(WaitSkill())
        self.skills.register(LogSkill())
        self.skills.register(MemorizeSkill())
        self.skills.register(RecallSkill())
        
        # 3. Initialize Loops
        self.reflex = ReflexSystem()
        self.cognitive = CognitiveSystem(
            self.knowledge, 
            self.skills, 
            self.planner, 
            self.agent_manager
        )
        self.scheduler = Scheduler(target_fps=60)
        self.lifecycle = LifecycleManager(self)

    async def start(self):
        self.running = True
        print("Noetic Engine Starting...")
        await self.run_loop()

    async def stop(self):
        self.running = False
        print("Noetic Engine Stopping...")
        # Cancel all pending cognitive tasks
        for task in self.cognitive.active_tasks:
            if not task.done():
                task.cancel()
        
        if self.cognitive.active_tasks:
            await asyncio.gather(*self.cognitive.active_tasks, return_exceptions=True)
            self.cognitive.active_tasks.clear()

    def push_event(self, event_type: str, payload: dict = None):
        """
        Public API to inject events into the Noetic Engine (e.g. from UI).
        """
        self.knowledge.push_event(event_type, payload)

    def refresh_ui(self):
        """
        Forces an immediate re-render of the latest UI.
        """
        world_state = self.knowledge.get_world_state()
        self.latest_ui = self.reflex.render_now(world_state)

    async def run_loop(self):
        """
        The main Bi-Cameral Execution Loop.
        """
        print("Noetic Engine Loop Running...")
        while self.running:
            start_time = time.monotonic()

            try:
                # --- 1. REFLEX PHASE (Fast) ---
                world_state = self.knowledge.get_world_state()
                events = self.skills.poll_inputs()
                
                # Update Lifecycle
                if events:
                    await self.lifecycle.notify_interaction()
                await self.lifecycle.tick()
                
                # Update UI
                self.latest_ui = self.reflex.tick(events, world_state)

                # --- 2. COGNITIVE PHASE (Async Check) ---
                if world_state.event_queue:
                    # We wrap the call to process_next to handle task tracking
                    task = asyncio.create_task(self.cognitive.process_next(world_state))
                    self.cognitive.active_tasks.add(task)
                    # Clean up done tasks
                    task.add_done_callback(self.cognitive.active_tasks.discard)

            except Exception as e:
                # Reflex Loop Failure is CRITICAL
                print(f"CRITICAL: Reflex Loop Failure: {e}")
                # In a production app, we might try to recover or just exit
                # For now, let's log and keep trying if possible, or stop.
                # The README says "Log immediately and exit."
                self.running = False
                raise e

            # --- 3. SLEEP ---
            await self.scheduler.sleep_until_next_tick(start_time)

    