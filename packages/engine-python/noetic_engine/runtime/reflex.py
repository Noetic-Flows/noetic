from typing import List, Any, Dict, Optional
from noetic_stage.renderer import CanvasRenderer
from noetic_stage.reflex import ReflexManager
from noetic_stage.schema import Component
from noetic_knowledge import WorldState

from noetic_stage.visage import Visage

class ReflexSystem:
    """
    Manages the 'Reflex Loop' (System 1) - UI rendering and Input handling.
    Runs synchronously at 60Hz.
    """
    def __init__(self):
        self.renderer = CanvasRenderer()
        self.manager = ReflexManager()
        self.root_component: Optional[Component] = None
        self.visage: Optional[Visage] = None

    def set_root(self, root: Component):
        self.root_component = root
        
    def set_visage(self, visage: Visage):
        self.visage = visage

    def render_now(self, world_state: WorldState) -> Any:
        """
        Forces an immediate re-render of the UI with current state.
        """
        merged_context = self.manager.merge_state(world_state)
        
        # Priority: Visage -> Root Component
        root = self._get_current_root(merged_context)
        
        if root:
            return self.renderer.render(root, merged_context)
        return {}

    def tick(self, events: List[Any], world_state: WorldState) -> Any:
        """
        Performs one frame of the Reflex Loop.
        """
        # 1. Handle Events (Stub)
        for event in events:
            pass
            
        # 2. Merge State
        merged_context = self.manager.merge_state(world_state)
        
        # 3. Render
        root = self._get_current_root(merged_context)
        
        if root:
            return self.renderer.render(root, merged_context)
            
        return {}
        
    def _get_current_root(self, context) -> Optional[Component]:
        if self.visage:
            return self.visage.render(context)
        return self.root_component
