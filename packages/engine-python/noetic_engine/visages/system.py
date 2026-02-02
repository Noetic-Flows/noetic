from noetic_stage.visage import Visage
from noetic_stage.schema import Component, Column, Text
import time

class SystemDashboardVisage(Visage):
    def __init__(self, engine_ref):
        self.engine_ref = engine_ref

    def render(self, context: dict) -> Component:
        """
        Renders the System Dashboard, showing vital stats of the Noetic Engine.
        """
        subscribers = len(self.engine_ref.subscribers) if hasattr(self.engine_ref, 'subscribers') else 0
        
        return Column(
            children=[
                Text(content="Noetic Nexus OS - System Dashboard"),
                Text(content="--------------------------------"),
                Text(content=f"Engine Status: ONLINE"),
                Text(content=f"Connected Clients: {subscribers}"),
                Text(content=f"System Time: {time.time()}"),
                Text(content=f"Last Intent: {context.get('last_intent', 'None')}"),
                Text(content=f"Last Heartbeat: {context.get('last_intent_time', 'N/A')}")
            ]
        )
