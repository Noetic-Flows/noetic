import pytest
from uuid import uuid4
from datetime import datetime
from noetic_knowledge.store.store import KnowledgeStore
from noetic_knowledge.schema import Fact, Skill, EntityType, RelationType, MemoryFrame

@pytest.fixture
def store():
    # Use in-memory SQLite and ephemeral Chroma
    return KnowledgeStore(db_url="sqlite:///:memory:", vector_db_path=None)

def test_ingest_and_retrieve_fact(store):
    subject_id = str(uuid4())
    fact = Fact(
        subject_id=subject_id,
        subject_type=EntityType.CONCEPT,
        predicate=RelationType.RELATED_TO,
        object_literal="Test Concept",
        salience=0.8,
        confidence=0.9
    )
    
    saved_fact = store.ingest_fact(fact)
    
    assert saved_fact.id == fact.id
    assert saved_fact.salience == 0.8
    
    # Test retrieval via hybrid search
    results = store.hybrid_search("Test Concept")
    assert len(results) > 0
    assert results[0].object_literal == "Test Concept"

def test_ingest_and_retrieve_skill(store):
    skill = Skill(
        id=uuid4(),
        name="Python Coding",
        trigger_condition="User asks to write python code",
        steps=["Analyze request", "Write implementation", "Verify code"],
    )
    
    store.ingest_skill(skill)
    
    # Search for the skill
    results = store.retrieve_relevant_skills("I need a python script", limit=1)
    assert len(results) == 1
    assert results[0].name == "Python Coding"
    assert results[0].steps == ["Analyze request", "Write implementation", "Verify code"]

def test_episodic_ingestion(store):
    summary = "Agent successfully implemented the Tri-Store logic."
    frames = [] # Mock frames for now
    
    store.ingest_episode_summary(summary, frames)
    
    # Verify it was stored as a high-salience fact
    results = store.hybrid_search(summary)
    assert len(results) > 0
    fact = results[0]
    assert fact.object_literal == summary
    assert fact.predicate == RelationType.EVENT
    assert fact.salience == 1.0
