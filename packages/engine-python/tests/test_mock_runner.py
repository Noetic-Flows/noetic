import pytest
import os
import asyncio
from noetic_engine.runtime.engine import NoeticEngine
from noetic_engine.loader import NoeticLoader
from noetic_stage.schema import Column, Text
import fastui.components as c

@pytest.fixture
def mock_runner_setup():
    # 1. Initialize Engine (InMemory)
    engine = NoeticEngine(db_url="sqlite:///:memory:")
    
    # 2. Load Fixture
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fixture_path = os.path.join(base_dir, "fixtures/minimal.noetic")
    
    loader = NoeticLoader()
    loader.load(engine, fixture_path)
    
    return engine

@pytest.mark.asyncio
async def test_mock_runner_initialization(mock_runner_setup):
    engine = mock_runner_setup
    
    # Verify Knowledge Hydration
    # We expect "Project Alpha" facts to be in the graph/store
    # We'll search for it (hybrid search or exact match using internal store)
    
    # Check Internal Store directly for exact match
    # Since we don't have easy exact match API exposed public, using hybrid search on known literal
    results = engine.knowledge.hybrid_search("Project Alpha", limit=1)
    # Note: Hybrid search might return empty if Chroma not flushed/committed or if mocked
    # Let's check get_world_state() directly which uses SQL
    
    state = engine.knowledge.get_world_state()
    
    # Verify Fact Existence
    found_title = any(
        f.predicate == "title" and f.object_literal == "Project Alpha" 
        for f in state.facts
    )
    assert found_title, "Failed to hydrate assertions from minimal.noetic"

    # Verify Canvas Loading
    assert engine.reflex.root_component is not None
    assert isinstance(engine.reflex.root_component, Column)

@pytest.mark.asyncio
async def test_mock_runner_rendering(mock_runner_setup):
    engine = mock_runner_setup
    
    # Trigger a Render Tick
    state = engine.knowledge.get_world_state()
    ui_tree = engine.reflex.tick([], state)
    
    # Verify Rendering - Returns FastUI Components
    # The root is a Div (from Column) with 2 children.
    
    assert isinstance(ui_tree, c.Div)
    assert len(ui_tree.components) == 2
    
    # Check First Child (Bound)
    child_0 = ui_tree.components[0]
    assert isinstance(child_0, c.Text)
    # The 'text' should be resolved to the string value if binding worked
    assert child_0.text == "Project Alpha"
    
    # Check Second Child (Static)
    child_1 = ui_tree.components[1]
    assert child_1.text == "Static Footer"

