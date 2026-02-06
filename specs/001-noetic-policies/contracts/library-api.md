# Library API Contract: Noetic Policies Package

**Feature**: Build the noetic-policies package
**Branch**: 001-noetic-policies
**Date**: 2026-02-05

## Overview

This document defines the programmatic API for the noetic-policies package. Per constitution Principle V (Library-First with CLI Exposure), core functionality is exposed as importable Python libraries.

---

## Parser API

### PolicyParser

**Module**: `noetic_policies.parser`

**Purpose**: Parse policy files (YAML format) into structured Pydantic models.

#### Methods

##### `parse_yaml(content: str) -> Policy`

Parse YAML string into Policy object.

**Parameters**:
- `content` (str): YAML policy specification

**Returns**:
- `Policy`: Parsed and validated policy object

**Raises**:
- `PolicyParseError`: If YAML is malformed or validation fails
- `PolicyVersionError`: If policy version is unsupported

**Example**:
```python
from noetic_policies.parser import PolicyParser

parser = PolicyParser()
policy = parser.parse_yaml("""
version: "1.0"
constraints:
  - name: positive_amount
    expr: "amount > 0"
state_graph:
  initial: start
  states:
    - name: start
""")
```

##### `parse_file(file_path: str | Path) -> Policy`

Parse policy file from filesystem.

**Parameters**:
- `file_path` (str | Path): Path to YAML policy file

**Returns**:
- `Policy`: Parsed and validated policy object

**Raises**:
- `FileNotFoundError`: If file doesn't exist
- `PolicyParseError`: If parsing fails

**Example**:
```python
policy = parser.parse_file("policies/token_transfer.yaml")
```

##### `parse_dict(data: dict[str, Any]) -> Policy`

Parse policy from dictionary (already loaded YAML/JSON).

**Parameters**:
- `data` (dict): Policy data as dictionary

**Returns**:
- `Policy`: Parsed and validated policy object

**Raises**:
- `PolicyParseError`: If validation fails

---

## Validator API

### PolicyValidator

**Module**: `noetic_policies.validator`

**Purpose**: Validate policy correctness via static analysis.

#### Methods

##### `validate(policy: Policy, mode: str = "fast") -> ValidationResult`

Validate a parsed policy.

**Parameters**:
- `policy` (Policy): Parsed policy object
- `mode` (str): Validation mode - "fast" or "thorough"
  - **"fast"**: Basic checks, <1 second (SC-001)
  - **"thorough"**: Complete static analysis, no time constraint (SC-002)

**Returns**:
- `ValidationResult`: Validation results with errors, warnings, metadata

**Example**:
```python
from noetic_policies.validator import PolicyValidator

validator = PolicyValidator()

# Fast mode (development)
result = validator.validate(policy, mode="fast")

# Thorough mode (CI/CD)
result = validator.validate(policy, mode="thorough")

if not result.is_valid:
    for error in result.errors:
        print(error.format())
```

##### `validate_yaml(content: str, mode: str = "fast") -> ValidationResult`

Parse and validate YAML in one step.

**Parameters**:
- `content` (str): YAML policy specification
- `mode` (str): Validation mode

**Returns**:
- `ValidationResult`: Validation results

**Example**:
```python
result = validator.validate_yaml(policy_yaml, mode="thorough")
```

##### `validate_file(file_path: str | Path, mode: str = "fast") -> ValidationResult`

Parse and validate file in one step.

**Parameters**:
- `file_path` (str | Path): Path to policy file
- `mode` (str): Validation mode

**Returns**:
- `ValidationResult`: Validation results

---

## Graph Analyzer API

### GraphAnalyzer

**Module**: `noetic_policies.validator.graph_analyzer`

**Purpose**: Perform static analysis on state graphs.

#### Methods

##### `analyze(state_graph: StateGraph, initial: str, goals: list[GoalState], policy_temporal_bounds: TemporalBounds | None = None) -> GraphAnalysisResult`

Perform complete graph analysis including cost-aware pathfinding and temporal feasibility checking.

**Parameters**:
- `state_graph` (StateGraph): State graph to analyze
- `initial` (str): Initial state name
- `goals` (list[GoalState]): Goal state objects (with scoring and temporal bounds)
- `policy_temporal_bounds` (TemporalBounds | None): Global temporal bounds for feasibility checking

**Returns**:
- `GraphAnalysisResult`: Analysis results including goal costs, min steps, and temporal feasibility

