from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Any, Optional, Dict, Literal
from pydantic import BaseModel, Field
from .ontology import EntityType, RelationType

class Entity(BaseModel):
    """
    A persistent entity in the Knowledge Graph.
    """
    id: UUID = Field(default_factory=uuid4)
    type: EntityType
    attributes: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Fact(BaseModel):
    """
    An atomic unit of knowledge (Subject -> Predicate -> Object).
    """
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    salience: float = 0.0  # 0.0 to 1.0 importance score
    
    subject_id: str # UUID string
    subject_type: EntityType
    predicate: RelationType
    object_literal: Optional[str] = None
    object_id: Optional[str] = None # UUID string
    
    # Metadata for Validity & Confidence
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_type: Literal["axiom", "doc", "web", "inference", "user"] = "inference"
    valid_from: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None

    @property
    def current_confidence(self) -> float:
        """Applies time-decay logic based on source type."""
        if self.source_type == "axiom": return 1.0
        
        now = datetime.utcnow()
        if self.valid_from > now: return self.confidence
        
        # Calculate age in hours
        age_hours = (now - self.valid_from).total_seconds() / 3600
        
        # Decay factor: 10% loss every 24 hours -> 0.9 every 24h
        # This is a tunable parameter for the "Forgetting Curve"
        decay = 0.9 ** (age_hours / 24.0)
        return self.confidence * decay

class MemoryFrame(BaseModel):
    """
    A specific context of execution (e.g., a function call, a task step).
    Maps to the 'Stack' in AgentProg.
    """
    id: UUID = Field(default_factory=uuid4)
    parent_id: Optional[UUID] = None
    goal: str
    
    # The Local Scope (Garbage Collected on pop)
    local_vars: Dict[str, Any] = Field(default_factory=dict)
    scratchpad: List[str] = Field(default_factory=list)
    
    # The Return Value (Promoted to Heap)
    return_value: Any = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Skill(BaseModel):
    """
    A consolidated procedural memory (How-To).
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    trigger_condition: str  # Vector embedding target text
    steps: List[str]
    success_rate: float = 0.5
    created_at: datetime = Field(default_factory=datetime.utcnow)
    usage_count: int = 0
