import pytest
from pydantic import ValidationError
from noetic_lang.core.stanza import StanzaDefinition, Step
from noetic_lang.core.agent import AgentDefinition, Principle
from noetic_lang.core.flow import FlowDefinition, FlowState

class TestCoreModels:
    
    def test_stanza_definition(self):
        """Test valid implementation of a Stanza."""
        stanza = StanzaDefinition(
            id="stanza_1",
            description="A test stanza",
            steps=[
                Step(id="s1", instruction="Do something")
            ]
        )
        assert stanza.id == "stanza_1"
        assert len(stanza.steps) == 1

    def test_agent_definition_types(self):
        """Test AgentDefinition validation, especially strictly typed Principles."""
        # Valid Agent
        agent = AgentDefinition(
            id="agent_1",
            system_prompt="You are a bot.",
            allowed_skills=["skill_a"],
            principles=[
                Principle(description="Be nice", threshold=0.9)
            ]
        )
        assert agent.principles[0].threshold == 0.9

        # Invalid Principle (passing a raw string instead of a Principle/dict)
        # Note: Pydantic might coalesce dicts into models, but strings should fail 
        # IF we change List[Any] to List[Principle]. 
        # Currently it is List[Any], so this test is expected to FAIL (assert logic) 
        # or PASS (if we test for failure and it doesn't fail).
        # TDD: We write the test expecting the Desired Behavior (it should fail).
        with pytest.raises(ValidationError):
            AgentDefinition(
                id="agent_2",
                system_prompt="Bot",
                allowed_skills=[],
                principles=["Not a principle object"] 
            )

    def test_flow_graph_integrity(self):
        """Test validation of Flow graph transitions."""
        # Valid Flow
        flow = FlowDefinition(
            id="flow_1",
            start_at="state_a",
            states={
                "state_a": FlowState(next="state_b"),
                "state_b": FlowState(end=True)
            }
        )
        assert flow.id == "flow_1"

        # Invalid: Transitions to unknown state
        with pytest.raises(ValueError, match="transitions to unknown state"):
            FlowDefinition(
                id="flow_bad",
                start_at="state_a",
                states={
                    "state_a": FlowState(next="non_existent_state")
                }
            )

        # Invalid: Start at unknown state
        with pytest.raises(ValueError, match="not found in states"):
            FlowDefinition(
                id="flow_bad_start",
                start_at="missing_start",
                states={
                    "state_a": FlowState(end=True)
                }
            )
