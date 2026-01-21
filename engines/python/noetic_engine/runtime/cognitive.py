import asyncio
import logging
from noetic_engine.knowledge import KnowledgeStore, WorldState
from noetic_engine.skills import SkillRegistry, SkillContext
from noetic_engine.orchestration import Planner, AgentContext, Goal, PlanStep, AgentManager

logger = logging.getLogger(__name__)

class CognitiveSystem:
    """
    Manages the 'Cognitive Loop' (System 2) - Planning and Decision Making.
    Running asynchronously from the UI loop.
    """
    def __init__(self, knowledge: KnowledgeStore, skills: SkillRegistry, planner: Planner, agent_manager: AgentManager):
        self.knowledge = knowledge
        self.skills = skills
        self.planner = planner
        self.agent_manager = agent_manager
        self.active_tasks = set()

    async def process_next(self, state: WorldState):
        """
        Called when the Reflex loop detects a Trigger (Event).
        Decides what to do.
        """
        if not state.event_queue:
            return

        event = state.event_queue[0] 
        logger.info(f"Cognitive System processing event: {event.type}")
        
        agent_ids = list(self.agent_manager.agents.keys())
        if not agent_ids:
            logger.warning("No agents registered to handle event.")
            return

        agent = self.agent_manager.get(agent_ids[0])
        
        # Simple heuristic: if we have a test-event, we want to 'wait'
        target = {"done": True} if event.type == "test-event" else {}
        goal = Goal(description=f"Handle event {event.type}", target_state=target)
        
        plan = await self.planner.generate_plan(agent, goal, state)
        
        for step in plan.steps:
            await self._execute_step(step, agent)

    async def _execute_step(self, step: PlanStep, agent: AgentContext):
        skill = self.skills.get_skill(step.skill_id)
        if not skill:
            logger.error(f"Skill not found: {step.skill_id}")
            return

        if step.skill_id not in agent.allowed_skills:
            logger.warning(f"Agent {agent.id} not allowed to use {step.skill_id}")

        context = SkillContext(agent_id=agent.id, store=self.knowledge)
        logger.info(f"Executing Skill: {step.skill_id}")
        
        try:
            result = await skill.execute(context, **step.params)
            logger.info(f"Skill Result: {result}")
        except Exception as e:
            logger.error(f"Skill execution failed: {e}")
