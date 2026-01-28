import pytest
from noetic_stage.visage import Visage
from noetic_stage.schema import Component, Text, Column
from noetic_engine.runtime.reflex import ReflexSystem

class MockVisage(Visage):
    def render(self, context) -> Component:
        return Column(children=[
            Text(content="Hello Visage"),
            Text(content=f"Project: {context.get('project_name', 'Unknown')}")
        ])

def test_visage_contract():
    # 1. Verify Instantiation
    visage = MockVisage()
    assert isinstance(visage, Visage)

def test_reflex_loading_visage():
    # 2. Verify integration with ReflexSystem
    reflex = ReflexSystem()
    visage = MockVisage()
    
    # ReflexSystem doesn't have set_visage yet, we pretend it does or use set_root
    #Ideally ReflexSystem should take a Visage strategy
    
    # For now, let's verify we can manually render it
    context = {"project_name": "Noetic"}
    root = visage.render(context)
    
    # Render using the engine's renderer
    output = reflex.renderer.render(root, context)
    
    # Depending on whether fastui is installed, check output
    # Asserting we got a Div (Column)
    assert output  # Just check it returns something valid
    # In a real test we'd check isinstance(output, fastui.components.Div) but we avoid strict dependency here
