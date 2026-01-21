import logging
from typing import Dict, Any, Optional, List
from noetic_engine.knowledge import WorldState

logger = logging.getLogger(__name__)

try:
    from langgraph.graph import StateGraph, END
except ImportError:
    StateGraph = None
    END = "END"

try:
    from json_logic import jsonLogic
except ImportError:
    jsonLogic = None

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
            node_func = self._make_node_func(name, state_def)
            workflow.add_node(name, node_func)
            
        # Add Edges
        for name, state_def in states.items():
            if "branches" in state_def:
                # Conditional edges
                branches = state_def["branches"]
                # Map potential destinations
                destinations = {b["next"]: b["next"] for b in branches}
                # If there is a default fallback?
                
                workflow.add_conditional_edges(
                    name,
                    self._make_router(branches),
                    destinations
                )
            elif "next" in state_def:
                workflow.add_edge(name, state_def["next"])
            elif state_def.get("end"):
                workflow.add_edge(name, END)
                
        if start_at:
            workflow.set_entry_point(start_at)
            
        return workflow

    def _make_node_func(self, name: str, state_def: Dict[str, Any]):
        def node(state: Dict[str, Any]):
            trace = state.get("trace", [])
            new_trace = trace + [name]
            outputs = state_def.get("params", {})
            
            # TODO: Execute associated skill if any
            
            return {"trace": new_trace, **outputs}
        return node

    def _make_router(self, branches: List[Dict[str, Any]]):
        def router(state: Dict[str, Any]):
            if jsonLogic is None:
                # Fallback: take first branch
                return branches[0]["next"]
                
            for branch in branches:
                condition = branch.get("condition", {})
                if jsonLogic(condition, state):
                    return branch["next"]
            
            # If no match, we should probably stop or go to error?
            # For now, return END or raise?
            # LangGraph expects one of the keys in conditional_edges map.
            # Assuming the last branch is default or we define behavior.
            return END 
        return router

    def step(self, inputs: Dict[str, Any], state: WorldState) -> Dict[str, Any]:
        """
        Executes one step (or run) of the flow.
        """
        if not self.runnable:
            return {}
            
        # Inject WorldState into the flow state for logic evaluation
        inputs["_world_state"] = state 
        
        try:
            return self.runnable.invoke(inputs)
        except Exception as e:
            logger.error(f"Error executing flow: {e}")
            return {}