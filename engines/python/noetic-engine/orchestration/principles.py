import logging
from typing import List, Dict, Any, Union
from .agents import Principle
from .schema import Action
from noetic_engine.knowledge import WorldState

# Try importing json_logic
try:
    from json_logic import jsonLogic
except ImportError:
    jsonLogic = None

logger = logging.getLogger(__name__)

class PrincipleEngine:
    def __init__(self):
        if jsonLogic is None:
            logger.warning("json-logic library not found. Principle evaluation will be disabled.")

    def evaluate_cost(self, action: Action, state: Union[WorldState, Dict[str, Any]], principles: List[Principle]) -> float:
        """
        Evaluates the 'Moral Cost' of an action based on a list of Principles.
        Returns a float representing the cost penalty (or bonus).
        """
        if jsonLogic is None:
            return 0.0
            
        total_cost = 0.0
        
        # Handle both WorldState object and Dict state from planner
        state_data = state.model_dump() if hasattr(state, "model_dump") else state
        
        context = {
            "action": action.model_dump(),
            "state": state_data,
            "tags": [] 
        }
        
        for principle in principles:
            try:
                result = jsonLogic(principle.logic, context)
                
                if isinstance(result, (int, float)):
                    total_cost += float(result)
                elif result is True:
                    # Boolean true might imply a violation (cost) or valid (0 cost)?
                    # Usually principles return cost penalty. If logic returns true, maybe default penalty?
                    # Or maybe principles define 'rules' where true = allowed?
                    # "Ensure it calculates 'Moral Cost'" implies numeric return.
                    # Let's assume boolean True means "violation detected" -> add default cost?
                    # Or "compliant" -> 0 cost.
                    # Let's stick to numeric accumulation for now, ignore boolean unless we define standard.
                    pass
                
            except Exception as e:
                logger.error(f"Error evaluating principle {principle.id}: {e}")
                continue
                
        return total_cost