# Feature Specification: Noetic Policies Package

**Feature Branch**: `001-noetic-policies`
**Created**: 2026-02-05
**Status**: Draft
**Input**: User description: "Build the noetic-policies package"

## Clarifications

### Session 2026-02-05

- Q: When validation time exceeds the 1-second target for complex policies, should the system prioritize speed or thoroughness? → A: Offer both fast mode (basic checks, <1 sec) and thorough mode (complete analysis, may take longer)
- Q: Should the validation system enforce resource limits (CPU time, memory) to prevent runaway analysis of pathological policies? → A: Soft limits with warnings - validation completes but warns if resource usage is high (organizations can harden limits in their deployment environments if needed)
- Q: What level of diagnostic information should validation provide beyond error messages? → A: Comprehensive logging - detailed execution log of entire validation process, always enabled. All Noetic ecosystem components must support comprehensive logging/tracing from the ground up, using OpenTelemetry where applicable
- Q: How should the system handle different versions of the policy format? → A: Hybrid approach (configurable) - version detection with backward compatibility (support current version plus one previous) AND optional automatic migration to upgrade older policies to current format
- Q: What level of completeness should the standard library policies demonstrate? → A: Production-ready - comprehensive coverage including edge cases, gas optimization (for Solidity compilation target), and security hardening to fully prove the Noetic Policy design
- Q: Which specific validation checks should run in fast mode vs thorough mode? → A: Fast mode includes schema validation, constraint syntax checking, and basic reachability analysis (completes in <1 second). Thorough mode includes all fast mode checks plus cycle detection, invariant consistency verification, and comprehensive edge case analysis (no time constraint)
- Q: What specific threshold values should trigger resource consumption warnings? → A: Configurable thresholds with sensible defaults - Default CPU: 5 seconds, Default Memory: 1 GB. Users can override via config file or environment variables to accommodate different deployment scenarios (developer laptops vs CI servers)
- Q: What format should error messages follow? → A: Machine-readable + human-readable hybrid - JSON format for programmatic access (with fields: code, severity, message, location, suggestion, docs_url) and structured human-readable format for CLI output (with error codes, line/column info, fix suggestions, and documentation links)
- Q: Which CEL operations should be allowed in constraint expressions? → A: Three-tier approach with configurable restriction mode - (1) Safe subset: deterministic operations only (comparisons, logical, arithmetic, string/list operations - excludes I/O, time, random, external calls), (2) Full CEL: complete standard library when explicitly enabled, (3) Extension points: mechanism for custom deterministic functions. Default mode enforces safe subset for determinism guarantees (similar to strict mode). Policies can declare required mode; validation enforces restrictions based on configuration
- Q: How should standard library production-readiness be verified beyond static verification? → A: Multi-layer verification suite - Layer 1: Static verification (unreachable states, deadlocks), Layer 2: Property-based testing with Hypothesis (invariant preservation under random state transitions), Layer 3: Scenario-based testing (documented test cases for each edge case), Layer 4: Security audit checklist (reentrancy, overflow, etc.). This provides quantitative evidence of production-readiness and serves as a template for user policies

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Write and Validate Policy Specifications (Priority: P1)

A developer wants to define a policy for an autonomous agent or smart contract using a human-readable format. They need to write the policy specification and have it validated for correctness before using it in execution or compilation.

**Why this priority**: This is the foundation of the entire Noetic system. Without the ability to write and validate policies, no other functionality (agent execution, smart contract compilation) can work. This validates the policy language's expressiveness.

**Independent Test**: Can be fully tested by creating a policy file, running validation, and receiving clear feedback on policy correctness. Delivers immediate value by catching errors early.

**Acceptance Scenarios**:

1. **Given** a developer has written a policy specification file, **When** they validate the policy, **Then** the system confirms the policy is well-formed and all required sections are present
2. **Given** a policy contains a malformed constraint expression, **When** validation runs, **Then** the system identifies the specific error with line number and clear error message
3. **Given** a policy has an unreachable state in the state graph, **When** static analysis runs, **Then** the system reports the unreachable state and suggests corrections
4. **Given** a valid policy from the standard library, **When** validation runs, **Then** all checks pass and the policy is marked as verified

---

### User Story 2 - Parse Policy into Structured Format (Priority: P2)

A developer or tool needs to load a policy file and convert it into a structured format that can be used by execution engines or compilers. The parser must handle all sections of the policy specification and preserve semantic meaning.

**Why this priority**: Parsing is required before any policy can be executed or compiled. This enables programmatic access to policy definitions, which is essential for both the kernel and compiler packages.

