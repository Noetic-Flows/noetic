<!--
SYNC IMPACT REPORT
==================
Version: 1.0.0 → 1.1.0
Rationale: MINOR version bump - Added Principle VIII (Error Handling & User Experience),
expanded Quality Standards with validation requirements, added Code Review Standards,
enhanced observability requirements with OpenTelemetry specifics

Modified Principles:
- IV. Test-Driven Development: Clarified approval gate timing and added performance testing requirement
- V. Library-First with CLI Exposure: Added exit code standards

Added Sections:
- Principle VIII: Error Handling & User Experience (NEW)
- Quality Standards: Validation & Error Message Design (NEW subsection)
- Quality Standards: Code Review Standards (NEW subsection)
- Quality Standards: Performance Requirements (NEW subsection)
- Observability: Added OpenTelemetry specifics and metrics requirements

Removed Sections:
- None

Templates Requiring Updates:
- ✅ .specify/templates/plan-template.md (Constitution Check section covers new principles)
- ✅ .specify/templates/spec-template.md (Error message requirements align with Principle VIII)
- ✅ .specify/templates/tasks-template.md (Task categorization includes validation testing)
- ✅ .specify/templates/commands/plan.md (References constitution compliance)
- ✅ .specify/templates/commands/tasks.md (TDD workflow with approval gates)

Follow-up TODOs:
- Consider adding security review checklist in Phase 2
- Evaluate adding accessibility standards for CLI output in Phase 2
-->

# Noetic Constitution

## Core Principles

### I. Policy-First Architecture

**Rule**: Every feature MUST separate policy (declarative "what") from execution (imperative "how").

- Policies defined in YAML with CEL constraints
- No business logic in execution engines (kernel/compiler)
- Runtime engines interpret policies, not implement them
- Policies must be independently testable and verifiable

**Rationale**: This separation enables the same policy to compile to multiple execution
targets (Python agents, Solidity contracts) and ensures policy specifications remain the
single source of truth for behavior.

### II. Determinism & Reproducibility

**Rule**: All constraint evaluation MUST be deterministic and sandboxed.

- CEL (Common Expression Language) for all constraint expressions
- No platform-specific functions in policy constraints
- Same policy + same state = same evaluation result, regardless of target
- All policy effects must be explicitly declared
- Validation results must be deterministic (same policy → same validation result)

**Rationale**: Determinism is non-negotiable for smart contract compilation and formal
verification. Users must trust that policies behave identically across execution environments.

### III. Type Safety & Static Verification

**Rule**: Policy validation MUST catch errors before runtime.

- Static analysis of state graphs (completeness, reachability, deadlock detection)
- CEL type checking at policy validation time
- Schema validation for all policy sections
- Python codebase uses strict type hints (mypy strict mode)
- Pydantic models with field validators for runtime validation
- All validators must use decorators (@field_validator, @model_validator)

**Rationale**: Catching errors early prevents runtime failures in production and builds
confidence in generated code (especially Solidity contracts where bugs are expensive).

### IV. Test-Driven Development (NON-NEGOTIABLE)

**Rule**: TDD mandatory for all implementation work.

1. Tests written → User approved → Tests MUST fail → Then implement
2. Red-Green-Refactor cycle strictly enforced
3. Minimum 80% test coverage required
4. Example policies in standard library must execute successfully
5. Performance tests required for all performance-critical paths

**Test Categories**:
- **Unit tests**: Core functionality (parser, validator, CEL evaluator)
- **Integration tests**: End-to-end workflows (policy → execution, policy → compilation)
- **Comparison tests**: Generated code vs reference implementations (e.g., generated ERC-20 vs OpenZeppelin)
- **Property-based tests**: Variable mapping accuracy (>90% target), validation invariants
- **Performance tests**: Fast mode <1s for ≤100 states, resource consumption monitoring

**Approval Gates**:
- Test suite must be reviewed and approved BEFORE implementation begins
- Tests must fail initially (proving they test the right thing)
- No implementation work starts until approval gate passes

**Rationale**: Noetic's value proposition depends on correctness. TDD ensures all code paths
are validated and provides regression protection during refactoring. Explicit approval gates
prevent premature implementation and ensure test quality.

### V. Library-First with CLI Exposure

**Rule**: Every package must be usable as both a library and CLI tool.

