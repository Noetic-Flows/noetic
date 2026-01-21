import pytest
from uuid import uuid4
from datetime import datetime
from noetic_engine.knowledge.store import KnowledgeStore
from noetic_engine.knowledge.schema import Entity

@pytest.fixture
def store():
    return KnowledgeStore(db_url="sqlite:///:memory:")

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