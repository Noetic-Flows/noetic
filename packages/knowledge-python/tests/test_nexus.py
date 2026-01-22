import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from noetic_knowledge.working.nexus import Nexus
from noetic_knowledge.store.schema import Fact

def test_relevance_scoring():
    nexus = Nexus()
    
    now = datetime.utcnow()
    
    fact_recent = Fact(
        id=uuid4(), subject_id=uuid4(), predicate="test", object_literal="A",
        valid_from=now - timedelta(minutes=1),
        confidence=1.0,
        source_type="observation"
    )
    
    fact_old = Fact(
        id=uuid4(), subject_id=uuid4(), predicate="test", object_literal="B",
        valid_from=now - timedelta(days=1),
        confidence=1.0,
        source_type="observation"
    )
    
    # Nexus should score recent facts higher if semantic relevance is equal
    # We assume score_fact takes the fact and an optional query string context
    score_recent = nexus.score_fact(fact_recent, query="test")
    score_old = nexus.score_fact(fact_old, query="test")
    
    assert score_recent > score_old
