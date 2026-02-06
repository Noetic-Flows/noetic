# Spec-Kit Constitution Prompt for Noetic Phase 1

Create a federated monorepo for Noetic, a policy-driven framework for autonomous AI agents and smart contracts.

## Project Overview

Noetic enables users to define declarative policies (rules, constraints, and goals) that govern autonomous AI agents. Policies are expressed in human-readable YAML with CEL (Common Expression Language) for constraint evaluation. The same policy specification can be compiled to multiple execution targets, proving the architecture is suitable for both AI agents and smart contracts.

## Core Concept

Separate policy (what should happen) from execution (how it happens):

- **Policies**: Declarative YAML specifications defining state graphs, constraints, and transitions
- **Kernel**: Runtime that executes agents under policy constraints
- **Compiler**: Generates target code (Solidity, Python) from policies

## Phase 1 Scope

This monorepo contains three main components:

1. **noetic-policies**: Policy specification format, parser, validator, and standard library
2. **noetic-kernel**: Python reference implementation for executing AI agents under policy constraints
3. **noetic-compiler**: Proof-of-concept compiler that generates Solidity contracts from policies

## Key Technical Decisions

### Policy Specification

- Format: YAML for policy structure + CEL for constraint expressions
- Required sections: constraints, state_graph, invariants, goal_state
- Meta-policy: Special policy that refines vague user intent into robust specifications
- Standard library: Pre-built verified policies (token transfer, voting, escrow)

### CEL (Common Expression Language)

- Used for all constraint evaluation (deterministic, sandboxed, type-safe)
- Python implementation: `celpy` library
- Solidity compilation: CEL expressions translate to `require()` statements

### Variable Mapping

- Policies use human-friendly variable names (e.g., "sender_balance")
- Execution environments have specific names (e.g., "balances[msg.sender]" in Solidity)
- Solution: Reflection + vector similarity + interactive disambiguation
- Each target provides schema describing its variables

### Reference Implementation Language

- Python for Noetic Kernel (accessibility, rapid development, rich ecosystem)
- Rust for performance-critical components in future (out of scope for Phase 1)

## Primary Use Cases

### Use Case 1: AI Research Agent

- User: "Find and summarize papers on zero-knowledge proofs"
- Meta-policy refines vague request into robust policy with constraints
- Kernel executes search/filtering/summarization under budget/time/source constraints
- Validates: Policies can govern autonomous AI agents

### Use Case 2: ERC-20 Token Transfer (Solidity Compilation)

- Policy: Define token transfer constraints (sufficient balance, positive amount, etc.)
- Compiler generates Solidity contract from policy
- Compare generated contract to OpenZeppelin ERC-20 implementation
- Validates: Policies can express smart contract requirements

## Repository Structure

```
noetic/
├── packages/
│   ├── policies/               # Policy specification and tools
│   │   ├── spec/              # Policy format specification (markdown)
│   │   ├── parser/            # YAML + CEL parser
│   │   ├── validator/         # Static policy verification
│   │   ├── stdlib/            # Standard library of policies
│   │   └── tests/
│   │
│   ├── kernel/                # Python reference implementation
│   │   ├── runtime/           # Policy execution engine
│   │   ├── cel_evaluator/    # CEL constraint checking
│   │   ├── state_graph/      # State graph navigation
│   │   ├── planner/           # MCTS-based pathfinding
│   │   └── tests/
│   │
│   └── compiler/              # Policy to target code compiler
│       ├── core/              # Shared compilation infrastructure
│       ├── solidity/          # Solidity code generator
│       ├── python/            # Python code generator
│       ├── schema/            # Schema reflection system
│       ├── mapper/            # Variable mapping (reflection + similarity)
│       └── tests/
│
├── examples/
│   ├── research_agent/        # AI research agent example
│   │   ├── policy.yaml
│   │   ├── agent.py
│   │   └── README.md
│   │
│   └── token_transfer/        # ERC-20 token example
│       ├── policy.yaml
│       ├── generated.sol      # Auto-generated from policy
│       ├── tests/
│       └── README.md
│
├── docs/
│   ├── getting-started.md
│   ├── policy-spec.md         # Complete policy format specification
│   ├── cel-guide.md           # CEL usage guide
│   ├── variable-mapping.md    # Variable mapping system
│   └── examples/
│
└── tools/
    ├── cli/                   # CLI for policy validation, compilation
    └── vscode-extension/      # VS Code support (syntax highlighting)
```

## Technical Requirements

### Policies Package

