from __future__ import annotations
from typing import Optional, Any
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Text
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
    
    # Temporal Columns
    valid_from: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    subject = relationship("EntityModel", foreign_keys=[subject_id], back_populates="facts_as_subject")
    object_entity = relationship("EntityModel", foreign_keys=[object_entity_id], back_populates="facts_as_object")

class TagModel(Base):
    __tablename__ = "tags"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
