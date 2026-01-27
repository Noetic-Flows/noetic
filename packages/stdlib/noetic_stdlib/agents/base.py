from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from noetic_conscience.contracts import AgenticIntentContract

class AgentDefinition(BaseModel):
    """
    The Data: Configuration for an Agent.
    """
    id: str
    name: str 
    description: str
    allowed_tools: List[str]
    # system_prompt is optional because some agents (like n8n) might not be LLM-based
    system_prompt: Optional[str] = None 

class Agent(ABC):
    """
    The Entity: Runtime logic for an Agent.
    """
    def __init__(self, definition: AgentDefinition):
        self.definition = definition

    @abstractmethod
    async def execute(self, tool: str, params: Dict[str, Any], contract: AgenticIntentContract) -> Dict[str, Any]:
        """
        Execute an intent.
        :param tool: The name of the tool/capability to execute.
        :param params: The parameters for the tool.
        :param contract: The signed contract authorizing this execution.
        """
        pass
