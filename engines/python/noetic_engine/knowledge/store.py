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
    def __init__(self, db_url: str = "sqlite:///noetic.db", vector_db_path: Optional[str] = None, collection_name: str = "knowledge_facts"):
        self.db_url = db_url
        # Use StaticPool for in-memory if requested, but file-based is safer for concurrency
        if db_url == "sqlite:///:memory:":
            from sqlalchemy.pool import StaticPool
            self.engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False}, poolclass=StaticPool)
        else:
            self.engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False})
        
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

    from contextlib import contextmanager
    @contextmanager
    def transaction(self):
        """
        Atomic transaction context manager for SQL and Vector stores.
        """
        session = self._get_session()
        try:
            # We don't have a native 'transaction' for ChromaDB easily in this version,
            # but we can ensure SQL commits before we claim success.
            # If SQL fails, we don't proceed to subsequent logic if caller uses session.
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def _load_graph_cache(self):
        """Loads all currently active facts into the NetworkX graph."""
        state = self.get_world_state()
        self.graph.clear()
        for fact in state.facts:
            self._add_fact_to_graph(fact)

    def _add_fact_to_graph(self, fact: Fact):
        """Helper to add a single fact to the NetworkX graph."""
        # Nodes are stored as strings for consistency with external IDs/Tags
        
        u = str(fact.subject_id)
        
        if fact.object_entity_id:
            v = str(fact.object_entity_id)
            self.graph.add_edge(
                u, v, 
                key=str(fact.id),
                predicate=fact.predicate, 
                weight=1.0 
            )
        else:
            v = f"literal:{fact.object_literal}"
            self.graph.add_edge(
                u, v,
                key=str(fact.id),
                predicate=fact.predicate,
                weight=1.0
            )

    def ingest_fact(self, subject_id: UUID, predicate: str, object_entity_id: Optional[UUID] = None, object_literal: Optional[str] = None, subject_type: str = "unknown") -> Fact:
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
                subject = EntityModel(id=subject_id, type=subject_type)
                session.add(subject)
            elif subject_type != "unknown":
                subject.type = subject_type
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
                try:
                    u = str(old_fact.subject_id)
                    v = str(old_fact.object_entity_id) if old_fact.object_entity_id else f"literal:{old_fact.object_literal}"
                    key = str(old_fact.id)
                    if self.graph.has_edge(u, v, key=key):
                        self.graph.remove_edge(u, v, key=key)
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
            
            # Update Entity Attributes for A2UI Data Binding
            # We treat facts as property updates on the subject entity
            val = object_literal if object_literal else str(object_entity_id)
            
            # Ensure subject attributes is a dict and update
            attrs = dict(subject.attributes) if subject.attributes else {}
            attrs[predicate] = val
            subject.attributes = attrs
            session.add(subject)
            
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

    def get_all_parent_tags(self, tags: List[str]) -> List[str]:
        """
        Recursively finds all parent tags for the given list of tags.
        Uses the 'is_a' predicate in the knowledge graph.
        """
        all_tags = set(tags)
        to_process = list(tags)
        visited = set()

        # Since we use NetworkX for active facts, we can use it for fast traversal
        # We need to make sure 'is_a' facts are in the graph.
        # Node IDs in graph are UUIDs or literals.
        # If tags are names, we might need a mapping name -> UUID.
        
        # For simplicity in this reference implementation, let's assume 
        # tags in ctx.tags can be names or UUID strings.
        
        while to_process:
            current = to_process.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Find parents in NetworkX graph
            # We look for edges (current, parent, predicate='is_a')
            if current in self.graph:
                for _, neighbor, data in self.graph.edges(current, data=True):
                    if data.get("predicate") == "is_a":
                        parent = str(neighbor)
                        if parent not in all_tags:
                            all_tags.add(parent)
                            to_process.append(parent)
                            
        return list(all_tags)

    def get_world_state(self, snapshot_time: Optional[datetime] = None) -> WorldState:
        """
        Retrieves the state of the world at a specific point in time.
        """
        if snapshot_time is None:
            snapshot_time = datetime.utcnow()
            
        session = self._get_session()
        try:
            # Clear ORM cache to ensure we get the latest from other threads/processes
            session.expire_all()
            
            # Fetch Active Entities
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
            
            # Fetch transient events
            events = []
            if hasattr(self, "_transient_events"):
                events = list(self._transient_events)
                self._transient_events.clear()

            return WorldState(
                tick=int(snapshot_time.timestamp() * 60), # Approx tick count
                entities=entities_map,
                facts=facts_list,
                event_queue=events
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

    

    def push_event(self, event_type: str, payload: Dict[str, Any] = None):
        """
        Pushes a new event into the world state queue.
        """
        from .schema import Event
        event = Event(
            id=uuid4(),
            type=event_type,
            payload=payload or {},
            timestamp=datetime.utcnow()
        )
        # Note: In a persistent DB, we would store this in an 'events' table.
        # For now, we'll keep a transient session-based queue if needed, 
        # but get_world_state currently hydrates from DB.
        # Let's add a simple transient queue to the store for this session.
        if not hasattr(self, "_transient_events"):
            self._transient_events = []
        self._transient_events.append(event)

    async def run_sleep_cycle(self):
        """
        Executes background maintenance tasks (Sleep Mode).
        Consolidates memories, prunes graph, distills skills.
        """
        import asyncio
        import logging
        logger = logging.getLogger("noetic.knowledge")
        
        logger.info("Starting Sleep Cycle...")
        
        try:
            # 1. Chunked/Async consolidation
            # For now, just simulate work
            for i in range(5):
                logger.debug(f"Sleep Cycle: Consolidating chunk {i+1}/5...")
                await asyncio.sleep(0.5) # Simulate IO
                
                # Check cancellation in loop (asyncio.sleep handles it, but logic might need explicit checks)
            
            logger.info("Sleep Cycle Complete.")
            
        except asyncio.CancelledError:
            logger.info("Sleep Cycle Interrupted (Waking Up).")
            raise

    