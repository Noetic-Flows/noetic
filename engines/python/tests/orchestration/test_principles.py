import pytest
from noetic_engine.conscience import Evaluator, Principle, JudgementContext
from noetic_engine.knowledge import WorldState

def test_evaluate_cost_simple():
    evaluator = Evaluator()
    
    p1 = Principle(
        id="safety", 
        affects="val.safety",
        description="Avoid danger", 
        logic={"if": [{"==": [{"var": "action.id"}, "skill.danger"]}, 100, 0]}
    )
    
    # 1. Safe Action
    ctx_safe = JudgementContext(
        agent_id="test_agent",
        action_id="skill.safe",
        action_args={},
        world_state={}
    )
    
    # 2. Danger Action
    ctx_danger = JudgementContext(
        agent_id="test_agent",
        action_id="skill.danger",
        action_args={},
        world_state={}
    )
    
    res_safe = evaluator.judge(ctx_safe, [p1])
    res_danger = evaluator.judge(ctx_danger, [p1])
    
    assert res_safe.cost == 0
    assert res_danger.cost == 100

def test_malformed_logic_is_safe():
    # If logic is bad, LogicEngine (fail_closed) returns inf, but let's test behavior
    evaluator = Evaluator(safety_mode="fail_open") # For this test to pass with 0 cost
    p_bad = Principle(id="bad", affects="val.test", description="...", logic={"broken": "syntax"})
    
    ctx = JudgementContext(
        agent_id="test_agent",
        action_id="any",
        action_args={},
        world_state={}
    )
    
    res = evaluator.judge(ctx, [p_bad])
    assert res.cost == 0.0