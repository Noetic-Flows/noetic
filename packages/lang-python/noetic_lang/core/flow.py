from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator

class FlowState(BaseModel):
    name: str
    skill: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    next: Optional[str] = None # Simple transition
    # We will need conditional transitions logic here eventually

class FlowDefinition(BaseModel):
    id: str
    description: Optional[str] = None
    start_at: str
    states: Dict[str, FlowState]

    @model_validator(mode='after')
    def check_graph_integrity(self) -> 'FlowDefinition':
        # Check start_at
        if self.start_at not in self.states:
            raise ValueError(f"start_at '{self.start_at}' not found in states")
        
        # Check transitions
        for state_id, state in self.states.items():
            if state.next and state.next not in self.states:
                raise ValueError(f"State '{state_id}' transitions to unknown state '{state.next}'")
        
        return self
