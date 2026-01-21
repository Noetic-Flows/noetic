import json
import logging
from noetic_engine.runtime import NoeticEngine
from noetic_engine.orchestration import AgentContext
from noetic_engine.canvas import Component
from noetic_engine.skills.library.system.control import PlaceholderSkill

logger = logging.getLogger(__name__)

class NoeticLoader:
    def load(self, engine: NoeticEngine, codex_path: str):
        """
        Hydrates the engine with the definitions from a .noetic Codex file.
        """
        try:
            with open(codex_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Codex file: {e}")
            return

        # 1. Load Skills (Load these first so Agents can reference them)
        skills_data = data.get("skills", [])
        for skill_def in skills_data:
            try:
                # If skill already exists (e.g. system skill), skip or update?
                # For now, we only register if missing, using Placeholder
                skill_id = skill_def.get("id")
                if not engine.skills.get_skill(skill_id):
                    skill = PlaceholderSkill(
                        id=skill_id,
                        description=skill_def.get("description", ""),
                        type=skill_def.get("type", "custom")
                    )
                    engine.skills.register(skill)
                    logger.info(f"Loaded (Placeholder) Skill: {skill_id}")
            except Exception as e:
                logger.error(f"Failed to parse skill: {e}")

        # 2. Load Agents
        # Support legacy root agents or new orchestration.agents
        agents = data.get("agents", [])
        if not agents:
            orchestration = data.get("orchestration", {})
            agents = orchestration.get("agents", [])

        for agent_data in agents:
            try:
                # Adapter for Spec -> Internal Model
                if "persona" in agent_data and "system_prompt" not in agent_data:
                    agent_data["system_prompt"] = agent_data["persona"].get("backstory", "")
                
                # Adapter for skills (list of strings vs objects?)
                # Spec says "skills": ["skill.weather.get"] which is list of strings.
                # AgentContext expects allowed_skills: List[str]. So this matches.

                agent = AgentContext(**agent_data)
                engine.agent_manager.register(agent)
                logger.info(f"Loaded Agent: {agent.id}")
            except Exception as e:
                logger.error(f"Failed to parse agent: {e}")

        # 2. Load Canvas
        canvas_data = data.get("canvas")
        if canvas_data:
            try:
                if "templates" in canvas_data:
                    # TODO: Implement A2UI Template hydration
                    logger.warning("Canvas templates found but not yet supported. Skipping root render.")
                else:
                    root = Component(**canvas_data)
                    engine.reflex.set_root(root)
                    logger.info("Loaded Canvas definition")
            except Exception as e:
                logger.error(f"Failed to parse canvas: {e}")
        
        # 3. Load Flows
        orchestration = data.get("orchestration", {})
        flows = orchestration.get("flows", [])
        for flow_data in flows:
            try:
                engine.flow_manager.register(flow_data)
                logger.info(f"Loaded Flow: {flow_data.get('id')}")
            except Exception as e:
                logger.error(f"Failed to parse flow: {e}")