- Core functionality implemented as importable Python libraries
- CLI tools expose library functionality via text I/O (stdin/args → stdout, errors → stderr)
- Support both JSON and human-readable output formats
- Clear API boundaries between packages
- Standard exit codes: 0=success, 1=validation failure, 2=parse error, 3=not found, 4=invalid args

**Rationale**: Library-first design enables programmatic composition while CLI exposure
ensures debuggability and integration with Unix tooling. This dual interface supports both
developers and automation.

### VI. Standard Library as Proof of Quality

**Rule**: Standard library policies are verified exemplars, not convenience utilities.

- Each stdlib policy demonstrates a design pattern
- All stdlib policies formally verified (static analysis passes all checks)
- Stdlib serves as regression suite for parser/validator/compiler changes
- Include at least: token transfer, voting, time-locked escrow, research agent
- Multi-layer verification: static analysis, property-based testing, scenario tests, security audit

**Rationale**: The standard library demonstrates Noetic's expressiveness and serves as a
quality gate. If we can't express common patterns elegantly, the policy language is insufficient.

### VII. Simplicity & YAGNI

**Rule**: Start simple, add complexity only when validated by real use cases.

- Phase 1 focus: Single agent, local state only
- Defer multi-agent negotiation, Data Mesh, ZK-proofs, formal verification proofs to Phase 2+
- No abstractions for hypothetical future requirements
- Complexity requires explicit justification in plan.md Complexity Tracking table
- Avoid premature optimization

**Rationale**: Phase 1 exists to validate two critical hypotheses: (1) policy expressiveness
for smart contracts, (2) variable mapping reliability. Premature complexity jeopardizes this
learning mission.

### VIII. Error Handling & User Experience

**Rule**: Error messages MUST be actionable and documentation MUST be accessible.

