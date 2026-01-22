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
    def __init__(self, flow_definition: Dict[str, Any], skill_registry: Optional[Any] = None):
        self.flow_def = flow_definition
        self.skills = skill_registry
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
        # ... (rest of _build_graph same as before)


    def _make_node_func(self, name: str, state_def: Dict[str, Any]):
        async def node(state: Dict[str, Any]):
            trace = state.get("trace", [])
            new_trace = trace + [name]
            params = state_def.get("params", {})
            
            # Execute associated skill if any
            skill_id = state_def.get("skill")
            if skill_id and self.skills:
                skill = self.skills.get_skill(skill_id)
                if skill:
                    # Note: We need a SkillContext. 
                    # In a real flow run, this would be provided.
                    # For now, we inject a minimal one if possible.
                    ctx = state.get("_skill_context")
                    if ctx:
                        await skill.execute(ctx, **params)
            
            return {"trace": new_trace, **params}
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

    async def step(self, inputs: Dict[str, Any], state: WorldState) -> Dict[str, Any]:

        """

        Executes one step (or run) of the flow.

        """

        if not self.runnable:

            return {}

            

        # Inject WorldState into the flow state for logic evaluation

        inputs["_world_state"] = state 

        

        try:

            return await self.runnable.ainvoke(inputs)

        except Exception as e:

            logger.error(f"Error executing flow: {e}")

            return {}
