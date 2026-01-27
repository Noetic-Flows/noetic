from typing import Dict, Any
import httpx
from noetic_conscience.contracts import AgenticIntentContract
from .base import Agent, AgentDefinition

class N8nAgent(Agent):
    """
    An Agent that executes intents by forwarding them to an n8n Webhook.
    """
    def __init__(self, definition: AgentDefinition, webhook_url: str):
        super().__init__(definition)
        self.webhook_url = webhook_url

    async def execute(self, tool: str, params: Dict[str, Any], contract: AgenticIntentContract) -> Dict[str, Any]:
        """
        Forwards the execution request to n8n.
        payload = {
            "tool": tool,
            "params": params,
            "contract": contract.serialize()
        }
        """
        payload = {
            "tool": tool,
            "params": params,
            "contract": contract.serialize()
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # We expect n8n to return a JSON response with the result
                response = await client.post(self.webhook_url, json=payload, timeout=60.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                # Wrap the error 
                return {
                    "error": str(e),
                    "status": "failed",
                    "details": "N8n webhook call failed"
                }
