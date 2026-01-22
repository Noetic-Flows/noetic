import heapq
from typing import List, Dict, Any, Set, Tuple, Optional
from noetic_lang.core import Plan, PlanStep, Goal, Action
from noetic_lang.core import AgentDefinition as AgentContext
from noetic_lang.core.stanza import StanzaDefinition
from noetic_knowledge.working.stack import MemoryStack
from noetic_conscience import Evaluator, JudgementContext, JudgementResult, PolicyViolationError
from noetic_knowledge import WorldState
from noetic_engine.skills.registry import SkillRegistry
from noetic_engine.skills.interfaces import Skill

class Planner:
    """
    Goal-Oriented Action Planner (GOAP) implementation.
    """
    def __init__(self, skill_registry: Optional[SkillRegistry] = None, evaluator: Optional[Evaluator] = None):
        self.registry = skill_registry or SkillRegistry()
        self.evaluator = evaluator or Evaluator()

    async def create_plan(self, stanza: StanzaDefinition, stack: MemoryStack) -> Plan:
        steps = []
        for step_def in stanza.steps:
            steps.append(PlanStep(
                skill_id="basic_execution", # Placeholder skill
                params={"instruction": step_def.instruction},
                instruction=step_def.instruction,
                cost=1.0
            ))
        return Plan(steps=steps, total_cost=float(len(steps)))

    async def generate_plan(self, agent: AgentContext, goal: Goal, state: WorldState) -> Plan:
        """
        Generates a sequence of Actions (Plan) to reach the Goal from the current WorldState,
        respecting the Agent's Principles and Skills.
        """
        # 1. Init
        start_state = self._extract_state(state, agent.id)
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
                    
                    if self.evaluator:
                        try:
                            ctx = JudgementContext(
                                agent_id=agent.id,
                                action_id=skill.id,
                                action_args={},
                                tags=[], # TODO: Get tags from skill definition
                                world_state=new_dict
                            )
                            judgement = self.evaluator.judge(ctx, agent.principles)
                            moral_cost = judgement.cost
                        except PolicyViolationError:
                            # Hard veto -> Path blocked
                            continue
                    
                    new_g = g + base_cost + moral_cost
                    h = self._heuristic(new_dict, target_state)
                    
                    new_path = path + [skill]
                    heapq.heappush(queue, (new_g + h, new_g, new_frozen, new_path))
                    
        # Return empty plan if no path found (or maybe a 'Wait' plan?)
        return Plan(steps=[], total_cost=0.0)

    def _extract_state(self, world_state: WorldState, agent_id: str = None) -> Dict[str, Any]:
        # Map facts to a simple KV store
        # Key format: "{subject_id}:{predicate}" or just "predicate" if subject is implied?
        # Ideally, we map Fact(sub, pred, obj) -> "sub:pred": obj
        state = {}
        for fact in world_state.facts:
            # Full canonical key
            key = f"{fact.subject_id}:{fact.predicate}"
            val = fact.object_literal if fact.object_literal else str(fact.object_entity_id)
            state[key] = val
            
            # Simplified key for Agent's own state
            if agent_id and str(fact.subject_id) == agent_id:
                state[fact.predicate] = val
            
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