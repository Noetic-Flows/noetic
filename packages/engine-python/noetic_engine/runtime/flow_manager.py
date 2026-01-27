from typing import Dict, Any, Optional

class FlowManager:
    """
    Manages the lifecycle and execution of Flows (State Machines).
    """
    def __init__(self):
        self.flows: Dict[str, Any] = {}
        self.active_instances: Dict[str, Any] = {}

    def register(self, flow_definition: Dict[str, Any]):
        """
        Register a new Flow Definition.
        """
        flow_id = flow_definition.get("id")
        if not flow_id:
            raise ValueError("Flow definition missing 'id'")
        self.flows[flow_id] = flow_definition
        
    def get_flow(self, flow_id: str) -> Optional[Dict[str, Any]]:
        return self.flows.get(flow_id)