**Independent Test**: Can be tested by loading various policy files and verifying the parsed output matches expected structure. Delivers value by enabling programmatic policy manipulation.

**Acceptance Scenarios**:

1. **Given** a valid policy file, **When** the parser loads it, **Then** all sections (constraints, state_graph, invariants, goal_state) are correctly parsed into structured data
2. **Given** a policy with constraint expressions, **When** parsed, **Then** constraint expressions are represented as evaluable structures
3. **Given** a policy with state transitions, **When** parsed, **Then** the state graph preserves all nodes, edges, preconditions, and effects
4. **Given** an invalid policy file format, **When** parsing is attempted, **Then** the parser returns clear error messages indicating what is malformed

---

### User Story 3 - Use Pre-Built Verified Policies (Priority: P3)

A developer wants to use common policy patterns (token transfer, voting, escrow) without writing them from scratch. They need access to a standard library of verified, reusable policies that demonstrate best practices.

**Why this priority**: The standard library demonstrates policy expressiveness and provides proven examples. While valuable, developers can still write custom policies (P1) and use them (P2) without the standard library.

**Independent Test**: Can be tested by importing a standard library policy, validating it passes all checks, and using it in a simple scenario. Delivers value by reducing development time and providing examples.

**Acceptance Scenarios**:

1. **Given** a developer needs a token transfer policy, **When** they access the standard library, **Then** they find a verified token transfer policy ready to use
2. **Given** a standard library policy, **When** validation runs, **Then** all verification checks pass
3. **Given** a developer wants to customize a standard library policy, **When** they copy and modify it, **Then** validation provides feedback on their modifications
4. **Given** the standard library, **When** reviewed, **Then** it includes at least token transfer, voting, time-locked escrow, and research agent policies

---

### Edge Cases

- What happens when a policy file is extremely large (thousands of states)? → Fast mode provides rapid basic checks; thorough mode performs complete analysis without time constraint
- How does the system handle circular dependencies in state graphs? → Circular graphs are valid if there exists an exit transition from the cycle; deadlock detection (FR-005) identifies terminal cycles without exits (tested in T041)
- What happens when constraint expressions reference undefined variables? → Validation fails with actionable error identifying the undefined variable
- How are policies with missing required sections handled? → Schema validation (FR-002) fails with clear error identifying missing sections
- What happens when two states have identical names? → Schema validation fails - state names must be unique within a policy
- How does the system handle policies with unreachable goal states? → Static analysis (FR-007) detects and reports unreachable goal states
- What happens when invariants contradict each other? → Thorough mode validation detects logical contradictions via consistency checking; reports as validation error with both conflicting invariants identified

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse policy files written in standard format
- **FR-002**: System MUST validate policy structure against required schema (state_schema, constraints, state_graph, invariants, goal_states sections present)
- **FR-003**: System MUST validate constraint expressions for syntactic correctness
- **FR-004**: System MUST perform static analysis to detect unreachable states in state graphs
- **FR-005**: System MUST perform static analysis to detect potential deadlocks in state graphs
- **FR-006**: System MUST validate that all state transitions have well-formed preconditions and effects
- **FR-007**: System MUST validate that goal states are reachable from initial states
- **FR-008**: System MUST validate that invariants are well-formed logical expressions
- **FR-008a**: System MUST validate state schema defines all variables referenced in constraints, effects, and invariants
- **FR-008b**: System MUST validate goal conditions are well-formed CEL expressions referencing only variables defined in state schema
- **FR-008c**: System MUST verify goal conditions are satisfiable (not logically contradictory with constraints or invariants)
- **FR-009**: System MUST provide clear, actionable error messages for all validation failures in both machine-readable JSON format (with fields: code, severity, message, location, suggestion, docs_url) and structured human-readable format (with error codes, line/column info, fix suggestions, documentation links)
- **FR-010**: System MUST support programmatic access to parsed policy data structures
- **FR-011**: System MUST include a standard library with at least four production-ready policies: ERC-20 compliant token transfer (including all standard operations and edge cases), simple majority voting (with comprehensive validation), time-locked escrow (with security hardening), and autonomous research agent (with budget/time/quality constraints)
- **FR-012**: All standard library policies MUST pass multi-layer verification suite: (1) complete static verification, (2) property-based testing for invariant preservation, (3) scenario-based testing with documented edge cases, (4) security audit checklist covering common vulnerabilities
- **FR-013**: System MUST support deterministic constraint evaluation semantics with configurable restriction modes (safe subset default, full CEL optional, extension points for custom functions)
- **FR-014**: System MUST validate that constraint expressions use only allowed operations based on the policy's declared mode and system configuration (safe mode: deterministic subset only; full mode: complete CEL standard library; extensions: registered custom functions)
- **FR-014a**: System MUST allow policies to declare their required CEL mode (safe/full/extended) via top-level `cel_mode` field (defaults to "safe" if unspecified) and provide system-level configuration to enforce mode restrictions for organizational policy requirements
- **FR-015**: System MUST provide a specification document defining the complete policy format including CEL mode semantics and operation allowlists for each mode
- **FR-016**: System MUST support both fast validation mode (schema validation, constraint syntax checking, basic reachability analysis - completing in <1 second) and thorough validation mode (all fast mode checks plus cycle detection, invariant consistency verification, comprehensive edge case analysis - no time constraint)
- **FR-017**: System MUST monitor resource consumption during validation and issue warnings when CPU time or memory usage exceeds configurable thresholds (defaults: 5 seconds CPU time, 1 GB memory)
- **FR-018**: System MUST provide comprehensive logging of all validation operations including which checks were performed, their results, and timing information
- **FR-019**: System MUST support structured observability using OpenTelemetry-compatible tracing and metrics where applicable
- **FR-020**: System MUST detect policy format version and support parsing current version plus one previous version
- **FR-021**: System MUST provide configurable automatic migration to upgrade older policy formats to current version
- **FR-022**: System MUST issue deprecation warnings when loading policies in older format versions

