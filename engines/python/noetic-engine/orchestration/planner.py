from typing import List, Any
from pydantic import BaseModel
from noetic-engine.knowledge import WorldState
from .agents import AgentContext

class PlanStep(BaseModel):
    skill_id: str
    params: dict

class Plan(BaseModel):
    steps: List[PlanStep]

class Planner:
    async def generate_plan(self, agent: AgentContext, goal: str, state: WorldState) -> Plan:
        # TODO: Implement GOAP / A* logic
        return Plan(steps=[])
