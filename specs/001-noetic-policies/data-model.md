# Data Model: Noetic Policies Package

**Feature**: Build the noetic-policies package
**Branch**: 001-noetic-policies
**Date**: 2026-02-05

## Overview

This document defines the data models for the noetic-policies package. All models use Pydantic for validation and type safety (mypy strict mode compliance per constitution).

---

## Core Entities

### Policy

**Description**: A complete policy specification including metadata, constraints, state graph, invariants, and goal state. Represents the declarative "what" that governs agent or contract behavior.

**Attributes**:
- `version` (str, required): Policy format version (e.g., "1.0"). Used for compatibility checking and migration.
- `cel_mode` (str, optional): CEL evaluation mode - "safe" (default), "full", or "extended". Determines which CEL operations are allowed in constraint expressions.
- `name` (str, optional): Human-readable policy name
- `description` (str, optional): Policy purpose and context
- `metadata` (dict[str, Any], optional): Additional metadata (author, created_at, tags, etc.)
- `state_schema` (dict[str, str], required): Defines state variables and their types (e.g., {"balance": "number", "status": "enum[pending,complete]"})
- `constraints` (list[Constraint], required): List of constraint definitions
- `state_graph` (StateGraph, required): State machine definition
- `invariants` (list[Invariant], optional): Global invariants that must hold throughout execution
- `goal_states` (list[GoalState], optional): Target states with optional goal conditions representing successful completion

**Validation Rules**:
- Version must match supported format (current or current-1)
- At least one constraint must be defined
- State graph must be complete and valid
- Goal states (if specified) must exist in state graph

**Pydantic Model**:
```python
from pydantic import BaseModel, Field, field_validator
from typing import Any

class Policy(BaseModel):
    version: str = Field(..., pattern=r'^\d+\.\d+$')
    cel_mode: str = Field(default="safe", pattern=r'^(safe|full|extended)$')
    name: str | None = None
    description: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    state_schema: dict[str, str] = Field(..., min_length=1)
    constraints: list[Constraint] = Field(..., min_length=1)
    state_graph: StateGraph
    invariants: list[Invariant] = Field(default_factory=list)
    goal_states: list[GoalState] = Field(default_factory=list)

    @field_validator('goal_states')
    @classmethod
    def validate_goal_states_exist(cls, v, info):
        if v and info.data.get('state_graph'):
            state_names = {s.name for s in info.data['state_graph'].states}
            goal_names = {g.name for g in v}
            invalid_goals = goal_names - state_names
            if invalid_goals:
                raise ValueError(f"Goal states not in state graph: {invalid_goals}")
        return v

    @field_validator('state_schema')
    @classmethod
    def validate_state_schema_types(cls, v):
        valid_types = {"number", "string", "boolean", "address"}
        for field_name, field_type in v.items():
            # Handle enum types: enum[value1,value2,...]
            if field_type.startswith("enum[") and field_type.endswith("]"):
                continue
            if field_type not in valid_types:
                raise ValueError(f"Invalid type '{field_type}' for field '{field_name}'")
        return v
```

---

### Constraint

**Description**: A logical expression that must evaluate to true for a transition or state to be valid. Uses CEL expression syntax and references policy variables.

**Attributes**:
- `name` (str, required): Unique constraint identifier (used in preconditions)
- `expr` (str, required): CEL expression that evaluates to boolean
- `description` (str, optional): Human-readable explanation
- `severity` (str, optional): "error" (default) or "warning"

**Validation Rules**:
- Name must be unique within policy
- Expression must be valid CEL syntax
- Expression must evaluate to boolean type

**Pydantic Model**:
```python
class Constraint(BaseModel):
    name: str = Field(..., min_length=1, pattern=r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    expr: str = Field(..., min_length=1)
    description: str | None = None
    severity: str = Field(default="error", pattern=r'^(error|warning)$')

    @field_validator('expr')
    @classmethod
    def validate_cel_syntax(cls, v):
        # CEL syntax validation performed during validation phase
        return v
```

---

### StateGraph

**Description**: A directed graph of states and transitions representing all possible execution paths. Each state has optional preconditions, each transition has optional effects.

**Attributes**:
- `initial` (str, required): Name of the initial state
- `states` (list[State], required): List of all states in the graph

**Validation Rules**:
- Initial state must exist in states list
- At least one state must be defined
- State names must be unique
- Graph must be connected (all states reachable from initial)

