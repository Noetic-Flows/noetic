import pytest
from noetic_engine.knowledge.working.stack import MemoryStack, MemoryFrame, LogEntry

@pytest.fixture
def stack():
    return MemoryStack()

def test_push_frame(stack):
    stack.push_frame("Goal 1")
    assert len(stack.frames) == 1
    assert stack.current_frame.goal == "Goal 1"

def test_add_log(stack):
    stack.push_frame("Goal 1")
    stack.add_log("Log 1")
    assert len(stack.current_frame.logs) == 1
    assert stack.current_frame.logs[0].content == "Log 1"

def test_pop_frame(stack):
    stack.push_frame("Goal 1")
    stack.add_log("Log 1")
    
    result = stack.pop_frame(result="Success")
    
    assert len(stack.frames) == 0
    assert result == "Success"

def test_scope_isolation(stack):
    stack.push_frame("Root")
    stack.add_log("Root Log")
    
    stack.push_frame("Subtask")
    stack.add_log("Sub Log")
    
    assert len(stack.frames) == 2
    assert len(stack.current_frame.logs) == 1
    assert stack.current_frame.logs[0].content == "Sub Log"
    
    stack.pop_frame()
    
    assert len(stack.frames) == 1
    assert stack.current_frame.goal == "Root"
    assert len(stack.current_frame.logs) == 1
    assert stack.current_frame.logs[0].content == "Root Log"
