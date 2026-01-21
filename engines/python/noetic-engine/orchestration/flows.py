import logging
from typing import Dict, Any, Optional
from noetic_engine.knowledge import WorldState

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, END
except ImportError:
    StateGraph = None
    END = "END"

class FlowExecutor:
    """
    Wraps LangGraph to execute deterministic state machines defined in the Codex.
    """
    def __init__(self, flow_definition: Dict[str, Any]):
        self.flow_def = flow_definition
        self.graph = self._build_graph(flow_definition)
        self.runnable = self.graph.compile() if self.graph else None

    def _build_graph(self, definition: Dict[str, Any]):
        if StateGraph is None:
            logger.warning("LangGraph not found. Flows will not execute.")
            return None
        
        workflow = StateGraph(dict)
        
        start_at = definition.get("start_at")
        states = definition.get("states", {})
        
        for name, state_def in states.items():
            # Create a node for each state
            # For now, we create a simple node that records its execution
            node_func = self._make_node_func(name, state_def)
            workflow.add_node(name, node_func)
            
        # Add Edges
        for name, state_def in states.items():
            if state_def.get("end"):
                workflow.add_edge(name, END)
            elif "next" in state_def:
                workflow.add_edge(name, state_def["next"])
                
        if start_at:
            workflow.set_entry_point(start_at)
            
        return workflow

    def _make_node_func(self, name: str, state_def: Dict[str, Any]):
        def node(state: Dict[str, Any]):
            # Minimal implementation: record visit
            # In future, execute 'skill' defined in state_def
            trace = state.get("trace", [])
            new_trace = trace + [name]
            
            # Merge output or params (mock behavior)
            outputs = state_def.get("params", {})
            
            return {"trace": new_trace, **outputs}
        return node

    def step(self, inputs: Dict[str, Any], state: WorldState) -> Dict[str, Any]:
        """
        Executes one step (or run) of the flow.
        """
        if not self.runnable:
            return {}
            
        inputs["_world_state"] = state 
        
        try:
            return self.runnable.invoke(inputs)
        except Exception as e:
            logger.error(f"Error executing flow: {e}")
            return {}