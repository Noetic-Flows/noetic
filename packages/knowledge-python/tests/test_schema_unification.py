import pytest
from datetime import datetime, timedelta
from noetic_knowledge.schema import Fact, Entity, Skill, EntityType, RelationType

def test_fact_confidence_decay():
    """Verify that confidence decays over time for non-axiom facts."""
    now = datetime.utcnow()
    past = now - timedelta(hours=24)
    
    fact = Fact(
        subject_id="test_sub", 
        subject_type=EntityType.CONCEPT,
        predicate=RelationType.RELATED_TO,
        valid_from=past,
        confidence=1.0,
        source_type="inference"
    )
    
    # After 24 hours, confidence should be 0.9 * 1.0 = 0.9
    assert abs(fact.current_confidence - 0.9) < 0.001

def test_axiom_confidence_stable():
    """Axioms should not decay."""
    now = datetime.utcnow()
    past = now - timedelta(hours=1000)
    
    fact = Fact(
        subject_id="test_sub",
        subject_type=EntityType.CONCEPT,
        predicate=RelationType.RELATED_TO, 
        valid_from=past,
        confidence=1.0,
        source_type="axiom"
    )
    
    assert fact.current_confidence == 1.0

def test_entity_model():
    entity = Entity(type=EntityType.AGENT, attributes={"name": "Archie"})
    assert entity.type == EntityType.AGENT
    assert entity.attributes["name"] == "Archie"

def test_skill_model():
    skill = Skill(
        name="TestSkill",
        trigger_condition="Perform test",
        steps=["Step 1", "Step 2"]
    )
    assert skill.usage_count == 0
    assert len(skill.steps) == 2
