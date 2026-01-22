from typing import Dict, Optional
from noetic_engine.stanzas.agents import AgentContext

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, AgentContext] = {}

    def register(self, agent: AgentContext):
        self.agents[agent.id] = agent

    def get(self, agent_id: str) -> Optional[AgentContext]:
        return self.agents.get(agent_id)
