from typing import Optional, List, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import create_engine, select, and_, or_, delete
from sqlalchemy.orm import sessionmaker, Session
import chromadb
from chromadb.config import Settings
import networkx as nx
from typing import Protocol

# Import Models (DB Layer)
from .models import Base, EntityModel, FactModel, SkillModel

# Import Unified Schema (API Layer)
from ..schema import Entity, Fact, Skill, EntityType, RelationType, MemoryFrame

class KnowledgeStore:
    def __init__(self, db_url: str = "sqlite:///noetic.db", vector_db_path: Optional[str] = None, collection_name: str = "knowledge_facts"):
        self.db_url = db_url
        if db_url == "sqlite:///:memory:":
            from sqlalchemy.pool import StaticPool
            self.engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False}, poolclass=StaticPool)
        else:
            self.engine = create_engine(db_url, echo=False, connect_args={"check_same_thread": False})
        
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        
        # Initialize ChromaDB (Vector Store)
        # We need two collections: one for Declarative Facts (Semantic), one for Procedural Skills (Procedural)
        if vector_db_path:
            self.chroma_client = chromadb.PersistentClient(path=vector_db_path)
        else:
            self.chroma_client = chromadb.EphemeralClient()
            
        self.fact_collection = self.chroma_client.get_or_create_collection(name="facts")
        self.skill_collection = self.chroma_client.get_or_create_collection(name="skills")

        # Initialize Graph Cache (Semantic Store)
        self.graph = nx.MultiDiGraph()
        self._load_graph_cache()
        
    def _get_session(self) -> Session:
        return self.SessionLocal()
        
    # ==========================================
    # Layer 2a: Semantic Store (Facts & Graph)
    # ==========================================
    
    def ingest_fact(self, fact: Fact) -> Fact:
        """
        Ingests a unified Fact object into SQL (Persistence), Graph (Relations), and Chroma (Search).
        """
        session = self._get_session()
        try:
            # 1. Ensure Subject Entity Exists
            self._ensure_entity(session, fact.subject_id, fact.subject_type)
            if fact.object_id:
                self._ensure_entity(session, fact.object_id, EntityType.CONCEPT) # Default to concept if unknown

            # 2. Add to SQL
            model = FactModel(
                id=fact.id,
                subject_id=UUID(fact.subject_id),
                predicate=fact.predicate.value,
                object_entity_id=UUID(fact.object_id) if fact.object_id else None,
                object_literal=fact.object_literal,
                confidence=fact.confidence,
                salience=fact.salience,
                source_type=fact.source_type,
                valid_from=fact.valid_from,
                valid_until=fact.valid_until
            )
            session.add(model)
            session.commit()
            
            # 3. Add to Graph
            self._add_fact_to_graph(fact)
            
            # 4. Add to Vector Store
            doc_text = f"{fact.subject_id} {fact.predicate.value} {fact.object_literal or fact.object_id}"
            self.fact_collection.add(
                ids=[str(fact.id)],
                documents=[doc_text],
                metadatas=[{"subject": fact.subject_id, "predicate": fact.predicate.value, "type": "fact"}]
            )
            
            return fact
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _ensure_entity(self, session: Session, entity_id: str, type: EntityType):
        uid = UUID(entity_id)
        existing = session.execute(select(EntityModel).where(EntityModel.id == uid)).scalar_one_or_none()
        if not existing:
            ent = EntityModel(id=uid, type=type.value)
            session.add(ent)

    def _add_fact_to_graph(self, fact: Fact):
        u = fact.subject_id
        v = fact.object_id if fact.object_id else f"literal:{fact.object_literal}"
        self.graph.add_edge(u, v, key=str(fact.id), predicate=fact.predicate.value)

    def _load_graph_cache(self):
        self.graph.clear()
        session = self._get_session()
        try:
            active_facts = session.execute(select(FactModel).where(FactModel.valid_until.is_(None))).scalars().all()
            for f in active_facts:
                self._add_fact_to_graph(self._map_model_to_fact(f))
        finally:
            session.close()

    def _map_model_to_fact(self, model: FactModel) -> Fact:
        return Fact(
            id=model.id,
            subject_id=str(model.subject_id),
            subject_type=EntityType.CONCEPT, # Simplified for reconstruction
            predicate=RelationType(model.predicate) if model.predicate in [r.value for r in RelationType] else RelationType.RELATED_TO,
            object_id=str(model.object_entity_id) if model.object_entity_id else None,
            object_literal=model.object_literal,
            confidence=model.confidence,
            salience=model.salience,
            valid_from=model.valid_from,
            valid_until=model.valid_until
        )

    # ==========================================
    # Layer 2b: Procedural Store (Skills)
    # ==========================================

    def ingest_skill(self, skill: Skill):
        """
        Persists a reusable skill into SQL and Vector Store.
        """
        session = self._get_session()
        try:
            model = SkillModel(
                id=skill.id,
                name=skill.name,
                trigger_condition=skill.trigger_condition,
                steps=skill.steps,
                success_rate=skill.success_rate,
                usage_count=skill.usage_count,
                created_at=skill.created_at
            )
            session.add(model)
            session.commit()
            
            # Vectorize Trigger Condition
            self.skill_collection.add(
                ids=[str(skill.id)],
                documents=[skill.trigger_condition],
                metadatas=[{"name": skill.name, "type": "skill"}]
            )
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def retrieve_relevant_skills(self, query: str, limit: int = 3) -> List[Skill]:
        """
        Finds skills semantically related to the query (Intent).
        """
        results = self.skill_collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        skills = []
        if results['ids'] and results['ids'][0]:
            session = self._get_session()
            try:
                ids = [UUID(i) for i in results['ids'][0]]
                models = session.execute(select(SkillModel).where(SkillModel.id.in_(ids))).scalars().all()
                for m in models:
                    skills.append(Skill(
                        id=m.id,
                        name=m.name,
                        trigger_condition=m.trigger_condition,
                        steps=m.steps,
                        success_rate=m.success_rate,
                        usage_count=m.usage_count,
                        created_at=m.created_at
                    ))
            finally:
                session.close()
        
        return skills

    # ==========================================
    # Layer 2c: Episodic Store (Events/Logs)
    # ==========================================

    def ingest_episode_summary(self, summary: str, frames: List[MemoryFrame]):
        """
        Invoked by AgentFold to store a consolidated narrative of an execution trace.
        """
        # For MVP, we treat an Episode Summary as a high-salience Fact on the Agent
        # Subject: Agent (Self) -> Predicate: EXPERIENCED -> Object: Summary
        fact = Fact(
            subject_id=str(uuid4()), # Placeholder for Self ID
            subject_type=EntityType.AGENT,
            predicate=RelationType.EVENT, # We might need a new RelationType like 'EXPERIENCED'
            object_literal=summary,
            salience=1.0,
            confidence=1.0
        )
        self.ingest_fact(fact)

    def hybrid_search(self, query: str, limit: int = 5) -> List[Fact]:
        """
        Performs a hybrid search:
        1. Semantic search in ChromaDB.
        2. Filters results for validity in SQL (or just by checking valid_until via ID lookup).
        """
        # 1. Search Chroma
        results = self.fact_collection.query(
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
            return [self._map_model_to_fact(m) for m in valid_models]
            
        finally:
            session.close()
