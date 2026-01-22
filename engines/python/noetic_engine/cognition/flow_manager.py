from typing import Dict, Optional, Any
from noetic_engine.stanzas.flows import FlowExecutor

class FlowManager:
    def __init__(self):
        self._flows: Dict[str, FlowExecutor] = {}

    def register(self, flow_def: Dict[str, Any]):
        flow_id = flow_def.get("id")
        if not flow_id:
            return
        
        executor = FlowExecutor(flow_def)
        self._flows[flow_id] = executor

    def get_executor(self, flow_id: str) -> Optional[FlowExecutor]:
        return self._flows.get(flow_id)
