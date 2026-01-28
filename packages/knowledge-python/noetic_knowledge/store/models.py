from __future__ import annotations
from typing import Optional, Any
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class EntityModel(Base):
    __tablename__ = "entities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    type: Mapped[str] = mapped_column(String, nullable=False)
    attributes: Mapped[dict] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    facts_as_subject = relationship("FactModel", foreign_keys="[FactModel.subject_id]", back_populates="subject")
    facts_as_object = relationship("FactModel", foreign_keys="[FactModel.object_entity_id]", back_populates="object_entity")

class FactModel(Base):
    __tablename__ = "facts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("entities.id"), nullable=False)
    predicate: Mapped[str] = mapped_column(String, nullable=False)
    object_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("entities.id"), nullable=True)
    object_literal: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    # salience: Mapped[float] = mapped_column(Float, default=0.0) # Duplicate? I see I added it before.
    # Note: View file showed salience on line 33. I should preserve it.
    salience: Mapped[float] = mapped_column(Float, default=0.0)
    source_type: Mapped[str] = mapped_column(String, default="inference")
    
    # Temporal Columns
    valid_from: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    subject = relationship("EntityModel", foreign_keys=[subject_id], back_populates="facts_as_subject")
    object_entity = relationship("EntityModel", foreign_keys=[object_entity_id], back_populates="facts_as_object")

class SkillModel(Base):
    __tablename__ = "skills"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    trigger_condition: Mapped[str] = mapped_column(Text, nullable=False)
    steps: Mapped[list] = mapped_column(JSON, default=list) 
    success_rate: Mapped[float] = mapped_column(Float, default=0.5)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