**Example**:
```python
from noetic_policies.validator.graph_analyzer import GraphAnalyzer

analyzer = GraphAnalyzer()
result = analyzer.analyze(
    state_graph=policy.state_graph,
    initial=policy.state_graph.initial,
    goals=policy.goal_states,
    policy_temporal_bounds=policy.temporal_bounds
)

if result.unreachable_states:
    print(f"Unreachable states: {result.unreachable_states}")

if result.deadlock_sccs:
    print(f"Deadlocks detected: {result.deadlock_sccs}")

# Cost-aware analysis (thorough mode)
if result.goal_costs:
    for goal_name, cost in result.goal_costs.items():
        print(f"Min cost to {goal_name}: {cost}")

if result.temporally_infeasible_goals:
    for goal_name in result.temporally_infeasible_goals:
        steps = result.goal_min_steps[goal_name]
        print(f"Goal '{goal_name}' infeasible: needs {steps} steps minimum")
```

##### `find_unreachable_states(state_graph: StateGraph, initial: str) -> set[str]`

Find states not reachable from initial state.

**Parameters**:
- `state_graph` (StateGraph): State graph
- `initial` (str): Initial state name

**Returns**:
- `set[str]`: Set of unreachable state names

##### `detect_deadlocks(state_graph: StateGraph) -> list[set[str]]`

Detect deadlock cycles in state graph.

**Parameters**:
- `state_graph` (StateGraph): State graph

**Returns**:
- `list[set[str]]`: List of deadlock SCCs (each SCC is a set of state names)

##### `verify_goal_reachable(state_graph: StateGraph, initial: str, goals: set[str]) -> bool`

Check if any goal state is reachable from initial state.

**Parameters**:
- `state_graph` (StateGraph): State graph
- `initial` (str): Initial state name
- `goals` (set[str]): Goal state names

**Returns**:
- `bool`: True if at least one goal is reachable

---

## CEL Evaluator API

### CELEvaluator

**Module**: `noetic_policies.cel_evaluator`

**Purpose**: Evaluate CEL constraint expressions (deterministic evaluation per constitution).

#### Methods

##### `evaluate(expr: str, context: dict[str, Any]) -> Any`

Evaluate CEL expression in given context.

**Parameters**:
- `expr` (str): CEL expression
- `context` (dict): Variable context

**Returns**:
- `Any`: Expression result (typically bool for constraints)

**Raises**:
- `CELSyntaxError`: If expression is malformed
- `CELEvaluationError`: If evaluation fails

**Example**:
```python
from noetic_policies.cel_evaluator import CELEvaluator

evaluator = CELEvaluator()

result = evaluator.evaluate(
    "balance >= amount",
    {"balance": 100, "amount": 50}
)
# result = True
```

##### `validate_syntax(expr: str) -> bool`

Check if CEL expression is syntactically valid.

**Parameters**:
- `expr` (str): CEL expression

**Returns**:
- `bool`: True if syntax is valid

**Raises**:
- `CELSyntaxError`: If expression is malformed (with details)

---

## Standard Library API

### StandardLibrary

**Module**: `noetic_policies.stdlib`

**Purpose**: Access pre-built verified policies.

#### Methods

##### `get(name: str) -> Policy`

Get a standard library policy by name.

**Parameters**:
- `name` (str): Policy name - "token_transfer", "voting", "escrow", or "research_agent"

**Returns**:
- `Policy`: Standard library policy

**Raises**:
- `KeyError`: If policy not found

**Example**:
```python
from noetic_policies.stdlib import StandardLibrary

stdlib = StandardLibrary()

token_policy = stdlib.get("token_transfer")
voting_policy = stdlib.get("voting")
escrow_policy = stdlib.get("escrow")
```

##### `list_policies() -> list[str]`

List all available standard library policy names.

**Returns**:
- `list[str]`: Policy names

##### `validate_all() -> dict[str, ValidationResult]`

Validate all standard library policies.

**Returns**:
- `dict[str, ValidationResult]`: Policy name → validation result

**Example**:
```python
results = stdlib.validate_all()

for name, result in results.items():
    if not result.is_valid:
        print(f"Standard library policy '{name}' failed validation!")
```

---

## Migration API

### PolicyMigrator

**Module**: `noetic_policies.migration`

**Purpose**: Migrate policies between versions (from clarification Q4).

#### Methods

##### `migrate(policy: Policy, target_version: str) -> Policy`

Migrate policy to target version.

**Parameters**:
- `policy` (Policy): Policy to migrate
- `target_version` (str): Target version (e.g., "1.0")

**Returns**:
- `Policy`: Migrated policy

**Raises**:
- `MigrationError`: If migration fails or is unsupported

**Example**:
```python
from noetic_policies.migration import PolicyMigrator

migrator = PolicyMigrator()

# Migrate old policy to current version
migrated = migrator.migrate(old_policy, "1.0")
```

