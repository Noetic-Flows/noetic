from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from noetic_engine.conscience import Principle

class AgentContext(BaseModel):
    id: str
    system_prompt: str
    allowed_skills: List[str]
    principles: List[Principle]
    persona: Optional[Dict[str, Any]] = None
