from datetime import datetime
import math
from ..store.schema import Fact

class Nexus:
    def __init__(self):
        pass

    def score_fact(self, fact: Fact, query: str = None) -> float:
        """
        Calculates the relevance score of a fact based on Recency and Confidence.
        Score = Recency * Confidence
        """
        # 1. Recency Decay (Exponential)
        # We assume 'valid_from' is UTC.
        now = datetime.utcnow()
        if fact.valid_from > now:
             # Future facts (clock skew?) are treated as now
             age = 0
        else:
            age = (now - fact.valid_from).total_seconds() / 3600.0 # Age in hours
            
        # Decay: Value drops to ~37% after 24 hours
        recency = math.exp(-age / 24.0) 
        
        # 2. Confidence
        confidence = fact.confidence
        
        # 3. Semantic (Placeholder)
        # In a real system, we'd compare query vector with fact vector.
        semantic = 1.0
        
        return recency * confidence * semantic
