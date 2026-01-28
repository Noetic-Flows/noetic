from abc import ABC, abstractmethod
from typing import Any, Dict
from .schema import Component

class Visage(ABC):
    """
    Abstract Base Class for a specific "Presence" or "Personality" of the Agent.
    Defines the structural layout and rendering strategy of the UI.
    """
    
    @abstractmethod
    def render(self, context: Dict[str, Any]) -> Component:
        """
        Returns the Root Component of the UI based on the current context.
        """
        pass
