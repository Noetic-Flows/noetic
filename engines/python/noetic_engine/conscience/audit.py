import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Records the 'Why' behind Conscience decisions.
    """
    
    def log_judgement(self, 
                      action_id: str, 
                      total_cost: float, 
                      contributing_principles: List[Dict[str, Any]]):
        """
        Logs the outcome of a judgement.
        
        Args:
            action_id: The ID of the action being judged.
            total_cost: The aggregated cost.
            contributing_principles: List of principles that added cost.
                                     Format: [{'id': str, 'cost': float, 'rationale': str}]
        """
        
        # Telemetry Stub (Replace with OTel span events later)
        if contributing_principles:
            logger.info(f"Judgement for '{action_id}': Cost={total_cost}")
            for entry in contributing_principles:
                logger.debug(f"  + {entry['id']}: {entry['cost']}")
        else:
            logger.debug(f"Judgement for '{action_id}': Cost={total_cost} (Clean)")

    def log_violation(self, principle_id: str, reason: str):
        """
        Logs a hard veto.
        """
        logger.warning(f"VETO TRIGGERED by '{principle_id}': {reason}")
