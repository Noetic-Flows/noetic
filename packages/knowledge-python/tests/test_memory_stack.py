import pytest
from noetic_knowledge.working.stack import MemoryStack, MemoryFrame

def test_stack_lifecycle():
    stack = MemoryStack()
    assert stack.current_frame is None

    # Push Frame 1
    frame1 = stack.push_frame(goal="Root Goal", context={"user": "alice"})
    assert stack.current_frame == frame1
    assert stack.current_frame.goal == "Root Goal"
    assert stack.current_frame.context["user"] == "alice"

    # Log to Frame 1
    stack.add_log("Started process")
    assert len(stack.current_frame.logs) == 1
    assert stack.current_frame.logs[0].content == "Started process"

    # Push Frame 2
    frame2 = stack.push_frame(goal="Sub Goal")
    assert stack.current_frame == frame2
    assert stack.current_frame != frame1

    # Log to Frame 2
    stack.add_log("Working on subtask")
    assert len(stack.current_frame.logs) == 1
    assert len(frame1.logs) == 1 # Frame 1 unchanged

    # Pop Frame 2
    stack.pop_frame()
    assert stack.current_frame == frame1
    
    # Pop Frame 1
    stack.pop_frame()
    assert stack.current_frame is None

def test_empty_stack_pop():
    stack = MemoryStack()
    result = stack.pop_frame()
    assert result is None