**Pydantic Model**:
```python
class StateGraph(BaseModel):
    initial: str
    states: list[State] = Field(..., min_length=1)

    @field_validator('states')
    @classmethod
    def validate_unique_state_names(cls, v):
        names = [s.name for s in v]
        if len(names) != len(set(names)):
            duplicates = {name for name in names if names.count(name) > 1}
            raise ValueError(f"Duplicate state names: {duplicates}")
        return v

    @field_validator('initial')
    @classmethod
    def validate_initial_exists(cls, v, info):
        if info.data.get('states'):
            state_names = {s.name for s in info.data['states']}
            if v not in state_names:
                raise ValueError(f"Initial state '{v}' not found in states")
        return v
```

---

### State

**Description**: A node in the state graph representing a valid configuration. Has a unique name, optional preconditions, and outgoing transitions.

**Attributes**:
- `name` (str, required): Unique state identifier
- `preconditions` (list[str], optional): List of constraint names that must be satisfied to enter this state
- `transitions` (list[Transition], optional): Outgoing transitions to other states
- `description` (str, optional): Human-readable state description

**Validation Rules**:
- Name must be unique within state graph
- Precondition names must reference valid constraints
- At least one transition required for non-goal states

**Pydantic Model**:
```python
class State(BaseModel):
    name: str = Field(..., min_length=1, pattern=r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    preconditions: list[str] = Field(default_factory=list)
    transitions: list[Transition] = Field(default_factory=list)
    description: str | None = None
```

---

### Transition

**Description**: An edge in the state graph connecting two states. Has preconditions (when allowed) and effects (what changes).

**Attributes**:
- `to` (str, required): Target state name
- `preconditions` (list[str], optional): Constraint names that must be satisfied for this transition
- `effects` (list[str], optional): State changes applied when transition occurs
- `description` (str, optional): Human-readable transition description

**Validation Rules**:
- Target state must exist in state graph
- Precondition names must reference valid constraints
- Effects must be valid CEL assignment expressions

**Pydantic Model**:
```python
class Transition(BaseModel):
    to: str
    preconditions: list[str] = Field(default_factory=list)
    effects: list[str] = Field(default_factory=list)
    description: str | None = None
```

---

### Invariant

**Description**: A logical expression that must remain true throughout policy execution, regardless of state or transitions.

**Attributes**:
- `name` (str, optional): Human-readable invariant name
- `expr` (str, required): CEL expression that must always evaluate to true
- `description` (str, optional): Rationale for invariant

**Validation Rules**:
- Expression must be valid CEL syntax
- Expression must evaluate to boolean type

**Pydantic Model**:
```python
class Invariant(BaseModel):
    name: str | None = None
    expr: str = Field(..., min_length=1)
    description: str | None = None
```

---

### GoalState

**Description**: A target abstract state with optional goal conditions that specify desired concrete values. Enables goal-directed agent execution with precise success criteria.

**Attributes**:
- `name` (str, required): Goal state name (must exist in state graph)
- `conditions` (list[str], optional): CEL expressions defining target values (e.g., "balance >= 1000", "quality_score >= 0.8")
- `description` (str, optional): Human-readable explanation of what this goal represents

**Validation Rules**:
- Name must reference a valid state in state graph
- Conditions must be valid CEL expressions
- Conditions must reference only variables defined in state schema
- Conditions should be satisfiable (not contradict constraints/invariants)

**Pydantic Model**:
```python
class GoalState(BaseModel):
    name: str = Field(..., min_length=1, pattern=r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    conditions: list[str] = Field(default_factory=list)
    description: str | None = None

    @field_validator('conditions')
    @classmethod
    def validate_conditions_syntax(cls, v):
        # CEL syntax validation performed during validation phase
        for condition in v:
            if not condition.strip():
                raise ValueError("Empty goal condition not allowed")
        return v
```

---

## Validation Result Models

### ValidationResult

**Description**: Results from policy validation, including errors, warnings, and metadata.

**Attributes**:
- `is_valid` (bool, required): Overall validation status
- `errors` (list[ValidationError], required): Validation errors
- `warnings` (list[ValidationError], required): Validation warnings
- `metadata` (dict[str, Any], required): Validation metadata (mode, checks performed, timing)

**Pydantic Model**:
```python
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationError]
    metadata: dict[str, Any]
```

---

### ValidationError

**Description**: Structured validation error with actionable information (SC-003: 90% fixable without docs).

