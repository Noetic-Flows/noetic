import pytest
from uuid import UUID
from noetic_knowledge.working.stack import MemoryStack, StackError
from noetic_knowledge.schema import MemoryFrame

def test_stack_initialization():
    """Verify stack starts empty or with initial frame."""
    stack = MemoryStack()
    assert stack.depth == 0
    assert stack.get_active_frame() is None

def test_push_pop_frame_lifecycle():
    """Test the full lifecycle of a frame: Push -> Act -> Pop."""
    stack = MemoryStack()
    
    # 1. Push
    frame_id = stack.push_frame(goal="Understand the Universe")
    assert stack.depth == 1
    active = stack.get_active_frame()
    assert active.goal == "Understand the Universe"
    assert active.id == frame_id
    
    # 2. Push Child
    child_id = stack.push_frame(goal="Calculate 42")
    assert stack.depth == 2
    child = stack.get_active_frame()
    assert child.goal == "Calculate 42"
    assert child.parent_id == frame_id
    
    # 3. Pop Child
    return_val = stack.pop_frame(return_value=42)
    assert return_val == 42
    assert stack.depth == 1
    assert stack.get_active_frame().id == frame_id
    
    # 4. Pop Root
    final_val = stack.pop_frame(return_value="42")
    assert final_val == "42"
    assert stack.depth == 0

def test_local_scope_isolation():
    """Verify that variables are isolated to frames and destroyed on pop."""
    stack = MemoryStack()
    stack.push_frame("Parent Task")
    stack.set_var("shared_key", "parent_value")
    
    stack.push_frame("Child Task")
    stack.set_var("child_key", "child_value")
    
    # Child frame should have its own var, and NOT see parent's var implicitly (unless we decide on scope rules)
    # Strict AgentProg usually means explicit passing, or lexical scoping.
    # For now, let's assume Strict Scoping: active frame only.
    current_vars = stack.get_active_frame().local_vars
    assert "child_key" in current_vars
    assert "shared_key" not in current_vars # MemoryFrame is isolated
    
    stack.pop_frame()
    
    # Back to parent
    parent_vars = stack.get_active_frame().local_vars
    assert "shared_key" in parent_vars
    assert "child_key" not in parent_vars # Child var effectively GC'd

def test_scratchpad_logging():
    """Test adding thoughts to the scratchpad."""
    stack = MemoryStack()
    stack.push_frame("Thinking Task")
    
    stack.add_log("Thought 1")
    stack.add_log("Thought 2")
    
    frame = stack.get_active_frame()
    assert len(frame.scratchpad) == 2
    assert frame.scratchpad[0] == "Thought 1"

def test_pop_empty_stack_error():
    """Pop on empty stack should raise error."""
    stack = MemoryStack()
    with pytest.raises(StackError):
        stack.pop_frame()
