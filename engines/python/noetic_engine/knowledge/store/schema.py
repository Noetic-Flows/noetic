from __future__ import annotations
from typing import Dict, List, Optional, Any, Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

class Entity(BaseModel):
    id: UUID
    type: str
    attributes: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

class Fact(BaseModel):
    id: UUID
    subject_id: UUID
    predicate: str
    object_entity_id: Optional[UUID] = None
    object_literal: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_type: Literal["axiom", "doc", "web", "inference"] = "inference"
    valid_from: datetime
    valid_until: Optional[datetime] = None

    @property
    def current_confidence(self) -> float:
        """Applies time-decay logic."""
        if self.source_type == "axiom": return 1.0
        # Calculate age in hours
        now = datetime.utcnow()
        # If valid_from is naive, assume utc. If aware, ensure compatibility.
        # Assuming naive UTC for now as per other code.
        if self.valid_from > now: return self.confidence
        age_hours = (now - self.valid_from).total_seconds() / 3600
        # Decay factor: 10% loss every 24 hours -> 0.9 every 24h
        decay = 0.9 ** (age_hours / 24)
        return self.confidence * decay

class Event(BaseModel):
    id: UUID
    type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime

class WorldState(BaseModel):
    tick: int
    entities: Dict[UUID, Entity]
    facts: List[Fact]
    event_queue: List[Event] = Field(default_factory=list)
    # active_goals: List[Goal]