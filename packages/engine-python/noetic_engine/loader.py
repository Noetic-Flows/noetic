import json
import logging
from noetic_engine.runtime.engine import NoeticEngine
from noetic_lang.core import AgentDefinition as AgentContext
from noetic_conscience import Principle
from noetic_stage import Component
from noetic_stage.schema import parse_component
from noetic_engine.skills.library.system.control import PlaceholderSkill

logger = logging.getLogger(__name__)

class CodexIntegrityError(Exception):
    """
    Raised when a Codex file contains invalid references or malformed definitions.
    """
    pass

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

        # 0.5 Load Initial Knowledge
        knowledge_data = data.get("knowledge", {})
        initial_state = knowledge_data.get("initial_state", [])
        for fact_def in initial_state:
            try:
                import uuid
                # Simple mapper: [subject_id, predicate, object]
                if isinstance(fact_def, list) and len(fact_def) == 3:
                    sub_id, pred, obj = fact_def
                    # Generate deterministic UUID for named entities if they aren't UUIDs
                    try:
                        u_sub = uuid.UUID(sub_id)
                    except ValueError:
                        u_sub = uuid.uuid5(uuid.NAMESPACE_DNS, sub_id)
                    
                    # Infer type from prefix
                    subject_type = "Project" if sub_id.startswith("project.") else "unknown"
                    
                    if isinstance(obj, str) and obj.startswith("entity:"):
                        # Object is an entity reference
                        obj_entity_name = obj.replace("entity:", "")
                        u_obj = uuid.uuid5(uuid.NAMESPACE_DNS, obj_entity_name)
                        engine.knowledge.ingest_fact(u_sub, pred, object_entity_id=u_obj, subject_type=subject_type)
                    else:
                        # Object is a literal
                        engine.knowledge.ingest_fact(u_sub, pred, object_literal=str(obj), subject_type=subject_type)
                    
                    # Also ensure the entity has a 'name' attribute for easier binding lookup
                    engine.knowledge.ingest_fact(u_sub, "name", object_literal=sub_id, subject_type=subject_type)
            except Exception as e:
                logger.error(f"Failed to load initial fact {fact_def}: {e}")

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

        # 1.5 Load Principles (Store them for agent lookup)
        orchestration = data.get("orchestration", {})
        principles_data = orchestration.get("principles", [])
        principles_map = {}
        for p_def in principles_data:
            try:
                p = Principle(**p_def)
                principles_map[p.id] = p
            except Exception as e:
                logger.error(f"Failed to parse principle {p_def.get('id')}: {e}")

        # 2. Load Agents
        # Support legacy root agents or new orchestration.agents
        agents = data.get("agents", [])
        if not agents:
            agents = orchestration.get("agents", [])

        for agent_data in agents:
            try:
                # Adapter for Spec -> Internal Model
                if "persona" in agent_data and "system_prompt" not in agent_data:
                    agent_data["system_prompt"] = agent_data["persona"].get("backstory", "")
                
                # Integrity Check: Skills
                allowed_skills = agent_data.get("allowed_skills", [])
                for skill_id in allowed_skills:
                    if not engine.skills.get_skill(skill_id):
                        raise CodexIntegrityError(f"Agent '{agent_data.get('id')}' references missing skill: {skill_id}")

                # Principle Resolution: ID List -> Object List
                p_ids = agent_data.get("principles", [])
                resolved_principles = []
                for p_id in p_ids:
                    if isinstance(p_id, str):
                        if p_id in principles_map:
                            resolved_principles.append(principles_map[p_id])
                        else:
                            raise CodexIntegrityError(f"Agent '{agent_data.get('id')}' references missing principle: {p_id}")
                    else:
                        # Already an object? (unlikely in JSON but for robustness)
                        resolved_principles.append(p_id)
                
                agent_data["principles"] = resolved_principles

                # Adapter: Convert Lang Model -> Stdlib Model
                from noetic_stdlib.agents.base import AgentDefinition as RuntimeAgentDef
                from noetic_stdlib.agents.local import LocalAgent

                agent_def = AgentContext(**agent_data) # RESTORED: Create Context first

                runtime_def = RuntimeAgentDef(
                    id=agent_def.id,
                    name=agent_def.id, # Map ID to Name if Name missing
                    description="Loaded from Codex",
                    allowed_tools=agent_def.allowed_skills, # Map skills to tools
                    system_prompt=agent_def.system_prompt
                )
                
                # Instantiate Concrete Agent (LocalAgent for generic runner)
                agent_instance = LocalAgent(definition=runtime_def)
                engine.mesh.register_agent(agent_instance)
                logger.info(f"Loaded Agent: {agent_def.id}")
            except CodexIntegrityError as e:
                logger.error(f"Integrity Error: {e}")
                raise e
            except Exception as e:
                logger.error(f"Failed to parse agent: {e}")
                raise e

        # 2. Load Canvas
        canvas_data = data.get("canvas", {})
        if canvas_data:
            try:
                if "templates" in canvas_data:
                    # TODO: Implement A2UI Template hydration
                    logger.warning("Canvas templates found but not yet supported. Skipping root render.")
                
                root_def = canvas_data.get("root")
                if root_def:
                    root = parse_component(root_def)
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
