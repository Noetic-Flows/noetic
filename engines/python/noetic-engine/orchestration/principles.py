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

    def evaluate_cost(self, action: Action, state: WorldState, principles: List[Principle]) -> float:
        """
        Evaluates the 'Moral Cost' of an action based on a list of Principles.
        Returns a float representing the cost penalty (or bonus).
        """
        if jsonLogic is None:
            return 0.0
            
        total_cost = 0.0
        
        context = {
            "action": action.model_dump(),
            "state": state.model_dump(),
            "tags": [] 
        }
        
        for principle in principles:
            try:
                result = jsonLogic(principle.logic, context)
                
                if isinstance(result, (int, float)):
                    total_cost += float(result)
                elif result is True:
                    pass
                
            except Exception as e:
                logger.error(f"Error evaluating principle {principle.id}: {e}")
                continue
                
        return total_cost