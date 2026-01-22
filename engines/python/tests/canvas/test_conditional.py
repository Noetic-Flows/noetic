import pytest
from noetic_engine.canvas import CanvasRenderer, Text, Binding, Conditional
from noetic_engine.canvas.schema import Conditional

@pytest.fixture
def renderer():
    return CanvasRenderer()

def test_conditional_true(renderer):
    context = {"is_admin": True}
    
    comp = Conditional(
        condition=Binding(bind="/is_admin"),
        true_child=Text(content="Admin Panel"),
        false_child=Text(content="Access Denied")
    )
    
    result = renderer.render(comp, context)
    
    # Assert result is the true child
    assert result.text == "Admin Panel"

def test_conditional_false(renderer):
    context = {"is_admin": False}
    
    comp = Conditional(
        condition=Binding(bind="/is_admin"),
        true_child=Text(content="Admin Panel"),
        false_child=Text(content="Access Denied")
    )
    
    result = renderer.render(comp, context)
    
    # Assert result is the false child
    assert result.text == "Access Denied"

def test_conditional_false_no_fallback(renderer):
    context = {"is_admin": False}
    
    comp = Conditional(
        condition=Binding(bind="/is_admin"),
        true_child=Text(content="Admin Panel")
    )
    
    result = renderer.render(comp, context)
    
    # Assert result is an empty div (components list empty)
    # The renderer returns c.Div(components=[])
    assert result.components == []

def test_conditional_literal(renderer):
    context = {}
    
    # Test with literal boolean True
    comp = Conditional(
        condition=True,
        true_child=Text(content="Always Visible")
    )
    
    result = renderer.render(comp, context)
    assert result.text == "Always Visible"
