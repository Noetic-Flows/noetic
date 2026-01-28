from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class EntityType(str, Enum):
    """
    Fundamental kinds of things that can exist in the Noetic Universe.
    """
    AGENT = "agent"
    TASK = "task"
    DOCUMENT = "document"
    CONCEPT = "concept"
    EVENT = "event"
    TOOL = "tool"

class RelationType(str, Enum):
    """
    Allowed edges in the Knowledge Graph.
    """
    CREATED = "created"
    MODIFIED = "modified"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    SUBTASK_OF = "subtask_of"
    MENTIONS = "mentions"
    EVENT = "event"

class Ontology(BaseModel):
    """
    The Shared Semantic Environment (SSE) enforces this schema.
    It acts as the 'Physics' of the Noetic world.
    """
    version: str = "0.1.0"
    allowed_types: List[EntityType] = list(EntityType)
    allowed_relations: List[RelationType] = list(RelationType)
    
    def validate_triple(self, subject_type: str, predicate: str, object_type: str) -> bool:
        """
        Validates if a subject-predicate-object triple is allowable.
        """
        # TODO: Implement strict validation logic (e.g., Tasks can DEPEND_ON Tasks, but Documents cannot DEPEND_ON Concepts)
        return True
