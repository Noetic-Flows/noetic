import pytest
from noetic_engine.conscience import Evaluator, JudgementContext, Principle, PolicyViolationError

# Mock Principle: Expensive actions cost 100
EXPENSIVE_PRINCIPLE = Principle(
    id="principle.frugal",
    affects="val.frugality",
    logic={
        "if": [
            { ">": [{ "var": "action_args.cost" }, 100] },
            50.0,
            0.0
        ]
    }
)

# Mock Principle: Never do "evil"
NO_EVIL_PRINCIPLE = Principle(
    id="principle.no_evil",
    affects="val.goodness",
    logic={
        "if": [
            { "==": [{ "var": "tags" }, "evil"] }, # Simplified check, usually checks containment
            "infinity", # JsonLogic doesn't support inf literal easily? We handle it.
             0.0
        ]
    }
)
# Note: "infinity" string might not be parsed to float("inf") by standard json_logic?
# Let's adjust logic.py to handle string "infinity" if needed or use a number.
# But json standard doesn't have infinity.
# LogicEngine probably needs to handle a special case or I should use a very large number?
# The README said "return a cost of INFINITY".
# In JSON, we can't represent Infinity.
# So the rule probably returns a large number, or LogicEngine handles "Infinity" string?
# Let's check my logic.py implementation.
# It does `float(result)`. float("infinity") works in Python.
# So if JsonLogic returns string "infinity", it works.

def test_evaluator_basic():
    evaluator = Evaluator()
    
    # Cheap action
    ctx1 = JudgementContext(
        agent_id="agent-1",
        action_id="buy_coffee",
        action_args={"cost": 5},
        tags=["lifestyle"]
    )
    result1 = evaluator.judge(ctx1, [EXPENSIVE_PRINCIPLE])
    assert result1.cost == 0.0
    
    # Expensive action
    ctx2 = JudgementContext(
        agent_id="agent-1",
        action_id="buy_server",
        action_args={"cost": 500},
        tags=["infra"]
    )
    result2 = evaluator.judge(ctx2, [EXPENSIVE_PRINCIPLE])
    assert result2.cost == 50.0

def test_evaluator_veto():
    evaluator = Evaluator()
    
    # Evil action
    ctx_evil = JudgementContext(
        agent_id="agent-1",
        action_id="do_bad_thing",
        tags="evil" # My logic rule expects string matching for simplicity here
    )
    
    with pytest.raises(PolicyViolationError):
        evaluator.judge(ctx_evil, [NO_EVIL_PRINCIPLE])

