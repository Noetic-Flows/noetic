from typing import Dict, Any, Optional
import datetime
from noetic_conscience.contracts import AgenticIntentContract
from noetic_stdlib.agents.base import Agent

class MeshOrchestrator:
    """
    The Runtime Kernel: Manages Agents and enforces Contracts.
    """
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.public_key: Optional[Any] = None

    def set_public_key(self, public_key):
        self.public_key = public_key

    def register_agent(self, agent: Agent):
        print(f"Registering agent: {agent.definition.name} ({agent.definition.id})")
        self.agents[agent.definition.id] = agent

    async def route_intent(self, agent_id: str, tool: str, params: Dict[str, Any], contract: AgenticIntentContract) -> Any:
        # 1. Verify Contract Signature
        if self.public_key:
             if not contract.verify(self.public_key):
                raise PermissionError("Invalid contract signature")
        
        # 2. Verify Capabilities (Scope Check)
        if tool not in contract.scopes.allowed_tools:
            raise PermissionError(f"Tool '{tool}' is not in the allowed scope of this contract")
            
        # 3. Find Agent
        target_agent = self.agents.get(agent_id)
        if not target_agent:
             raise ValueError(f"Agent '{agent_id}' not found in Mesh.")

        # 4. Verify Agent Capability
        if tool not in target_agent.definition.allowed_tools:
             raise PermissionError(f"Agent '{agent_id}' does not have capability '{tool}'")

        # 5. Execute
        print(f"Routing intent '{tool}' to agent '{agent_id}'...")
        return await target_agent.execute(tool, params, contract)
