from typing import List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class LogEntry(BaseModel):
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)

class MemoryFrame(BaseModel):
    goal: str
    logs: List[LogEntry] = Field(default_factory=list)
    context: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MemoryStack:
    def __init__(self):
        self.frames: List[MemoryFrame] = []

    @property
    def current_frame(self) -> Optional[MemoryFrame]:
        if not self.frames:
            return None
        return self.frames[-1]

    def push_frame(self, goal: str, context: dict = None) -> MemoryFrame:
        frame = MemoryFrame(goal=goal, context=context or {})
        self.frames.append(frame)
        return frame

    def pop_frame(self, result: Any = None) -> Any:
        if not self.frames:
            return None # Or raise Error
        self.frames.pop()
        # In a real implementation, we might log the result to the parent frame
        return result

    def add_log(self, content: str, metadata: dict = None):
        if self.current_frame:
            log = LogEntry(content=content, metadata=metadata or {})
            self.current_frame.logs.append(log)
