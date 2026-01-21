from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import create_engine, select, and_, or_
from sqlalchemy.orm import sessionmaker, Session
import chromadb
from chromadb.config import Settings
import networkx as nx

# Import Models (DB Layer)
from .models import Base, EntityModel, FactModel, TagModel

# Import Schema (API Layer)
from .schema import WorldState, Entity, Fact

class KnowledgeStore:
    def __init__(self, db_url: str = "sqlite:///:memory:", vector_db_path: Optional[str] = None, collection_name: str = "knowledge_facts"):
        self.db_url = db_url
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Initialize DB (Auto-migration for now)
        Base.metadata.create_all(bind=self.engine)
        
        # Initialize ChromaDB
        if vector_db_path:
            self.chroma_client = chromadb.PersistentClient(path=vector_db_path)
        else:
            self.chroma_client = chromadb.EphemeralClient()
            
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)

        # Initialize Graph Cache
        self.graph = nx.MultiDiGraph()
        self._load_graph_cache()

    def _get_session(self) -> Session:
        return self.SessionLocal()
    
    def _load_graph_cache(self):
        """Loads all currently active facts into the NetworkX graph."""
        state = self.get_world_state()
        self.graph.clear()
        for fact in state.facts:
            self._add_fact_to_graph(fact)

    def _add_fact_to_graph(self, fact: Fact):
        """Helper to add a single fact to the NetworkX graph."""
        # Nodes are UUIDs (subject_id) or strings (if we want literal nodes? for now just subjects)
        # Edges store the predicate and object info
        
        # If object is an entity, it's an edge to that entity
        # If object is literal, we might store it as node attribute or specific literal node?
        # For pathfinding, we usually care about Entity-Entity relations.
        
        if fact.object_entity_id:
            self.graph.add_edge(
                fact.subject_id, 
                fact.object_entity_id, 
                key=fact.id,
                predicate=fact.predicate, 
                weight=1.0 # Default weight, can be modified by principles
            )
        else:
            # For literals, maybe we just add it as data to the subject node? 
            # Or a special edge to a literal node?
            # Let's add an edge to a literal node identifier for completeness, 
            # though pathfinding usually doesn't traverse literals.
            literal_node_id = f"literal:{fact.object_literal}"
            self.graph.add_edge(
                fact.subject_id,
                literal_node_id,
                key=fact.id,
                predicate=fact.predicate,
                weight=1.0
            )

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
                subject = EntityModel(id=subject_id, type="unknown")
                session.add(subject)
            
            # 2. Check for Existing Active Fact (Same Subject, Predicate, Object)
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
                return self._map_fact_model_to_schema(existing_exact_fact)

            # 3. Check for Contradictions
            contradiction_stmt = select(FactModel).where(
                FactModel.subject_id == subject_id,
                FactModel.predicate == predicate,
                FactModel.valid_until.is_(None)
            )
            
            existing_contradictions = session.execute(contradiction_stmt).scalars().all()
            
            for old_fact in existing_contradictions:
                old_fact.valid_until = now
                session.add(old_fact)
                # Remove from Graph Cache
                # (NetworkX remove_edge requires u, v, key usually. We might need to look it up or rebuild)
                # Rebuilding might be slow. Removing by key is better if possible.
                # Since we don't track old object here easily without loading it, let's just rebuild or handle smartly.
                # Actually we have old_fact.
                try:
                    target = old_fact.object_entity_id if old_fact.object_entity_id else f"literal:{old_fact.object_literal}"
                    if self.graph.has_edge(old_fact.subject_id, target, key=old_fact.id):
                        self.graph.remove_edge(old_fact.subject_id, target, key=old_fact.id)
                except Exception:
                    pass # safe ignore if graph out of sync
                
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
            
            fact_schema = self._map_fact_model_to_schema(new_fact)

            # 5. Ingest into ChromaDB
            # Text representation: "Subject predicate Object"
            obj_str = str(object_entity_id) if object_entity_id else str(object_literal)
            doc_text = f"Fact: {predicate} {obj_str}" # Focus on predicate and object for search
            
            metadata = {
                "subject_id": str(subject_id),
                "predicate": predicate,
                "object": obj_str,
                "type": "fact",
                "valid_from": now.isoformat()
            }
            
            self.collection.add(
                documents=[doc_text],
                metadatas=[metadata],
                ids=[str(new_fact.id)]
            )
            
            # 6. Update Graph Cache
            self._add_fact_to_graph(fact_schema)
            
            return fact_schema
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
    def hybrid_search(self, query: str, limit: int = 5) -> List[Fact]:
        """
        Performs a hybrid search:
        1. Semantic search in ChromaDB.
        2. Filters results for validity in SQL (or just by checking valid_until via ID lookup).
        """
        # 1. Search Chroma
        results = self.collection.query(
            query_texts=[query],
            n_results=limit * 2 # Fetch more to account for invalid ones
        )
        
        if not results['ids'] or not results['ids'][0]:
            return []
            
        candidate_ids = results['ids'][0]
        
        # 2. Hydrate & Filter from SQL
        # We need to fetch these IDs and check if they are still valid.
        session = self._get_session()
        try:
            # Convert string IDs back to UUIDs
            uuid_ids = [UUID(id_str) for id_str in candidate_ids]
            
            stmt = select(FactModel).where(
                FactModel.id.in_(uuid_ids),
                FactModel.valid_until.is_(None) # Only active facts
            )
            
            valid_models = session.execute(stmt).scalars().all()
            return [self._map_fact_model_to_schema(m) for m in valid_models]
            
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