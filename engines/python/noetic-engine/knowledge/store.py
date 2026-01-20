from typing import Optional, List, Dict
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import create_engine, select, and_, or_
from sqlalchemy.orm import sessionmaker, Session

# Import Models (DB Layer)
from .models import Base, EntityModel, FactModel, TagModel

# Import Schema (API Layer)
from .schema import WorldState, Entity, Fact

class KnowledgeStore:
    def __init__(self, db_url: str = "sqlite:///:memory:"):
        self.db_url = db_url
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Initialize DB (Auto-migration for now)
        Base.metadata.create_all(bind=self.engine)
        
        # TODO: Initialize ChromaDB client here
        # self.chroma_client = chromadb.PersistentClient(...)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    def ingest_fact(self, subject_id: UUID, predicate: str, object_entity_id: Optional[UUID] = None, object_literal: Optional[str] = None) -> Fact:
        """
        Ingests a fact into the knowledge graph.
        Handles temporal validity and contradictions.
        """
        session = self._get_session()
        try:
            now = datetime.utcnow()
            
            # 1. Check if the Subject Entity exists
            subject = session.execute(select(EntityModel).where(EntityModel.id == subject_id)).scalar_one_or_none()
            if not subject:
                # Auto-create entity if it doesn't exist? 
                # The prompt implies we might need to be explicit, but for robustness let's auto-create stub
                # In a real system, we might want to fail or require type info.
                # Let's assume generic "Entity" type for auto-created ones.
                subject = EntityModel(id=subject_id, type="unknown")
                session.add(subject)
            
            # 2. Check for Existing Active Fact (Same Subject, Predicate, Object)
            # We want to see if this exact relation is already true.
            stmt = select(FactModel).where(
                FactModel.subject_id == subject_id,
                FactModel.predicate == predicate,
                FactModel.valid_until.is_(None)
            )
            
            if object_entity_id:
                stmt = stmt.where(FactModel.object_entity_id == object_entity_id)
            else:
                stmt = stmt.where(FactModel.object_literal == object_literal)
                
            existing_exact_fact = session.execute(stmt).scalar_one_or_none()
            
            if existing_exact_fact:
                # Fact already exists and is active. 
                # We could update confidence or just return it.
                # For now, just return the mapped schema object.
                return self._map_fact_model_to_schema(existing_exact_fact)

            # 3. Check for Contradictions (Same Subject, Predicate, BUT DIFFERENT Object)
            # e.g. (User, status, happy) vs (User, status, sad)
            # Only if the predicate implies uniqueness (Functional Property).
            # For this reference implementation, let's assume ALL predicates are functional 
            # (one value per subject-predicate pair) for simplicity, 
            # OR we just add it as a new fact if it's a multi-value property.
            
            # The README says: "Check for Contradictions... If contradiction found: Update the old fact's valid_until"
            # This implies functional properties.
            
            contradiction_stmt = select(FactModel).where(
                FactModel.subject_id == subject_id,
                FactModel.predicate == predicate,
                FactModel.valid_until.is_(None)
            )
            
            existing_contradictions = session.execute(contradiction_stmt).scalars().all()
            
            for old_fact in existing_contradictions:
                old_fact.valid_until = now
                session.add(old_fact)
                
            # 4. Insert New Fact
            new_fact = FactModel(
                subject_id=subject_id,
                predicate=predicate,
                object_entity_id=object_entity_id,
                object_literal=object_literal,
                valid_from=now,
                valid_until=None
            )
            session.add(new_fact)
            session.commit()
            session.refresh(new_fact)
            
            # TODO: Ingest into ChromaDB here
            
            return self._map_fact_model_to_schema(new_fact)
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_world_state(self, snapshot_time: Optional[datetime] = None) -> WorldState:
        """
        Retrieves the state of the world at a specific point in time.
        """
        if snapshot_time is None:
            snapshot_time = datetime.utcnow()
            
        session = self._get_session()
        try:
            # Fetch Active Entities (those that are part of any active fact or just exist?)
            # Usually we want all entities.
            # TODO: Add valid_from/until to Entities if we want to track their existence lifespan.
            # For now, just get all entities.
            entities_models = session.execute(select(EntityModel)).scalars().all()
            entities_map = {e.id: self._map_entity_model_to_schema(e) for e in entities_models}
            
            # Fetch Active Facts
            # valid_from <= snapshot_time AND (valid_until IS NULL OR valid_until > snapshot_time)
            facts_stmt = select(FactModel).where(
                FactModel.valid_from <= snapshot_time,
                or_(
                    FactModel.valid_until.is_(None),
                    FactModel.valid_until > snapshot_time
                )
            )
            facts_models = session.execute(facts_stmt).scalars().all()
            facts_list = [self._map_fact_model_to_schema(f) for f in facts_models]
            
            return WorldState(
                tick=int(snapshot_time.timestamp() * 60), # Approx tick count
                entities=entities_map,
                facts=facts_list
            )
            
        finally:
            session.close()

    def _map_fact_model_to_schema(self, model: FactModel) -> Fact:
        return Fact(
            id=model.id,
            subject_id=model.subject_id,
            predicate=model.predicate,
            object_entity_id=model.object_entity_id,
            object_literal=model.object_literal,
            confidence=model.confidence,
            valid_from=model.valid_from,
            valid_until=model.valid_until
        )

    def _map_entity_model_to_schema(self, model: EntityModel) -> Entity:
        return Entity(
            id=model.id,
            type=model.type,
            attributes=model.attributes,
            created_at=model.created_at,
            updated_at=model.updated_at
        )