from typing import Any, Optional
from noetic_lang.core import FlowDefinition

class FlowExecutor:
    def __init__(self, interpreter: Any):
        self.interpreter = interpreter

    async def run_flow(self, flow: FlowDefinition) -> str:
        current_state_name = flow.start_at
        
        while current_state_name:
            state_def = flow.states.get(current_state_name)
            if not state_def:
                break
            
            # Execute skill/stanza if needed (mocked in test)
            if state_def.skill:
                 # In real implementation, resolve skill/stanza from ID and call interpreter
                 pass

            if not state_def.next:
                return current_state_name
                
            current_state_name = state_def.next
            
        return current_state_name
