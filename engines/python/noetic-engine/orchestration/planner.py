import heapq
from typing import List, Dict, Any, Set, Tuple, Optional
from .schema import Plan, PlanStep, Goal, Action
from .agents import AgentContext
from .principles import PrincipleEngine
from noetic_engine.knowledge import WorldState
from noetic_engine.skills.registry import SkillRegistry
from noetic_engine.skills.interfaces import Skill

class Planner:
    """
    Goal-Oriented Action Planner (GOAP) implementation.
    """
    def __init__(self, skill_registry: SkillRegistry, principle_engine: Optional[PrincipleEngine] = None):
        self.registry = skill_registry
        self.principle_engine = principle_engine or PrincipleEngine()

    async def generate_plan(self, agent: AgentContext, goal: Goal, state: WorldState) -> Plan:
        """
        Generates a sequence of Actions (Plan) to reach the Goal from the current WorldState,
        respecting the Agent's Principles and Skills.
        """
        # 1. Init
        start_state = self._extract_state(state)
        target_state = goal.target_state
        
        # Priority Queue: (f_score, g_score, state_frozen, path)
        # state_frozen is frozenset of items for hashing
        
        start_frozen = frozenset(start_state.items())
        
        queue = []
        heapq.heappush(queue, (0, 0, start_frozen, []))
        
        visited = set()
        
        # 2. Search
        while queue:
            f, g, current_frozen, path = heapq.heappop(queue)
            current_dict = dict(current_frozen)
            
            if current_frozen in visited:
                continue
            visited.add(current_frozen)
            
            # Check Goal
            if self._satisfies(current_dict, target_state):
                return self._construct_plan(path, g)
            
            # Explore Neighbors (Skills)
            # Filter skills allowed for this agent
            available_skills = [
                self.registry.get_skill(sid) 
                for sid in agent.allowed_skills 
                if self.registry.get_skill(sid)
            ]
            
            for skill in available_skills:
                # Type check to ensuring we are working with a Skill object
                if skill and self._satisfies(current_dict, skill.preconditions):
                    # Apply effects
                    new_dict = current_dict.copy()
                    new_dict.update(skill.postconditions)
                    new_frozen = frozenset(new_dict.items())
                    
                    # Calculate Cost
                    base_cost = 1.0
                    moral_cost = 0.0
                    
                    # Create candidate action for principle evaluation
                    # We assume empty params for planning phase or default
                    candidate_action = Action(skill_id=skill.id, params={})
                    
                    if self.principle_engine:
                        moral_cost = self.principle_engine.evaluate_cost(
                            candidate_action, 
                            new_dict, # Use resultant state for evaluation? Or current? Usually resultant.
                            agent.principles
                        )
                    
                    new_g = g + base_cost + moral_cost
                    h = self._heuristic(new_dict, target_state)
                    
                    new_path = path + [skill]
                    heapq.heappush(queue, (new_g + h, new_g, new_frozen, new_path))
                    
        # Return empty plan if no path found (or maybe a 'Wait' plan?)
        return Plan(steps=[], total_cost=0.0)

    def _extract_state(self, world_state: WorldState) -> Dict[str, Any]:
        # Map facts to a simple KV store
        # Key format: "{subject_id}:{predicate}" or just "predicate" if subject is implied?
        # Ideally, we map Fact(sub, pred, obj) -> "sub:pred": obj
        state = {}
        for fact in world_state.facts:
            key = f"{fact.subject_id}:{fact.predicate}"
            val = fact.object_literal if fact.object_literal else str(fact.object_entity_id)
            state[key] = val
            
            # For simpler testing where goal keys might omit UUIDs:
            # We might want to support "fuzzy" matching, but for now strict.
        return state

    def _satisfies(self, state: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        for k, v in conditions.items():
            if state.get(k) != v:
                return False
        return True

    def _heuristic(self, state: Dict[str, Any], goal: Dict[str, Any]) -> float:
        # Count unsatisfied conditions
        cost = 0.0
        for k, v in goal.items():
            if state.get(k) != v:
                cost += 1.0
        return cost

    def _construct_plan(self, skills: List[Skill], cost: float) -> Plan:
        steps = []
        for skill in skills:
            steps.append(PlanStep(
                skill_id=skill.id,
                params={}, # We assume fixed params or derived from context in real GOAP
                cost=1.0,
                rationale=f"Achieves {skill.postconditions}"
            ))
        return Plan(steps=steps, total_cost=cost)
