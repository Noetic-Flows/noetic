from __future__ import annotations
from typing import Dict, List, Optional, Any
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
    confidence: float = 1.0
    valid_from: datetime
    valid_until: Optional[datetime] = None

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