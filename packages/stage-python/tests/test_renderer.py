import pytest
from noetic_stage.schema import Intent, RenderEvent
from noetic_stage.renderer import Renderer

def test_render_intent():
    renderer = Renderer()
    
    intent = Intent(
        type="display_message",
        content={"text": "Hello World"}
    )
    
    event = renderer.render(intent)
    
    assert isinstance(event, RenderEvent)
    assert event.type == "ui_card"
    assert event.payload["content"] == "Hello World"
    assert event.payload["component"] == "MessageCard"
