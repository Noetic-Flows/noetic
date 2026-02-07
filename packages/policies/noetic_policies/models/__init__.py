"""Core data models for noetic-policies package."""

from dataclasses import dataclass
from typing import Any

__all__ = [
    "ValidationError",
    "ValidationResult",
    "GraphAnalysisResult",
    "Invariant",
    "Transition",
    "ProgressCondition",
    "TemporalBounds",
    "GoalState",
]


# T009: ValidationError dataclass
@dataclass
class ValidationError:
    """Structured validation error with actionable information (SC-003: 90% fixable without docs)."""

    code: str
    message: str
    line_number: int | None = None
    column_number: int | None = None
    severity: str = "error"
    fix_suggestion: str | None = None
    documentation_url: str | None = None

    def format(self) -> str:
        """Format error message for display."""
        parts = []
        if self.line_number:
            parts.append(f"Line {self.line_number}")
            if self.column_number:
                parts.append(f", Column {self.column_number}")
            parts.append(": ")

        parts.append(f"{self.severity.upper()} [{self.code}]: {self.message}")

        if self.fix_suggestion:
            parts.append(f"\n  Suggestion: {self.fix_suggestion}")

        if self.documentation_url:
            parts.append(f"\n  See: {self.documentation_url}")

        return "".join(parts)


# T010: ValidationResult dataclass
@dataclass
class ValidationResult:
    """Results from policy validation, including errors, warnings, and metadata."""

    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationError]
    metadata: dict[str, Any]


# T011: GraphAnalysisResult dataclass
@dataclass
class GraphAnalysisResult:
    """Results from state graph static analysis, including cost-aware pathfinding and temporal feasibility."""

    unreachable_states: set[str]
    deadlock_sccs: list[set[str]]
    goal_reachable: bool
    cycles: list[list[str]] | None = None
    goal_costs: dict[str, float] | None = None
    goal_min_steps: dict[str, int] | None = None
    temporally_infeasible_goals: list[str] | None = None


# T014: Invariant Pydantic model
from pydantic import BaseModel, Field


class Invariant(BaseModel):
    """A logical expression that must remain true throughout policy execution."""

    name: str | None = None
    expr: str = Field(..., min_length=1)
    description: str | None = None


# T015: Transition Pydantic model
class Transition(BaseModel):
    """An edge in the state graph connecting two states."""

    to: str
    preconditions: list[str] = Field(default_factory=list)
    effects: list[str] = Field(default_factory=list)
    cost: float = Field(default=1.0, ge=0.0)
    cost_expr: str | None = None
    description: str | None = None

    @classmethod
    def validate_cost_expr_syntax(cls, v: str | None) -> str | None:
        """Validate cost expression syntax."""
        if v is not None and not v.strip():
            raise ValueError("Empty cost expression not allowed")
        return v


# T015a: ProgressCondition Pydantic model
class ProgressCondition(BaseModel):
    """CEL expression evaluating to 0.0-1.0 indicating proximity to goal satisfaction."""

    expr: str = Field(..., min_length=1)
    weight: float = Field(default=1.0, gt=0.0)
    description: str | None = None

    @classmethod
    def validate_expr_syntax(cls, v: str) -> str:
        """Validate expression syntax."""
        if not v.strip():
            raise ValueError("Empty progress condition expression not allowed")
        return v


# T015b: TemporalBounds Pydantic model
from pydantic import model_validator


class TemporalBounds(BaseModel):
    """Time and step constraints that limit policy or goal execution."""

    max_steps: int | None = Field(default=None, gt=0)
    deadline: str | None = None
    timeout_seconds: float | None = Field(default=None, gt=0.0)
    description: str | None = None

    @model_validator(mode="after")
    def validate_at_least_one_bound(self) -> "TemporalBounds":
        """Ensure at least one bound is specified."""
        if (
            self.max_steps is None
            and self.deadline is None
            and self.timeout_seconds is None
        ):
            raise ValueError(
                "At least one temporal bound must be specified (max_steps, deadline, or timeout_seconds)"
            )
        return self

    @classmethod
    def validate_deadline_syntax(cls, v: str | None) -> str | None:
        """Validate deadline expression syntax."""
        if v is not None and not v.strip():
            raise ValueError("Empty deadline expression not allowed")
        return v


# T015c: GoalState Pydantic model
class GoalState(BaseModel):
    """A target abstract state with goal conditions, scoring metadata, and temporal bounds."""

    name: str = Field(..., min_length=1, pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    conditions: list[str] = Field(default_factory=list)
    priority: int = Field(default=0)
    reward: float = Field(default=1.0, gt=0.0)
    progress_conditions: list[ProgressCondition] = Field(default_factory=list)
    temporal_bounds: TemporalBounds | None = None
    description: str | None = None

    @classmethod
    def validate_conditions_syntax(cls, v: list[str]) -> list[str]:
        """Validate goal conditions syntax."""
        for condition in v:
            if not condition.strip():
                raise ValueError("Empty goal condition not allowed")
        return v
