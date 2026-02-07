"""Constraint models."""

from pydantic import BaseModel, Field, field_validator


# T013: Constraint Pydantic model
class Constraint(BaseModel):
    """A logical expression that must evaluate to true for a transition or state to be valid."""

    name: str = Field(..., min_length=1, pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    expr: str = Field(..., min_length=1)
    description: str | None = None
    severity: str = Field(default="error", pattern=r"^(error|warning)$")

    @field_validator("expr")
    @classmethod
    def validate_cel_syntax(cls, v: str) -> str:
        """Validate CEL expression syntax (actual validation performed during validation phase)."""
        # CEL syntax validation performed during validation phase
        return v
