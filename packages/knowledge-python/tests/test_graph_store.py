import pytest
from uuid import uuid4
from noetic_knowledge.store.store import KnowledgeStore

@pytest.fixture
def store():
    # Use in-memory SQLite and Ephemeral Chroma Client
    s = KnowledgeStore(db_url="sqlite:///:memory:", vector_db_path=None)
    return s

def test_ingest_fact_literal(store):
    subject_id = uuid4()
    predicate = "likes"
    obj_literal = "pizza"
    
    fact = store.ingest_fact(
        subject_id=subject_id,
        predicate=predicate,
        object_literal=obj_literal
    )
    
    assert fact.subject_id == subject_id
    assert fact.predicate == predicate
    assert fact.object_literal == obj_literal
    assert fact.valid_until is None

    # Verify in SQL state
    state = store.get_world_state()
    assert len(state.facts) == 1
    assert state.facts[0].id == fact.id

def test_hybrid_search(store):
    subject_id = uuid4()
    store.ingest_fact(subject_id, "likes", object_literal="pizza")
    store.ingest_fact(subject_id, "likes", object_literal="sushi")
    
    # Search for "pizza"
    # We expect the semantic search to find the fact containing "pizza"
    results = store.hybrid_search("pizza")
    
    assert len(results) >= 1
    found_pizza = any(f.object_literal == "pizza" for f in results)
    assert found_pizza
