from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class SkillResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    cost: float = 0.0
    latency_ms: int = 0

class SkillContext(BaseModel):
    agent_id: str
    store: Optional[Any] = Field(default=None, exclude=True) # Exclude from serialization, hold runtime ref
    engine: Optional[Any] = Field(default=None, exclude=True) # Access to the NoeticEngine instance
    # Add other context like permissions here

class Skill(ABC):
    id: str
    description: str
    schema: Dict[str, Any] # JSON Schema for arguments

    @property
    def preconditions(self) -> Dict[str, Any]:
        """
        State requirements for this skill to be executable.
        Format: {"key": value}
        """
        return {}

    @property
    def postconditions(self) -> Dict[str, Any]:
        """
        State changes resulting from this skill's execution.
        Format: {"key": value}
        """
        return {}

    @abstractmethod
    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """
        The uniform entry point.
        """
        pass
