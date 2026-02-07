# Noetic Policies

Policy specification, parsing, and validation for the Noetic ecosystem.

## Overview

The `noetic-policies` package provides:

- **Policy Specification Format**: YAML-based declarative policy definition with CEL constraints
- **Parser**: Load and validate policy files into structured Pydantic models
- **Validator**: Static analysis for correctness (dual fast/thorough modes)
- **Standard Library**: Production-ready policies (ERC-20 token, voting, escrow, research agent)
- **CLI Tools**: Command-line interface for validation and management

## Installation

```bash
# Install via pip
pip install noetic-policies

# Or install from source
cd packages/policies
poetry install
```

## Quick Start

### 1. Validate a Policy

```bash
# Fast validation (<1 second)
noetic-policies validate my_policy.yaml

# Thorough validation (complete static analysis)
noetic-policies validate my_policy.yaml --mode thorough
```

### 2. Explore Standard Library

```bash
# List available policies
noetic-policies stdlib list

# View a policy
noetic-policies stdlib show token_transfer

# Copy for customization
noetic-policies stdlib copy token_transfer my_token.yaml
```

### 3. Use Programmatically

```python
from noetic_policies.parser import PolicyParser
from noetic_policies.validator import PolicyValidator

# Parse policy file
parser = PolicyParser()
policy = parser.parse_file("my_policy.yaml")

# Validate policy
validator = PolicyValidator()
result = validator.validate(policy, mode="thorough")

if result.is_valid:
    print(f"✓ Policy '{policy.name}' is valid!")
else:
    for error in result.errors:
        print(error.format())
```

## Features

- **Dual Validation Modes**:
  - Fast mode: <1 second, basic checks
  - Thorough mode: Complete static analysis (reachability, deadlocks, cost-aware pathfinding, temporal feasibility)

- **Weighted Scoring & Temporality**:
  - Transition costs for pathfinding optimization
  - Goal priorities and rewards for multi-goal disambiguation
  - Progress conditions for gradient-based heuristic search
  - Temporal bounds (max_steps, deadlines, timeouts) at policy and goal levels

- **Comprehensive Error Messages**:
  - Line/column numbers
  - Fix suggestions
  - Documentation links
  - 90% fixable without consulting docs

- **OpenTelemetry Integration**:
  - Automatic tracing and metrics
  - Comprehensive logging

- **Type Safety**:
  - Strict type hints (mypy strict mode)
  - Pydantic validation at parse time

## Documentation

- **Quickstart**: See `docs/quickstart.md` for 30-minute tutorial
- **Policy Specification**: Complete format reference in `docs/policy-specification.md`
- **CEL Guide**: Expression syntax in `docs/cel-guide.md`
- **API Reference**: Programmatic API in `docs/api-reference/`

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Type checking
poetry run mypy noetic_policies

# Linting
poetry run ruff check .

# Formatting
poetry run black .
```

## Architecture

Per the Noetic constitution (Principle V: Library-First with CLI Exposure):

- **Core**: Importable Python library
- **CLI**: Text I/O interface exposing library functionality
- **No Dependencies**: On kernel or compiler packages
- **Standards**: Python 3.11+, Poetry, strict type hints

## Standard Library

Production-ready verified policies:

- **token_transfer**: ERC-20 compliant token transfer with comprehensive edge cases
- **voting**: Simple majority voting with validation
- **escrow**: Time-locked escrow with security hardening
- **research_agent**: Autonomous research agent with budget/time/quality constraints

All standard library policies pass multi-layer verification:
1. Static verification
2. Property-based testing (Hypothesis)
3. Scenario-based edge case testing
4. Security audit checklist

## Requirements

- Python 3.11+
- Dependencies managed via Poetry

## License

MIT

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Support

- **Documentation**: https://docs.noetic.ai/policies
- **Issues**: https://github.com/noetic/noetic-policies/issues
- **Examples**: See `examples/` directory