**Attributes**:
- `code` (str, required): Error code (e.g., "E001", "W002")
- `message` (str, required): Human-readable description
- `line_number` (int, optional): Line in policy file
- `column_number` (int, optional): Column in policy file
- `severity` (str, required): "error", "warning", or "info"
- `fix_suggestion` (str, optional): How to fix the issue
- `documentation_url` (str, optional): Link to relevant documentation

**Pydantic Model**:
```python
from dataclasses import dataclass

@dataclass
class ValidationError:
    code: str
    message: str
    line_number: int | None = None
    column_number: int | None = None
    severity: str = "error"
    fix_suggestion: str | None = None
    documentation_url: str | None = None

    def format(self) -> str:
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
```

---

## Graph Analysis Models

### GraphAnalysisResult

**Description**: Results from state graph static analysis.

**Attributes**:
- `unreachable_states` (set[str], required): States not reachable from initial state
- `deadlock_sccs` (list[set[str]], required): Strongly connected components representing deadlocks
- `goal_reachable` (bool, required): Whether any goal state is reachable from initial
- `cycles` (list[list[str]], optional): All cycles in the graph (thorough mode only)

**Pydantic Model**:
```python
@dataclass
class GraphAnalysisResult:
    unreachable_states: set[str]
    deadlock_sccs: list[set[str]]
    goal_reachable: bool
    cycles: list[list[str]] | None = None
```

---

## Version Models

### PolicyVersion

**Description**: Policy format version information.

**Attributes**:
- `major` (int, required): Major version number
- `minor` (int, required): Minor version number

**Validation Rules**:
- Major and minor must be non-negative integers

**Pydantic Model**:
```python
class PolicyVersion(BaseModel):
    major: int = Field(..., ge=0)
    minor: int = Field(..., ge=0)

    @classmethod
    def from_string(cls, version: str) -> "PolicyVersion":
        major_str, minor_str = version.split('.')
        return cls(major=int(major_str), minor=int(minor_str))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

    def is_compatible(self, other: "PolicyVersion") -> bool:
        """Check if this version can parse policies from other version"""
        # Support current version and one previous
        if self.major == other.major:
            return abs(self.minor - other.minor) <= 1
        return False
```

---

## Relationships

```
Policy
  ├─ version: PolicyVersion
  ├─ state_schema: dict[str, str] (field_name -> type)
  ├─ constraints: list[Constraint]
  │    └─ expr: str (references state_schema variables)
  ├─ state_graph: StateGraph
  │    ├─ initial: str (references State.name)
  │    └─ states: list[State]
  │         └─ transitions: list[Transition]
  │              ├─ to: str (references State.name)
  │              ├─ preconditions: list[str] (references Constraint.name)
  │              └─ effects: list[str] (modify state_schema variables)
  ├─ invariants: list[Invariant]
  │    └─ expr: str (references state_schema variables)
  └─ goal_states: list[GoalState]
       ├─ name: str (references State.name)
       └─ conditions: list[str] (CEL expressions over state_schema variables)

ValidationResult
  ├─ errors: list[ValidationError]
  ├─ warnings: list[ValidationError]
  └─ metadata: dict[str, Any]

GraphAnalysisResult
  ├─ unreachable_states: set[str] (references State.name)
  └─ deadlock_sccs: list[set[str]] (references State.name)
```

---

## State Lifecycle

1. **Draft**: Policy created, not yet validated
2. **Validated**: Policy passes schema and structural validation
3. **Analyzed**: Static analysis complete (reachability, deadlocks checked)
4. **Ready**: Policy ready for execution or compilation

States tracked in `ValidationResult.metadata['status']`.

---

## Type Hints and Mypy Compliance

All models use strict type hints compatible with mypy strict mode:

```python
from typing import Any
from pydantic import BaseModel, Field

# All attributes explicitly typed
# Optional fields use | None syntax (Python 3.10+)
# Collections use built-in generics (list, dict, set)
```

**Configuration**:
```toml
[tool.mypy]
strict = true
python_version = "3.11"
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

---

## JSON Schema Generation

Pydantic models can generate JSON schemas for documentation:

```python
from noetic_policies.models import Policy

schema = Policy.model_json_schema()
# Use for: API documentation, editor autocomplete, validation tools
```

---

## Notes

- All models follow constitution's Type Safety & Static Verification principle
- Pydantic enables validation at parse time (fail early)
- Models support both dict and object-oriented access patterns
- JSON/YAML serialization built-in via Pydantic
- Compatible with OpenTelemetry attributes (can serialize to dict for span attributes)
