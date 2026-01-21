from typing import Dict, Any, Optional
from noetic_engine.knowledge import WorldState

class ReflexManager:
    """
    Manages the 'Reflex Loop' state - transient UI state that hasn't hit the Brain yet.
    """
    def __init__(self):
        self.local_state: Dict[str, Any] = {}

    def update(self, key: str, value: Any):
        """
        Updates a local state value (e.g. text input field).
        """
        self.local_state[key] = value

    def merge_state(self, world_state: WorldState) -> Dict[str, Any]:
        """
        Merges the authoritative WorldState with the local transient state.
        Local state takes precedence for UI responsiveness.
        """
        merged = world_state.model_dump()
        merged.update(self.local_state)
        return merged