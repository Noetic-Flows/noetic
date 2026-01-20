from typing import List, Dict, Any
from pydantic import BaseModel

class Principle(BaseModel):
    id: str
    description: str
    logic: Dict[str, Any] # JsonLogic

class AgentContext(BaseModel):
    id: str
    system_prompt: str
    allowed_skills: List[str]
    principles: List[Principle]
