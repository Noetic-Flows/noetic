<!--
SYNC IMPACT REPORT
==================
Version: 0.0.0 → 1.0.0
Rationale: Initial constitution creation for Noetic Phase 1

Modified Principles:
- N/A (initial creation)

Added Sections:
- Core Principles (7 principles)
- Architecture Constraints
- Quality Standards
- Governance

Removed Sections:
- N/A (initial creation)

Templates Requiring Updates:
- ✅ .specify/templates/plan-template.md (Constitution Check section compatible)
- ✅ .specify/templates/spec-template.md (Requirements align with principles)
- ✅ .specify/templates/tasks-template.md (Task categorization supports testing principle)

Follow-up TODOs:
- None (all placeholders resolved)
-->

# Noetic Constitution

## Core Principles

### I. Policy-First Architecture

**Rule**: Every feature MUST separate policy (declarative "what") from execution (imperative "how").

- Policies defined in YAML with CEL constraints
- No business logic in execution engines (kernel/compiler)
- Runtime engines interpret policies, not implement them
- Policies must be independently testable and verifiable

**Rationale**: This separation enables the same policy to compile to multiple execution targets (Python agents, Solidity contracts) and ensures policy specifications remain the single source of truth for behavior.

### II. Determinism & Reproducibility

**Rule**: All constraint evaluation MUST be deterministic and sandboxed.

- CEL (Common Expression Language) for all constraint expressions
- No platform-specific functions in policy constraints
- Same policy + same state = same evaluation result, regardless of target
- All policy effects must be explicitly declared

**Rationale**: Determinism is non-negotiable for smart contract compilation and formal verification. Users must trust that policies behave identically across execution environments.

### III. Type Safety & Static Verification

**Rule**: Policy validation MUST catch errors before runtime.

- Static analysis of state graphs (completeness, reachability, deadlock detection)
- CEL type checking at policy validation time
- Schema validation for all policy sections
- Python codebase uses strict type hints (mypy strict mode)

**Rationale**: Catching errors early prevents runtime failures in production and builds confidence in generated code (especially Solidity contracts where bugs are expensive).

### IV. Test-Driven Development (NON-NEGOTIABLE)

**Rule**: TDD mandatory for all implementation work.

1. Tests written → User approved → Tests fail → Then implement
2. Red-Green-Refactor cycle strictly enforced
3. Minimum 80% test coverage required
4. Example policies in standard library must execute successfully

**Test Categories**:
- **Unit tests**: Core functionality (parser, validator, CEL evaluator)
- **Integration tests**: End-to-end workflows (policy → execution, policy → compilation)
- **Comparison tests**: Generated code vs reference implementations (e.g., generated ERC-20 vs OpenZeppelin)
- **Property-based tests**: Variable mapping accuracy (>90% target)

**Rationale**: Noetic's value proposition depends on correctness. TDD ensures all code paths are validated and provides regression protection during refactoring.

### V. Library-First with CLI Exposure

**Rule**: Every package must be usable as both a library and CLI tool.

- Core functionality implemented as importable Python libraries
- CLI tools expose library functionality via text I/O (stdin/args → stdout, errors → stderr)
- Support both JSON and human-readable output formats
- Clear API boundaries between packages

**Rationale**: Library-first design enables programmatic composition while CLI exposure ensures debuggability and integration with Unix tooling. This dual interface supports both developers and automation.

### VI. Standard Library as Proof of Quality

**Rule**: Standard library policies are verified exemplars, not convenience utilities.

- Each stdlib policy demonstrates a design pattern
- All stdlib policies formally verified (static analysis passes all checks)
- Stdlib serves as regression suite for parser/validator/compiler changes
- Include at least: token transfer, voting, time-locked escrow

**Rationale**: The standard library demonstrates Noetic's expressiveness and serves as a quality gate. If we can't express common patterns elegantly, the policy language is insufficient.

### VII. Simplicity & YAGNI

**Rule**: Start simple, add complexity only when validated by real use cases.

