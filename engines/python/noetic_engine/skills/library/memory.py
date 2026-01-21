import uuid
from typing import Any, Optional
from noetic_engine.skills.interfaces import Skill, SkillResult, SkillContext

class MemorizeSkill(Skill):
    id = "skill.memory.memorize"
    description = "Saves a fact to the long-term knowledge store."
    schema = {
        "type": "object",
        "properties": {
            "subject_id": {"type": "string"},
            "predicate": {"type": "string"},
            "object_entity_id": {"type": "string"},
            "object_literal": {"type": "string"}
        },
        "required": ["subject_id", "predicate"]
    }

    async def execute(self, context: SkillContext, subject_id: str, predicate: str, object_entity_id: Optional[str] = None, object_literal: Optional[str] = None, **kwargs) -> SkillResult:
        if not context.store:
            return SkillResult(success=False, error="KnowledgeStore not available in context.")

        try:
            # Convert strings to UUIDs where necessary
            sub_uuid = uuid.UUID(subject_id)
            obj_uuid = uuid.UUID(object_entity_id) if object_entity_id else None
            
            fact = context.store.ingest_fact(
                subject_id=sub_uuid,
                predicate=predicate,
                object_entity_id=obj_uuid,
                object_literal=object_literal
            )
            
            return SkillResult(
                success=True,
                data={"fact_id": str(fact.id)},
                cost=0.1
            )
        except Exception as e:
            return SkillResult(success=False, error=str(e))

class RecallSkill(Skill):
    id = "skill.memory.recall"
    description = "Retrieves facts relevant to a query from knowledge."
    schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 5}
        },
        "required": ["query"]
    }

    async def execute(self, context: SkillContext, query: str, limit: int = 5, **kwargs) -> SkillResult:
        if not context.store:
            return SkillResult(success=False, error="KnowledgeStore not available in context.")

        try:
            facts = context.store.hybrid_search(query=query, limit=limit)
            # Serialize facts for return
            data = [fact.model_dump() for fact in facts] if hasattr(facts[0], "model_dump") else facts
            
            return SkillResult(
                success=True,
                data=data,
                cost=0.1
            )
        except Exception as e:
            return SkillResult(success=False, error=str(e))
