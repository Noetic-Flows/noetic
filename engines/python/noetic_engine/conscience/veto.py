from typing import List, Dict, Any

class PolicyViolationError(Exception):
    """
    Raised when an action violates a hard constraint (cost is INFINITY).
    """
    def __init__(self, principle_id: str, reason: str, context: Dict[str, Any]):
        self.principle_id = principle_id
        self.reason = reason
        self.context = context
        super().__init__(f"Policy Violation by '{principle_id}': {reason}")

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
