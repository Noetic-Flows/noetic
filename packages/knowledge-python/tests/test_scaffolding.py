import pytest
from noetic_knowledge.ontology import Ontology, EntityType
from noetic_knowledge.schema import MemoryFrame, Fact, Skill
from noetic_knowledge.nexus.assembler import ContextAssembler
from noetic_knowledge.nexus.budget import TokenBudgetManager
from noetic_knowledge.sync.scope import GraphScope
from noetic_knowledge.sync.bus import EventBus

def test_ontology_initialization():
    ontology = Ontology()
    assert len(ontology.allowed_types) > 0
    assert EntityType.AGENT in ontology.allowed_types

def test_schema_initialization():
    fact = Fact(subject_id="test", subject_type=EntityType.AGENT, predicate="created")
    assert fact.salience == 0.0

def test_nexus_initialization():
    budget = TokenBudgetManager()
    assembler = ContextAssembler(token_budget_manager=budget)
    assert assembler.budget is not None

def test_sync_initialization():
    bus = EventBus()
    assert bus.subscribers == {}
    
    scope = GraphScope(agent_id="test", mounts=[])
    assert scope.can_read("any_node") == True
