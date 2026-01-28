from typing import List, Optional, Any
from uuid import UUID
from ..schema import MemoryFrame

class StackError(Exception):
    """Raised when an invalid stack operation is attempted."""
    pass

class MemoryStack:
    """
    Implements the 'Working Memory' of the Agent as a Frame Stack.
    Enforces strict scoping of context to prevent 'Token Bloat'.
    """
    
    def __init__(self):
        self._frames: List[MemoryFrame] = []
        
    @property
    def depth(self) -> int:
        return len(self._frames)
    
    def get_active_frame(self) -> Optional[MemoryFrame]:
        """Returns the currently active (top) frame."""
        if not self._frames:
            return None
        return self._frames[-1]

    def push_frame(self, goal: str) -> UUID:
        """
        Creates a new stack frame for a sub-task.
        """
        parent_id = self.get_active_frame().id if self._frames else None
        
        new_frame = MemoryFrame(
            goal=goal,
            parent_id=parent_id
        )
        
        self._frames.append(new_frame)
        return new_frame.id
        
    def pop_frame(self, return_value: Any = None) -> Any:
        """
        Destroys the current frame (GC) and returns the result to the parent.
        """
        if not self._frames:
            raise StackError("Cannot pop from an empty stack.")
            
        # The frame is destroyed here (implicitly by removing reference)
        # Any local_vars in this frame are lost to the ether (Garbage Collected)
        popped_frame = self._frames.pop()
        
        # In a real implementation, we might process 'popped_frame' for Procedural Memory here
        # e.g., if success, distill into a Skill.
        
        return return_value

    def add_log(self, content: str):
        """Adds a thought/log to the active frame's scratchpad."""
        active = self.get_active_frame()
        if not active:
            raise StackError("No active frame to log to.")
        active.scratchpad.append(content)
        
    def set_var(self, key: str, value: Any):
        """Sets a local variable in the active frame."""
        active = self.get_active_frame()
        if not active:
            raise StackError("No active frame to set variable in.")
        active.local_vars[key] = value