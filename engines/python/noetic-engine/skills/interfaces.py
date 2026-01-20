from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class SkillResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    cost: float = 0.0
    latency_ms: int = 0

class SkillContext(BaseModel):
    agent_id: str
    # Add other context like permissions here

class Skill(ABC):
    id: str
    description: str
    schema: Dict[str, Any] # JSON Schema for arguments

    @abstractmethod
    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """
        The uniform entry point.
        """
        pass
