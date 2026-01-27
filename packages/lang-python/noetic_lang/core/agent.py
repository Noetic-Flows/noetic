from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class Principle(BaseModel):
    description: str
    threshold: float = 0.5

class AgentDefinition(BaseModel):
    id: str
    system_prompt: str
    allowed_skills: List[str]
    principles: List[Principle]
    persona: Optional[Dict[str, Any]] = None
