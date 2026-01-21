import pytest
from noetic_engine.orchestration.principles import PrincipleEngine
from noetic_engine.orchestration.agents import Principle
from noetic_engine.orchestration.schema import Action
from noetic_engine.knowledge import WorldState

def test_evaluate_cost_simple():
    engine = PrincipleEngine()
    
    p1 = Principle(
        id="safety", 
        description="Avoid danger", 
        logic={"if": [{"==": [{"var": "action.skill_id"}, "skill.danger"]}, 100, 0]}
    )
    
    safe_action = Action(skill_id="skill.safe")
    danger_action = Action(skill_id="skill.danger")
    
    state = WorldState(tick=0, entities={}, facts=[])
    
    cost_safe = engine.evaluate_cost(safe_action, state, [p1])
    cost_danger = engine.evaluate_cost(danger_action, state, [p1])
    
    assert cost_safe == 0
    assert cost_danger == 100

def test_malformed_logic_is_safe():
    engine = PrincipleEngine()
    p_bad = Principle(id="bad", description="...", logic={"broken": "syntax"})
    action = Action(skill_id="any")
    state = WorldState(tick=0, entities={}, facts=[])
    
    cost = engine.evaluate_cost(action, state, [p_bad])
    assert cost == 0.0