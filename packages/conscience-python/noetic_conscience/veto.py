from typing import List, Dict, Any, Callable, Tuple
from .logic import Principles

class PolicyViolationError(Exception):
    """
    Raised when an action violates a hard constraint (cost is INFINITY).
    """
    def __init__(self, principle_id: str, reason: str, context: Dict[str, Any]):
        self.principle_id = principle_id
        self.reason = reason
        self.context = context
        super().__init__(f"Policy Violation by '{principle_id}': {reason}")

class Veto:
    def __init__(self, principles: Principles):
        self.principles = principles
        self.scorer = None

    def set_scorer(self, scorer: Callable[[str, str], float]):
        self.scorer = scorer

    def check(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        if not self.scorer:
            return True, "No scorer set"
            
        action_desc = action.get("name", str(action))
        
        for principle in self.principles.items:
            score = self.scorer(action_desc, principle.description)
            if score >= principle.threshold:
                return False, f"Violated principle: {principle.description}"
                
        return True, "Allowed"

class VetoSwitch:
    """
    Checks for hard-stop conditions in judgement results.
    """
    
    @staticmethod
    def check(cost: float, principle_id: str, context: Dict[str, Any]):
        """
        If cost is infinite, raise PolicyViolationError.
        """
        if cost == float("inf"):
            raise PolicyViolationError(
                principle_id=principle_id,
                reason="Principle evaluated to INFINITY (Hard Veto)",
                context=context
            )
