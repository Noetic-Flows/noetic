from typing import Dict, Any, Optional
import uuid
from noetic_lang.core.flow import FlowDefinition

class FlowExecutor:
    """
    Executes a single instance of a Flow using a State Machine.
    """
    def __init__(self, flow_def: Dict[str, Any], context: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.flow_def = flow_def
        # Try to validate via Pydantic if possible, or trust dict
        try:
             self.model = FlowDefinition(**flow_def)
        except Exception:
             # Fallback if raw dict doesn't match exactly or pure dict usage
             self.model = None

        self.context = context
        self.current_state_name = flow_def.get("start_at") 
        self.is_complete = False
        self.history = []

    async def step(self):
        """
        Advance the state machine by one step.
        """
        if self.is_complete or not self.current_state_name:
            return

        states = self.flow_def.get("states", {})
        current_state = states.get(self.current_state_name)
        
        if not current_state:
            raise ValueError(f"State '{self.current_state_name}' not found in flow.")

        # Log history
        self.history.append({
            "state": self.current_state_name,
            "params": current_state.get("params")
        })

        # TODO: Execute State Logic here (Task/Stanza specific)
        # For now, we just transition.

        # Determine Next State
        if current_state.get("end", False):
            self.is_complete = True
            self.current_state_name = None
            return

        next_state = current_state.get("next")
        if next_state:
            self.current_state_name = next_state
        else:
            # Implicit end? Or error?
            # For now, treat as end if no next.
            self.is_complete = True
            self.current_state_name = None


class FlowManager:
    """
    Manages the lifecycle and execution of Flows (State Machines).
    """
    def __init__(self):
        self.flows: Dict[str, Dict[str, Any]] = {}
        self.active_instances: Dict[str, FlowExecutor] = {}

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

    def start_flow(self, flow_id: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a new execution instance of a registered flow.
        """
        flow_def = self.get_flow(flow_id)
        if not flow_def:
            raise ValueError(f"Flow '{flow_id}' not found.")
        
        if context is None:
            context = {}

        executor = FlowExecutor(flow_def, context)
        self.active_instances[executor.id] = executor
        return executor.id

    def get_executor(self, execution_id: str) -> Optional[FlowExecutor]:
        return self.active_instances.get(execution_id)