- YAML parser with schema validation
- CEL expression parser and evaluator (using `celpy`)
- Static verifier that checks:
  - State graph completeness (no unreachable states, no deadlocks)
  - CEL expressions are valid and deterministic
  - Success criteria are testable
  - Invariants are well-formed
- Standard library with at least 3 verified policies:
  - Token transfer
  - Simple voting
  - Time-locked escrow

### Kernel Package

- Load and parse Noetic policies
- Execute state graph transitions
- Evaluate CEL constraints at runtime
- MCTS-based transition selection for optimal pathfinding
- Integration with LLMs (OpenAI API for proof-of-concept, configurable)
- Execution context management (variables, state, history)
- Violation detection and reporting

### Compiler Package

- Abstract compilation pipeline (policy → IR → target code)
- Schema reflection system:
  - Python: Use `inspect` module
  - Solidity: Parse contract annotations or AST
- Variable mapper:
  - Exact match via aliases
  - Vector similarity using sentence transformers
  - Interactive disambiguation for low-confidence matches
- Solidity code generator:
  - Generate contract structure from policy
  - Convert CEL constraints to `require()` statements
  - Convert effects to state updates
  - Generate invariant checks as `assert()`
- Python code generator:
  - Generate class with policy enforcement
  - Runtime CEL evaluation
  - Exception-based violation handling

## Success Criteria

### Policies Package

- ✅ Can parse and validate example policies
- ✅ Static verifier catches common errors
- ✅ Standard library policies are formally verified

### Kernel Package

- ✅ Research agent successfully executes under policy constraints
- ✅ Constraint violations are detected and reported
- ✅ Meta-policy can refine vague user requests

### Compiler Package


- ✅ Can parse and validate example policies
- ✅ Static verifier catches common errors
- ✅ Standard library policies are formally verified

### Kernel Package

- ✅ Research agent successfully executes under policy constraints
- ✅ Constraint violations are detected and reported
- ✅ Meta-policy can refine vague user requests

### Compiler Package

- ✅ ERC-20 policy compiles to working Solidity contract
- ✅ Generated Solidity passes OpenZeppelin-style test suite
- ✅ Variable mapper achieves >90% accuracy on test cases
- ✅ Same policy compiles to both Python and Solidity

## Key Dependencies

- **Python**: 3.11+
- **Poetry**: Dependency management
- **celpy**: CEL implementation for Python
- **pydantic**: Data validation
- **PyYAML**: YAML parsing
- **sentence-transformers**: For variable name similarity
- **jinja2**: Code generation templates
- **pytest**: Testing framework
- **solc-select**: Solidity compiler version management

## Development Workflow

1. Define policy specification format (markdown)
2. Build policy parser and validator
3. Create standard library policies
4. Build Kernel runtime for Python execution
5. Build Solidity compiler with variable mapping
6. Validate with research agent use case
7. Validate with ERC-20 compilation use case
8. Document and create examples

## Documentation Requirements

- Complete policy format specification (similar to JSON Schema spec)
- CEL usage guide with examples
- Variable mapping system explanation
- Getting started tutorial
- API reference for each package
- Example walkthrough for research agent
- Example walkthrough for ERC-20 compilation

## Testing Requirements

- Unit tests for all core functionality
- Integration tests for end-to-end workflows
- Comparison tests (generated Solidity vs reference implementations)
- Property-based tests for variable mapping
- Example policies must execute successfully

## Code Quality Standards

- Type hints throughout (mypy strict mode)
- Docstrings for all public APIs
- Linting with ruff
- Code formatting with black
- Minimum 80% test coverage
- Pre-commit hooks for formatting and linting

## Non-Goals for Phase 1

- Formal verification proofs (acknowledge need, defer to Phase 2)
- Multi-agent negotiation (single agent only)
- Noetic Data Mesh integration (local state only)
- Mobile/Desktop applications (CLI and Python API only)
- Production deployment (research/validation focus)
- ZK-proof compilation (acknowledge in design, defer implementation)

## Validation Goals

Phase 1 exists to validate two critical hypotheses:

1. **Policy Expressiveness**: Noetic policies can express everything needed for smart contracts
2. **Variable Mapping**: Human-friendly variable names can map to execution environments reliably

Success means confidence to invest in Phase 2 (Data Mesh + production system).
Failure means pivot the architecture before wasting time.

## Additional Context

- This is a research project with potential commercial future
- Target users: Initially developers, eventually non-technical users via no-code builder
- Philosophy: Local-first, privacy-focused, formally verifiable
- Inspiration: Policy-as-code, formal methods, agent-oriented programming

Generate a comprehensive project constitution that sets up the monorepo structure, defines package boundaries, establishes testing strategy, and creates initial documentation framework for this Phase 1 implementation.
