from typing import List, Dict, Optional
from uuid import UUID

class GraphScope:
    """
    Manages the 'Mount Points' of an agent onto the shared Knowledge Graph.
    Enforces permissions (Read/Write) on specific sub-graphs.
    """
    
    def __init__(self, agent_id: UUID, mounts: List[Dict[str, str]]):
        self.agent_id = agent_id
        self.mounts = mounts  # E.g., [{"id": "project:123", "access": "RW"}]
        
    def can_read(self, node_id: str) -> bool:
        # TODO: Check if node_id falls within any mounted scope
        return True
        
    def can_write(self, node_id: str) -> bool:
        # TODO: Check if node_id falls within a RW mounted scope
        return True
