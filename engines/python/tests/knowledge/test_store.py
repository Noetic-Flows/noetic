import pytest
from uuid import uuid4
from datetime import datetime
from noetic_engine.knowledge.store import KnowledgeStore
from noetic_engine.knowledge.schema import Entity

import uuid

@pytest.fixture
def store():
    # Use unique collection name to avoid leakage between tests in the same process
    return KnowledgeStore(db_url="sqlite:///:memory:", collection_name=f"test_coll_{uuid.uuid4().hex}")

def test_ingest_and_retrieve_fact(store):
    # 1. Create dummy IDs
    user_id = uuid4()
    
    # 2. Ingest a fact
    fact = store.ingest_fact(
        subject_id=user_id,
        predicate="status",
        object_literal="happy"
    )
    
    assert fact.subject_id == user_id
    assert fact.predicate == "status"
    assert fact.object_literal == "happy"
    assert fact.valid_until is None

    # 3. Get World State
    state = store.get_world_state()
    
    assert len(state.facts) == 1
    assert state.facts[0].id == fact.id

def test_hybrid_search(store):
    user_id = uuid4()
    store.ingest_fact(user_id, "prefers", object_literal="pepperoni pizza")
    
    # Search for pizza
    results = store.hybrid_search("pepperoni pizza", limit=5)
    assert len(results) >= 1
    assert results[0].object_literal == "pepperoni pizza"

def test_graph_cache_integration(store):
    user_id = uuid4()
    store.ingest_fact(user_id, "location", object_literal="room_101")
    
    assert store.graph.has_edge(user_id, "literal:room_101")
    
    # Update fact (contradiction)
    store.ingest_fact(user_id, "location", object_literal="room_102")
    
    # Old edge should be gone (or at least marked invalid in DB, but graph check relies on logic)
    # Our implementation removes the old edge from graph
    assert not store.graph.has_edge(user_id, "literal:room_101")
    assert store.graph.has_edge(user_id, "literal:room_102")