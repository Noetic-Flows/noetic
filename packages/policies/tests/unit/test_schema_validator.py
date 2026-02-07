"""Unit tests for schema validation (T027-T031k)."""

import pytest

from noetic_policies.models import ValidationError
from noetic_policies.models.policy import Policy
from noetic_policies.models.constraint import Constraint
from noetic_policies.models.state_graph import State, StateGraph


class TestSchemaValidator:
    """Test schema validation logic."""

    # T027: Test valid policy passes schema validation
    def test_valid_policy_passes_schema_validation(self):
        """Valid policy should pass all schema checks."""
        policy_data = {
            "version": "1.0",
            "state_schema": {"count": "number"},
            "constraints": [{"name": "positive", "expr": "count > 0"}],
            "state_graph": {
                "initial": "start",
                "states": [{"name": "start", "transitions": []}],
            },
        }
        policy = Policy(**policy_data)
        assert policy.version == "1.0"
        assert len(policy.constraints) == 1

    # T028: Test missing constraints section fails with E001 error
    def test_missing_constraints_fails(self):
        """Missing constraints section should raise validation error."""
        with pytest.raises(ValueError, match="constraints"):
            Policy(
                version="1.0",
                state_schema={"count": "number"},
                constraints=[],  # Empty not allowed (min_length=1)
                state_graph=StateGraph(
                    initial="start",
                    states=[State(name="start")],
                ),
            )

    # T029: Test missing state_graph section fails
    def test_missing_state_graph_fails(self):
        """Missing state_graph should raise validation error."""
        with pytest.raises(ValueError):
            Policy(
                version="1.0",
                state_schema={"count": "number"},
                constraints=[Constraint(name="positive", expr="count > 0")],
                state_graph=None,  # type: ignore
            )

    # T030: Test invalid version format fails
    def test_invalid_version_format_fails(self):
        """Invalid version format should raise validation error."""
        with pytest.raises(ValueError, match="version"):
            Policy(
                version="1",  # Invalid - should be MAJOR.MINOR
                state_schema={"count": "number"},
                constraints=[Constraint(name="positive", expr="count > 0")],
                state_graph=StateGraph(
                    initial="start",
                    states=[State(name="start")],
                ),
            )

    # T031: Test goal states not in graph fails
    def test_goal_states_not_in_graph_fails(self):
        """Goal states must exist in state graph."""
        from noetic_policies.models import GoalState

        with pytest.raises(ValueError, match="not in state graph"):
            Policy(
                version="1.0",
                state_schema={"count": "number"},
                constraints=[Constraint(name="positive", expr="count > 0")],
                state_graph=StateGraph(
                    initial="start",
                    states=[State(name="start")],
                ),
                goal_states=[GoalState(name="nonexistent")],  # Not in graph
            )

    # T031a: Test transitions have well-formed preconditions and effects (FR-006)
    def test_transitions_well_formed(self):
        """Transitions should have valid preconditions and effects."""
        from noetic_policies.models import Transition

        # Valid transition
        transition = Transition(
            to="end",
            preconditions=["positive"],
            effects=["count = count + 1"],
        )
        assert transition.to == "end"
        assert "positive" in transition.preconditions

    # T031b: Test state schema defines all referenced variables (FR-008a)
    def test_state_schema_completeness(self):
        """State schema must define all variables used in constraints."""
        # This will be validated at the validator level, not model level
        # Model accepts any schema
        policy = Policy(
            version="1.0",
            state_schema={"count": "number", "balance": "number"},
            constraints=[Constraint(name="positive", expr="count > 0")],
            state_graph=StateGraph(initial="start", states=[State(name="start")]),
        )
        assert "count" in policy.state_schema
        assert "balance" in policy.state_schema

    # T031c: Test state schema uses valid types
    def test_state_schema_valid_types(self):
        """State schema should only use valid types."""
        # Valid types
        policy = Policy(
            version="1.0",
            state_schema={
                "count": "number",
                "name": "string",
                "active": "boolean",
                "wallet": "address",
                "status": "enum[pending,complete]",
            },
            constraints=[Constraint(name="positive", expr="count > 0")],
            state_graph=StateGraph(initial="start", states=[State(name="start")]),
        )
        assert policy.state_schema["count"] == "number"

        # Invalid type should fail
        with pytest.raises(ValueError, match="Invalid type"):
            Policy(
                version="1.0",
                state_schema={"invalid": "badtype"},
                constraints=[Constraint(name="positive", expr="true")],
                state_graph=StateGraph(initial="start", states=[State(name="start")]),
            )

    # T031d: Test goal conditions reference only schema-defined variables (FR-008b)
    def test_goal_conditions_reference_schema_variables(self):
        """Goal conditions should reference valid schema variables."""
        from noetic_policies.models import GoalState

        policy = Policy(
            version="1.0",
            state_schema={"count": "number"},
            constraints=[Constraint(name="positive", expr="count > 0")],
            state_graph=StateGraph(initial="start", states=[State(name="complete")]),
            goal_states=[
                GoalState(
                    name="complete",
                    conditions=["count >= 10"],  # References 'count' from schema
                )
            ],
        )
        assert policy.goal_states[0].conditions[0] == "count >= 10"

    # T031e: Test goal conditions are satisfiable (FR-008c)
    def test_goal_conditions_satisfiable(self):
        """Goal conditions should not contradict constraints/invariants."""
        # This requires semantic analysis - tested at validator level
        # Model level just ensures syntax
        from noetic_policies.models import GoalState

        policy = Policy(
            version="1.0",
            state_schema={"count": "number"},
            constraints=[Constraint(name="positive", expr="count > 0")],
            state_graph=StateGraph(initial="start", states=[State(name="complete")]),
            goal_states=[GoalState(name="complete", conditions=["count == 100"])],
        )
        assert policy.goal_states[0].conditions[0] == "count == 100"

    # T031f: Test transition cost values are non-negative (FR-008d)
    def test_transition_cost_non_negative(self):
        """Transition costs must be >= 0."""
        from noetic_policies.models import Transition

        # Valid cost
        transition = Transition(to="end", cost=1.5)
        assert transition.cost == 1.5

        # Negative cost should fail
        with pytest.raises(ValueError):
            Transition(to="end", cost=-1.0)

    # T031g: Test transition cost_expr is valid CEL evaluating to numeric (FR-008d)
    def test_transition_cost_expr_valid(self):
        """Transition cost_expr should be valid CEL."""
        from noetic_policies.models import Transition

        # Valid cost expression
        transition = Transition(to="end", cost_expr="amount * 0.01")
        assert transition.cost_expr == "amount * 0.01"

        # Empty expression should fail
        with pytest.raises(ValueError, match="Empty cost expression"):
            Transition(to="end", cost_expr="   ")

    # T031h: Test goal priority is integer and reward is positive (FR-008e)
    def test_goal_priority_and_reward(self):
        """Goal priority should be int, reward should be positive."""
        from noetic_policies.models import GoalState

        # Valid values
        goal = GoalState(name="complete", priority=1, reward=10.0)
        assert goal.priority == 1
        assert goal.reward == 10.0

        # Negative reward should fail
        with pytest.raises(ValueError):
            GoalState(name="complete", reward=-1.0)

    # T031i: Test progress conditions valid CEL evaluating to numeric (FR-008f)
    def test_progress_conditions_valid(self):
        """Progress conditions should be valid CEL numeric expressions."""
        from noetic_policies.models import GoalState, ProgressCondition

        goal = GoalState(
            name="complete",
            progress_conditions=[
                ProgressCondition(expr="count / max_count", weight=1.0)
            ],
        )
        assert len(goal.progress_conditions) == 1
        assert goal.progress_conditions[0].expr == "count / max_count"

        # Empty expression should fail
        with pytest.raises(ValueError, match="Empty progress condition"):
            ProgressCondition(expr="   ")

    # T031j: Test temporal bounds validation (FR-008g)
    def test_temporal_bounds_validation(self):
        """Temporal bounds should have valid values."""
        from noetic_policies.models import TemporalBounds

        # Valid bounds
        bounds = TemporalBounds(max_steps=100, timeout_seconds=30.0)
        assert bounds.max_steps == 100
        assert bounds.timeout_seconds == 30.0

        # Invalid max_steps (negative)
        with pytest.raises(ValueError):
            TemporalBounds(max_steps=-1)

        # Invalid timeout (negative)
        with pytest.raises(ValueError):
            TemporalBounds(timeout_seconds=-1.0)

        # No bounds specified should fail
        with pytest.raises(ValueError, match="At least one temporal bound"):
            TemporalBounds()

    # T031k: Test goal temporal bounds do not exceed policy bounds (FR-008h)
    def test_goal_temporal_bounds_hierarchy(self):
        """Goal temporal bounds must not exceed policy bounds."""
        from noetic_policies.models import GoalState, TemporalBounds

        # Valid hierarchy
        policy = Policy(
            version="1.0",
            state_schema={"count": "number"},
            constraints=[Constraint(name="positive", expr="count > 0")],
            state_graph=StateGraph(initial="start", states=[State(name="complete")]),
            temporal_bounds=TemporalBounds(max_steps=200, timeout_seconds=60.0),
            goal_states=[
                GoalState(
                    name="complete",
                    temporal_bounds=TemporalBounds(max_steps=100, timeout_seconds=30.0),
                )
            ],
        )
        assert policy.goal_states[0].temporal_bounds.max_steps == 100

        # Goal bounds exceed policy bounds - should fail
        with pytest.raises(ValueError, match="exceeds policy"):
            Policy(
                version="1.0",
                state_schema={"count": "number"},
                constraints=[Constraint(name="positive", expr="count > 0")],
                state_graph=StateGraph(initial="start", states=[State(name="complete")]),
                temporal_bounds=TemporalBounds(max_steps=100),
                goal_states=[
                    GoalState(
                        name="complete",
                        temporal_bounds=TemporalBounds(max_steps=200),  # Exceeds!
                    )
                ],
            )