##### `can_migrate(from_version: str, to_version: str) -> bool`

Check if migration is supported.

**Parameters**:
- `from_version` (str): Source version
- `to_version` (str): Target version

**Returns**:
- `bool`: True if migration is supported

---

## Observability API

### Tracing Integration

**Module**: `noetic_policies.observability`

**Purpose**: OpenTelemetry integration (from clarification Q3).

#### Usage

All major operations automatically create OpenTelemetry spans when a tracer is configured:

**Example**:
```python
from opentelemetry import trace
from noetic_policies.validator import PolicyValidator

# Configure tracer
tracer = trace.get_tracer("my_app")

# Validator will automatically create spans
validator = PolicyValidator(tracer=tracer)

# This creates nested spans:
# - policy.validate
#   - policy.validate.schema
#   - policy.validate.constraints
#   - policy.validate.state_graph
result = validator.validate(policy)
```

**Span Attributes**:
- `policy.version`: Policy format version
- `policy.name`: Policy name
- `policy.num_states`: Number of states
- `policy.num_constraints`: Number of constraints
- `policy.num_goals`: Number of goal states
- `policy.has_scoring`: Whether goals use priority/reward/progress conditions
- `policy.has_temporal_bounds`: Whether policy or goals have temporal bounds
- `validation.mode`: "fast" or "thorough"
- `validation.duration_ms`: Validation time in milliseconds

---

## Error Hierarchy

```
NoeticPoliciesError (base)
├── PolicyParseError
│   ├── YAMLSyntaxError
│   └── SchemaValidationError
├── PolicyVersionError
│   ├── UnsupportedVersionError
│   └── DeprecatedVersionWarning
├── ValidationError (different from ValidationError dataclass)
├── CELError
│   ├── CELSyntaxError
│   └── CELEvaluationError
└── MigrationError
```

---

## Type Hints and Mypy Compliance

All API methods use strict type hints:

```python
from typing import Any
from pathlib import Path

# Example: All parameters and returns explicitly typed
def validate_yaml(
    self,
    content: str,
    mode: str = "fast"
) -> ValidationResult:
    ...
```

**Mypy Configuration**:
```toml
[tool.mypy]
strict = true
plugins = ["pydantic.mypy"]
```

---

## Usage Patterns

### Basic Validation Workflow

```python
from noetic_policies.parser import PolicyParser
from noetic_policies.validator import PolicyValidator

# Parse policy
parser = PolicyParser()
policy = parser.parse_file("my_policy.yaml")

# Validate policy
validator = PolicyValidator()
result = validator.validate(policy, mode="thorough")

# Check results
if result.is_valid:
    print("Policy is valid!")
else:
    for error in result.errors:
        print(error.format())
```

### Standard Library Usage

```python
from noetic_policies.stdlib import StandardLibrary
from noetic_policies.validator import PolicyValidator

# Load stdlib policy
stdlib = StandardLibrary()
token_policy = stdlib.get("token_transfer")

# Customize and validate
token_policy.name = "my_token"
validator = PolicyValidator()
result = validator.validate(token_policy)
```

### With OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from noetic_policies.validator import PolicyValidator

# Setup tracing
provider = TracerProvider()
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Validate with tracing
validator = PolicyValidator(tracer=tracer)
result = validator.validate(policy, mode="fast")

# Spans automatically created and exported
```

---

## Performance Guarantees

Per success criteria:

- **SC-001**: Fast mode validation completes in <1 second regardless of policy size
- **SC-002**: Thorough mode achieves 100% detection accuracy (no time constraint)

Users can verify performance:

```python
import time

start = time.perf_counter()
result = validator.validate(policy, mode="fast")
duration = time.perf_counter() - start

assert duration < 1.0, "Fast mode exceeded 1 second"
```

---

## Backwards Compatibility

Per clarification Q4 (versioning strategy):

- Current version: 1.0
- Supported versions: 1.0, 0.9 (one previous)
- Deprecation warnings issued for version 0.9
- Auto-migration available (configurable)

```python
from noetic_policies.parser import PolicyParser

parser = PolicyParser(auto_migrate=True)

# Old version policy automatically migrated
policy = parser.parse_file("v0_9_policy.yaml")

# Check for deprecation warnings
if policy.version == "0.9":
    print("Warning: Policy using deprecated version 0.9")
```

---

## Notes

- All APIs follow constitution's Library-First principle
- Type safety enforced via Pydantic and mypy
- OpenTelemetry integration automatic when tracer configured
- Deterministic evaluation (CEL) per constitution
- Error messages designed for SC-003 (90% fixable without docs)
