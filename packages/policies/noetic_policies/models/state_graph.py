"""State graph models."""

from pydantic import BaseModel, Field, field_validator

from noetic_policies.models import Transition


# T016: State Pydantic model
class State(BaseModel):
    """A node in the state graph representing a valid configuration."""

    name: str = Field(..., min_length=1, pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    preconditions: list[str] = Field(default_factory=list)
    transitions: list[Transition] = Field(default_factory=list)
    description: str | None = None


# T017: StateGraph Pydantic model
class StateGraph(BaseModel):
    """A directed graph of states and transitions representing all possible execution paths."""

    initial: str
    states: list[State] = Field(..., min_length=1)

    @field_validator("states")
    @classmethod
    def validate_unique_state_names(cls, v: list[State]) -> list[State]:
        """Ensure state names are unique."""
        names = [s.name for s in v]
        if len(names) != len(set(names)):
            duplicates = {name for name in names if names.count(name) > 1}
            raise ValueError(f"Duplicate state names: {duplicates}")
        return v

    @field_validator("initial")
    @classmethod
    def validate_initial_exists(cls, v: str, info: any) -> str:
        """Ensure initial state exists in states list."""
        if info.data.get("states"):
            state_names = {s.name for s in info.data["states"]}
            if v not in state_names:
                raise ValueError(f"Initial state '{v}' not found in states")
        return v
