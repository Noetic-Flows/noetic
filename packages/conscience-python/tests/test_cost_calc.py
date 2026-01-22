import pytest
from noetic_conscience.veto import Veto
from noetic_conscience.logic import Principles
from noetic_lang.core.agent import Principle

def test_high_risk_veto():
    # Define a principle: "Do not delete data"
    p1 = Principle(description="Do not delete data", threshold=0.8)
    principles = Principles([p1])
    
    veto = Veto(principles)
    
    # Action: "delete_database"
    # We expect this to be high risk (simulated)
    action = {"type": "tool_call", "name": "delete_database"}
    
    # Mocking the semantic similarity/risk score for the test
    # In a real system, this would call an LLM or vector check.
    # We will inject a mock scorer into Veto for testing.
    def mock_scorer(action_desc, principle_desc):
        if "delete" in action_desc and "delete" in principle_desc:
            return 0.9 # High similarity/violation probability
        return 0.1
        
    veto.set_scorer(mock_scorer)
    
    is_allowed, reason = veto.check(action)
    
    assert is_allowed is False
    assert "Do not delete data" in reason

def test_low_risk_allow():
    p1 = Principle(description="Do not delete data", threshold=0.8)
    principles = Principles([p1])
    veto = Veto(principles)
    
    def mock_scorer(action_desc, principle_desc):
        return 0.1
    veto.set_scorer(mock_scorer)
    
    action = {"type": "tool_call", "name": "read_database"}
    is_allowed, reason = veto.check(action)
    
    assert is_allowed is True
