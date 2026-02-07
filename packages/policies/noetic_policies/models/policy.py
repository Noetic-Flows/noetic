"""Policy models."""

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from noetic_policies.models import GoalState, Invariant, TemporalBounds
from noetic_policies.models.constraint import Constraint
from noetic_policies.models.state_graph import StateGraph


# T018: Policy Pydantic model
class Policy(BaseModel):
    """A complete policy specification including metadata, constraints, state graph, invariants, and goals."""

    version: str = Field(..., pattern=r"^\d+\.\d+$")
    cel_mode: str = Field(default="safe", pattern=r"^(safe|full|extended)$")
    name: str | None = None
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    state_schema: dict[str, str] = Field(..., min_length=1)
    constraints: list[Constraint] = Field(..., min_length=1)
    state_graph: StateGraph
    invariants: list[Invariant] = Field(default_factory=list)
    goal_states: list[GoalState] = Field(default_factory=list)
    temporal_bounds: TemporalBounds | None = None

    @field_validator("goal_states")
    @classmethod
    def validate_goal_states_exist(cls, v: list[GoalState], info: any) -> list[GoalState]:
        """Ensure goal states exist in state graph."""
        if v and info.data.get("state_graph"):
            state_names = {s.name for s in info.data["state_graph"].states}
            goal_names = {g.name for g in v}
            invalid_goals = goal_names - state_names
            if invalid_goals:
                raise ValueError(f"Goal states not in state graph: {invalid_goals}")
        return v

    @model_validator(mode="after")
    def validate_temporal_bounds_hierarchy(self) -> "Policy":
        """Goal-level temporal bounds must not exceed policy-level temporal bounds (FR-008h)."""
        if self.temporal_bounds is None:
            return self

        for goal in self.goal_states:
            if goal.temporal_bounds is None:
                continue

            # Check max_steps
            if (
                self.temporal_bounds.max_steps is not None
                and goal.temporal_bounds.max_steps is not None
                and goal.temporal_bounds.max_steps > self.temporal_bounds.max_steps
            ):
                raise ValueError(
                    f"Goal '{goal.name}' max_steps ({goal.temporal_bounds.max_steps}) "
                    f"exceeds policy max_steps ({self.temporal_bounds.max_steps})"
                )

            # Check timeout_seconds
            if (
                self.temporal_bounds.timeout_seconds is not None
                and goal.temporal_bounds.timeout_seconds is not None
                and goal.temporal_bounds.timeout_seconds
                > self.temporal_bounds.timeout_seconds
            ):
                raise ValueError(
                    f"Goal '{goal.name}' timeout_seconds ({goal.temporal_bounds.timeout_seconds}) "
                    f"exceeds policy timeout_seconds ({self.temporal_bounds.timeout_seconds})"
                )

        return self

    @field_validator("state_schema")
    @classmethod
    def validate_state_schema_types(cls, v: dict[str, str]) -> dict[str, str]:
        """Validate that state schema types are valid."""
        valid_types = {"number", "string", "boolean", "address"}
        for field_name, field_type in v.items():
            # Handle enum types: enum[value1,value2,...]
            if field_type.startswith("enum[") and field_type.endswith("]"):
                continue
            if field_type not in valid_types:
                raise ValueError(f"Invalid type '{field_type}' for field '{field_name}'")
        return v