### Key Entities

- **Policy**: A complete policy specification including metadata, state schema, constraints, state graph, invariants, and goal states with conditions. Represents the declarative "what" that governs agent or contract behavior. Each policy has an associated format version.
- **State Schema**: Defines the structure of runtime state snapshots - the variables that exist, their types, and valid values. Enables type checking and provides the foundation for goal-directed agent execution.
- **Constraint**: A logical expression that must evaluate to true for a transition or state to be valid. Uses expression language syntax and references variables defined in state schema.
- **State Graph**: A directed graph of abstract states and transitions representing all possible execution paths. Each state has preconditions, each transition has effects. Abstract states are templates; runtime execution creates concrete state snapshots.
- **State**: A node in the state graph representing an abstract configuration. Has a unique name and optional preconditions. Distinguished from state snapshots (concrete runtime values).
- **Transition**: An edge in the state graph connecting two states. Has preconditions (when allowed) and effects (what changes in state variables).
- **Invariant**: A logical expression that must remain true throughout policy execution, regardless of state or transitions. References variables from state schema.
- **Goal State**: A target abstract state that represents successful completion. Includes optional goal conditions (concrete target values) that define precisely what "success" means for goal-directed agent search.
- **Goal Condition**: CEL expressions that specify the desired values of state variables when a goal state is reached. Enables AlphaGo-style heuristic evaluation of progress toward goals.
- **Standard Library Policy**: A pre-built, verified policy demonstrating a common pattern and serving as a reference implementation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developers can validate policies in fast mode and receive basic validation results in under 1 second regardless of policy size
- **SC-002**: Static analysis in thorough mode correctly identifies 100% of unreachable states and deadlocks in test suite policies
- **SC-003**: Error messages allow developers to fix 90% of policy errors without consulting documentation
- **SC-004**: All four standard library policies (token transfer, voting, escrow, research agent) pass the complete multi-layer verification suite (static verification, property-based testing, scenario-based testing, security audit) demonstrating quantifiable production-ready quality
- **SC-005**: Parsed policy data structures can be programmatically accessed and manipulated by other packages
- **SC-006**: The policy specification format can express all requirements needed for production-ready ERC-20 token contracts including edge cases, security constraints, and gas optimization considerations
- **SC-007**: The policy specification format can express all requirements needed for autonomous research agents with budget/time/quality constraints
- **SC-008**: Validation catches 100% of malformed constraint expressions before runtime
- **SC-009**: Documentation allows a new developer to write their first valid policy in under 30 minutes
- **SC-010**: Validation logs provide complete trace of all checks performed, enabling developers to understand validation behavior without reading source code

## Assumptions

- Policies are written by developers familiar with logical constraint expressions
- Policy files are text-based and version-controlled
- Static analysis is acceptable to run during development/validation phase (not required at runtime)
- Standard library policies serve as learning examples and starting templates
- Policy format will be documented separately in a comprehensive specification document
- Expression language for constraints will be clearly defined with deterministic semantics
- Validation runs in local developer environments (not centralized servers), though organizations may deploy validation services with their own resource limits
- OpenTelemetry is the standard observability framework for the entire Noetic ecosystem
