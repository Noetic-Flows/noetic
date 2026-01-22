from typing import Any, Dict, Optional, List
import json_logic
from functools import lru_cache
import logging
from noetic_lang.core.agent import Principle

logger = logging.getLogger(__name__)

class Principles:
    def __init__(self, items: List[Principle]):
        self.items = items

class LogicEngine:
    """
    Wrapper around json-logic-qubit to provide safe, cached evaluation of Principles.
    """

    def __init__(self, safety_mode: str = "fail_closed"):
        """
        :param safety_mode: 'fail_closed' (default) returns MAX_INT on error. 'fail_open' returns 0.0.
        """
        self.safety_mode = safety_mode

    @lru_cache(maxsize=1024)
    def evaluate(self, rule_json_str: str, data_json_str: str) -> float:
        """
        Evaluates a JsonLogic rule against data.
        
        Args:
            rule_json_str: JSON string of the rule (for hashing/caching).
            data_json_str: JSON string of the data (for hashing/caching).
            
        Returns:
            float: The calculated cost.
        """
        try:
            rule =_json_loads_safe(rule_json_str)
            data = _json_loads_safe(data_json_str)
            
            result = json_logic.jsonLogic(rule, data)
            
            # Ensure result is a float
            if result is None:
                return 0.0
            if isinstance(result, bool):
                 return 1.0 if result else 0.0
            return float(result)

        except Exception as e:
            logger.error(f"Logic evaluation failed: {e}")
            if self.safety_mode == "fail_closed":
                return float("inf") # Using infinity for "MAX_INT" equivalent in float context
            else:
                return 0.0

def _json_loads_safe(s: str) -> Any:
    import json
    return json.loads(s)
