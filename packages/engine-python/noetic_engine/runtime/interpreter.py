from typing import Any, Protocol
from noetic_lang.core.stanza import StanzaDefinition
from noetic_knowledge.working.stack import MemoryStack
from noetic_lang.core import PlanStep

class PlannerProtocol(Protocol):
    async def create_plan(self, stanza: StanzaDefinition, stack: MemoryStack) -> Any:
        ...

class ExecutorProtocol(Protocol):
    async def execute_step(self, step: PlanStep, stack: MemoryStack) -> Any:
        ...

class Interpreter:
    def __init__(self, stack: MemoryStack, planner: PlannerProtocol, executor: ExecutorProtocol):
        self.stack = stack
        self.planner = planner
        self.executor = executor

    async def execute_stanza(self, stanza: StanzaDefinition) -> Any:
        # 1. Push Frame
        self.stack.push_frame(goal=stanza.description, context={"stanza_id": stanza.id})
        
        try:
            # 2. Plan
            plan = await self.planner.create_plan(stanza, self.stack)
            
            # 3. Execute Loop
            results = []
            for step in plan.steps:
                res = await self.executor.execute_step(step, self.stack)
                results.append(res)
                
            return results
        finally:
            # 4. Pop Frame
            self.stack.pop_frame()