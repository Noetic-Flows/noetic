import pytest
from pydantic import ValidationError
from noetic_lang.core.flow import FlowDefinition, FlowState
from noetic_lang.core.stanza import StanzaDefinition, Step
from noetic_lang.core.agent import AgentDefinition, Principle

def test_flow_definition_invalid_start_at():
    # Test case where 'start_at' refers to a non-existent state
    invalid_data = {
        "id": "test_flow",
        "start_at": "non_existent_state",
        "states": {
            "state1": {
                "name": "state1",
                "skill": "skill1",
                "next": "state2"
            },
            "state2": {
                "name": "state2",
                "skill": "skill2"
            }
        }
    }
    with pytest.raises(ValidationError) as excinfo:
        FlowDefinition(**invalid_data)
    assert "start_at 'non_existent_state' not found in states" in str(excinfo.value)

def test_flow_definition_invalid_next_state():
    # Test case where 'next' refers to a non-existent state
    invalid_data = {
        "id": "test_flow",
        "start_at": "state1",
        "states": {
            "state1": {
                "name": "state1",
                "next": "non_existent_state"
            }
        }
    }
    with pytest.raises(ValidationError) as excinfo:
        FlowDefinition(**invalid_data)
    assert "State 'state1' transitions to unknown state 'non_existent_state'" in str(excinfo.value)

def test_flow_definition_missing_required_fields():
    # Test case with missing 'id'
    invalid_data = {
        "start_at": "state1",
        "states": {
            "state1": {
                "name": "state1"
            }
        }
    }
    with pytest.raises(ValidationError):
        FlowDefinition(**invalid_data)

    # Test case with missing 'start_at'
    invalid_data = {
        "id": "test_flow",
        "states": {
            "state1": {
                "name": "state1"
            }
        }
    }
    with pytest.raises(ValidationError):
        FlowDefinition(**invalid_data)

    # Test case with missing 'states'
    invalid_data = {
        "id": "test_flow",
        "start_at": "state1",
    }
    with pytest.raises(ValidationError):
        FlowDefinition(**invalid_data)

def test_stanza_definition_validation():
    # Valid case
    valid_data = {
        "id": "research_stanza",
        "description": "Research a topic",
        "steps": [
            {"id": "step1", "instruction": "Search Google"},
            {"id": "step2", "instruction": "Summarize"}
        ]
    }
    stanza = StanzaDefinition(**valid_data)
    assert stanza.id == "research_stanza"
    assert len(stanza.steps) == 2

    # Invalid case: missing steps
    invalid_data = {
        "id": "research_stanza",
        "description": "Research a topic"
    }
    with pytest.raises(ValidationError):
        StanzaDefinition(**invalid_data)

    # Invalid case: step missing instruction
    invalid_data = {
        "id": "research_stanza",
        "description": "Research a topic",
        "steps": [
            {"id": "step1"}
        ]
    }
    with pytest.raises(ValidationError):
        StanzaDefinition(**invalid_data)

def test_agent_definition_validation():
    # Valid case
    valid_data = {
        "id": "researcher",
        "system_prompt": "You are a researcher.",
        "allowed_skills": ["search", "read"],
        "principles": [
            {"description": "Be accurate", "threshold": 0.9}
        ]
    }
    agent = AgentDefinition(**valid_data)
    assert agent.id == "researcher"
    assert len(agent.principles) == 1

    # Invalid case: missing system_prompt
    invalid_data = {
        "id": "researcher",
        "allowed_skills": [],
        "principles": []
    }
    with pytest.raises(ValidationError):
        AgentDefinition(**invalid_data)