- Phase 1 focus: Single agent, local state only
- Defer multi-agent negotiation, Data Mesh, ZK-proofs, formal verification proofs to Phase 2+
- No abstractions for hypothetical future requirements
- Complexity requires explicit justification in plan.md Complexity Tracking table

**Rationale**: Phase 1 exists to validate two critical hypotheses: (1) policy expressiveness for smart contracts, (2) variable mapping reliability. Premature complexity jeopardizes this learning mission.

## Architecture Constraints

### Monorepo Structure

**Packages**:
1. **noetic-policies**: Policy specification, parser, validator, standard library
2. **noetic-kernel**: Python runtime for executing AI agents under policy constraints
3. **noetic-compiler**: Proof-of-concept compiler (policies → Solidity/Python)

**Package Boundaries**:
- Policies package has no dependencies on kernel or compiler
- Kernel depends on policies package only
- Compiler depends on policies package only
- No circular dependencies

### Technology Stack (Phase 1)

**Required**:
- Python 3.11+
- Poetry for dependency management
- celpy (CEL implementation)
- pydantic (data validation)
- PyYAML (policy parsing)
- sentence-transformers (variable name similarity)
- jinja2 (code generation templates)
- pytest (testing framework)
- solc-select (Solidity compiler management)

**Forbidden (Phase 1 scope)**:
- Rust implementations (defer to Phase 2)
- Database systems (local state only)
- Multi-process architectures
- Production deployment infrastructure

### Variable Mapping Strategy

**Problem**: Policies use human-friendly names ("sender_balance"), execution environments use specific names ("balances[msg.sender]").

**Solution (3-tier)**:
1. **Exact match**: Via explicit aliases in target schema
2. **Vector similarity**: Sentence transformers for semantic matching
3. **Interactive disambiguation**: User confirmation for low-confidence matches

**Quality Gate**: >90% accuracy on test cases required before Phase 1 completion.

## Quality Standards

### Code Quality (Enforced via Pre-Commit Hooks)

- Type hints throughout (mypy strict mode)
- Docstrings for all public APIs (Google style)
- Linting: ruff
- Formatting: black
- Minimum 80% test coverage
- No TODOs/FIXMEs in main branch

### Documentation Requirements

- Complete policy format specification (similar to JSON Schema spec)
- CEL usage guide with examples
- Variable mapping system explanation
- Getting started tutorial
- API reference for each package (auto-generated from docstrings)
- Example walkthroughs: research agent + ERC-20 compilation

### Observability

- Text I/O ensures debuggability (no binary protocols)
- Structured logging required for all runtime events
- Policy execution traces for debugging
- Violation detection with clear error messages
- Static analysis reports for policy validation

### Versioning & Breaking Changes

**Format**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes to policy format or API contracts
- **MINOR**: New features, backward-compatible API additions
- **PATCH**: Bug fixes, documentation, internal refactoring

**Policy**: Phase 1 is 0.x.y (unstable API). Breaking changes allowed with clear migration documentation.

## Governance

### Amendment Process

1. Propose change via issue/PR with rationale
2. Document impact on existing code and principles
3. Update constitution.md with version bump
4. Update dependent templates (plan-template.md, spec-template.md, tasks-template.md)
5. Create migration guide for breaking changes

### Compliance

- All PRs/reviews must verify compliance with constitution
- Constitution check in plan-template.md is a required gate
- Complexity violations require explicit justification in Complexity Tracking table
- Runtime development follows principles; special cases documented in MEMORY.md

### Success Validation (Phase 1)

**Hypothesis 1 - Policy Expressiveness**:
- ✅ ERC-20 policy compiles to working Solidity contract
- ✅ Generated Solidity passes OpenZeppelin-style test suite
- ✅ Research agent policy executes successfully under constraints

**Hypothesis 2 - Variable Mapping**:
- ✅ Variable mapper achieves >90% accuracy on test cases
- ✅ Same policy compiles to both Python and Solidity with correct mappings

**Decision Point**: If hypotheses validate, invest in Phase 2 (Data Mesh + production system). If hypotheses fail, pivot architecture before scaling.

**Version**: 1.0.0 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-05