**Error Message Requirements**:
- Include location (file, line, column) for all validation errors
- Provide specific problem description (what's wrong)
- Suggest concrete fix (how to resolve)
- Link to documentation when relevant (docs_url field)
- Target: 90% of errors fixable without consulting external documentation (SC-003)

**Error Message Format** (machine-readable):
```
{
  "code": "E001",
  "severity": "error",
  "message": "Missing required 'constraints' section",
  "line_number": 2,
  "column_number": 1,
  "fix_suggestion": "Add constraints: [] to define policy constraints",
  "documentation_url": "https://docs.noetic.ai/errors#E001"
}
```

**Error Message Format** (human-readable):
```
ERROR [E001]: Missing required 'constraints' section
  Line 2, Column 1
  Suggestion: Add constraints: [] to define policy constraints
  See: https://docs.noetic.ai/errors#E001
```

**Documentation Requirements**:
- Error code catalog with examples
- Quick start tutorial completable in <30 minutes
- API reference auto-generated from docstrings
- Policy format specification (comprehensive)

**Rationale**: User experience is a quality metric. Clear errors reduce friction, build trust,
and accelerate development. Measuring error fixability (SC-003) ensures we maintain standards.

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
- networkx (graph analysis)
- opentelemetry-api & opentelemetry-sdk (observability)
- sentence-transformers (variable name similarity)
- jinja2 (code generation templates)
- pytest (testing framework)
- hypothesis (property-based testing)
- solc-select (Solidity compiler management)

**Forbidden (Phase 1 scope)**:
- Rust implementations (defer to Phase 2)
- Database systems (local state only)
- Multi-process architectures
- Production deployment infrastructure

### Variable Mapping Strategy

**Problem**: Policies use human-friendly names ("sender_balance"), execution environments use
specific names ("balances[msg.sender]").

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
- Import organization: consolidate at module top, avoid circular dependencies
- Pydantic validators: use decorators (@field_validator, @model_validator)

### Validation & Error Message Design

**Validation Requirements**:
- Dual modes: fast (<1s for ≤100 states) and thorough (complete analysis)
- Fast mode: schema validation, constraint syntax, transition well-formedness, basic reachability
- Thorough mode: all fast checks + cycle detection, deadlock detection, invariant consistency,
  scoring consistency, temporal feasibility, comprehensive edge cases
- Resource monitoring: warn at configurable thresholds (default: 5s CPU, 1GB memory)

**Error Message Standards**:
- All errors include error code, severity, message, location
- Fix suggestions required for all validation failures
- Documentation URLs point to valid, helpful content
- Tested for actionability (SC-003: 90% fixable without docs)

### Code Review Standards

**Pre-Merge Checklist**:
- ✅ All tests pass (including new tests for changes)
- ✅ Coverage meets 80% minimum
- ✅ Mypy strict mode passes with no errors
- ✅ Ruff linting passes
- ✅ Black formatting applied
- ✅ No TODOs introduced in production code
- ✅ Constitution compliance verified (if adding features)
- ✅ Documentation updated (if changing APIs)

**Review Focus Areas**:
- Type safety: strict type hints, proper Pydantic usage
- Error handling: actionable messages, proper error codes
- Testing: adequate coverage, correct test categories
- Architecture: package boundaries respected, no circular dependencies

### Performance Requirements

**Validation Performance**:
- Fast mode: <1 second for policies ≤100 states
- Performance warning emitted for policies >100 states
- Thorough mode: no time constraint, prioritize correctness over speed
- Resource monitoring: track CPU time and memory usage

**Optimization Strategy**:
- Measure before optimizing (use pytest-benchmark)
- Document performance requirements in tests
- Profile validation workflows to identify bottlenecks

### Documentation Requirements

**Required Documentation**:
- Complete policy format specification (similar to JSON Schema spec)
- CEL usage guide with examples for each mode (safe/full/extended)
- Variable mapping system explanation
- Getting started tutorial (completable in <30 minutes per SC-009)
- API reference for each package (auto-generated from docstrings)
- Example walkthroughs: research agent + ERC-20 compilation
- Error code catalog with fix examples

**Documentation Standards**:
- Google-style docstrings for all public APIs
- Type hints in signatures
- Usage examples in docstrings
- Link to policy format spec from error messages

### Observability

**Logging Requirements**:
- Structured logging for all runtime events (always enabled per clarification Q3)
- Log all validation operations: which checks performed, results, timing
- Log format: include timestamp, level, component, message, context
- No logging to disable validation logging (comprehensive logging is mandatory)

**OpenTelemetry Integration**:
- Automatic span creation for all major operations
- Span attributes: policy metadata (version, name, num_states, num_constraints, num_goals,
  has_scoring, has_temporal_bounds), validation metadata (mode, duration_ms)
- Metrics: validation duration, error counts by code, resource usage
- Trace context propagation for distributed scenarios

**Debugging Support**:
- Text I/O ensures debuggability (no binary protocols)
- Policy execution traces for debugging
- Violation detection with clear error messages
- Static analysis reports for policy validation

### Versioning & Breaking Changes

**Format**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes to policy format or API contracts
- **MINOR**: New features, backward-compatible API additions
- **PATCH**: Bug fixes, documentation, internal refactoring

**Policy**: Phase 1 is 0.x.y (unstable API). Breaking changes allowed with clear migration
documentation.

**Version Support**: Current version + 1 previous version supported. Deprecation warnings
issued for old versions. Auto-migration available (configurable).

## Governance

### Amendment Process

1. Propose change via issue/PR with rationale
2. Document impact on existing code and principles
3. Update constitution.md with version bump (MAJOR/MINOR/PATCH)
4. Update dependent templates (plan-template.md, spec-template.md, tasks-template.md)
5. Create migration guide for breaking changes
6. Add sync impact report to constitution

### Compliance

- All PRs/reviews must verify compliance with constitution
- Constitution check in plan-template.md is a required gate
- Complexity violations require explicit justification in Complexity Tracking table
- Runtime development follows principles; special cases documented in MEMORY.md
- Pre-merge checklist enforced for all changes

### Success Validation (Phase 1)

**Hypothesis 1 - Policy Expressiveness**:
- ✅ ERC-20 policy compiles to working Solidity contract
- ✅ Generated Solidity passes OpenZeppelin-style test suite
- ✅ Research agent policy executes successfully under constraints

**Hypothesis 2 - Variable Mapping**:
- ✅ Variable mapper achieves >90% accuracy on test cases
- ✅ Same policy compiles to both Python and Solidity with correct mappings

**Decision Point**: If hypotheses validate, invest in Phase 2 (Data Mesh + production system).
If hypotheses fail, pivot architecture before scaling.

**Version**: 1.1.0 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-07
