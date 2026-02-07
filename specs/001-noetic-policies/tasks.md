# Tasks: Noetic Policies Package

**Input**: Design documents from `/specs/001-noetic-policies/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Following TDD per constitution - tests written FIRST, must FAIL, then implement

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure: `packages/policies/` (monorepo package)
- Source code: `packages/policies/noetic_policies/`
- Tests: `packages/policies/tests/`
- Docs: `packages/policies/docs/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure per plan.md

- [ ] T001 Create package directory structure at packages/policies/ per plan.md structure
- [ ] T002 Initialize Poetry project in packages/policies/pyproject.toml with Python 3.11+ and dependencies (PyYAML, celpy, pydantic, networkx, opentelemetry-api, opentelemetry-sdk, pytest, hypothesis, pytest-benchmark)
- [ ] T003 [P] Configure mypy strict mode in packages/policies/pyproject.toml
- [ ] T004 [P] Configure ruff linter in packages/policies/pyproject.toml
- [ ] T005 [P] Configure black formatter in packages/policies/pyproject.toml
- [ ] T006 [P] Configure pytest with coverage settings (80% minimum) in packages/policies/pyproject.toml
- [ ] T007 Create README.md in packages/policies/README.md with quickstart instructions
- [ ] T008 [P] Setup .gitignore for Python project in packages/policies/.gitignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure and data models that ALL user stories depend on - MUST complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Data Models (from data-model.md)

- [ ] T009 [P] Create ValidationError dataclass in packages/policies/noetic_policies/models/__init__.py with fields (code, message, line_number, column_number, severity, fix_suggestion, documentation_url) and format() method
- [ ] T010 [P] Create ValidationResult dataclass in packages/policies/noetic_policies/models/__init__.py with fields (is_valid, errors, warnings, metadata)
- [ ] T011 [P] Create GraphAnalysisResult dataclass in packages/policies/noetic_policies/models/__init__.py with fields (unreachable_states, deadlock_sccs, goal_reachable, cycles, goal_costs, goal_min_steps, temporally_infeasible_goals)
- [ ] T012 [P] Create PolicyVersion Pydantic model in packages/policies/noetic_policies/models/version.py with from_string() and is_compatible() methods
- [ ] T013 [P] Create Constraint Pydantic model in packages/policies/noetic_policies/models/constraint.py with name, expr, description, severity fields
- [ ] T014 [P] Create Invariant Pydantic model in packages/policies/noetic_policies/models/__init__.py with name, expr, description fields
- [ ] T015 [P] Create Transition Pydantic model in packages/policies/noetic_policies/models/__init__.py with to, preconditions, effects, cost (float, default 1.0, ge=0.0), cost_expr (str|None, CEL), description fields
- [ ] T015a [P] Create ProgressCondition Pydantic model in packages/policies/noetic_policies/models/__init__.py with expr, weight (default 1.0, gt=0.0), description fields and expr syntax validator
- [ ] T015b [P] Create TemporalBounds Pydantic model in packages/policies/noetic_policies/models/__init__.py with max_steps (int|None, gt=0), deadline (str|None, CEL expr), timeout_seconds (float|None, gt=0.0), description fields and at-least-one-bound validator
- [ ] T015c [P] Create GoalState Pydantic model in packages/policies/noetic_policies/models/__init__.py with name, conditions, priority (int, default 0), reward (float, default 1.0, gt=0.0), progress_conditions (list[ProgressCondition]), temporal_bounds (TemporalBounds|None), description fields and condition syntax validator
- [ ] T016 Create State Pydantic model in packages/policies/noetic_policies/models/state_graph.py with name, preconditions, transitions, description fields
- [ ] T017 Create StateGraph Pydantic model in packages/policies/noetic_policies/models/state_graph.py with initial, states fields and validators (unique state names, initial exists)
- [ ] T018 Create Policy Pydantic model in packages/policies/noetic_policies/models/policy.py with all fields (version, cel_mode with default "safe", name, description, metadata, state_schema, constraints, state_graph, invariants, goal_states as list[GoalState], temporal_bounds as TemporalBounds|None) and validators (state_schema types, goal_states exist in graph, temporal_bounds hierarchy FR-008h)

### OpenTelemetry Infrastructure (FR-018, FR-019)

- [ ] T019 [P] Create tracer module in packages/policies/noetic_policies/observability/tracer.py with get_tracer() function
- [ ] T020 [P] Create logger module in packages/policies/noetic_policies/observability/logger.py with structured logging setup
- [ ] T021 [P] Create metrics module in packages/policies/noetic_policies/observability/metrics.py with validation metrics (duration, mode, error count)

### CEL Evaluator Foundation (FR-013, FR-014, FR-014a)

- [ ] T022 Create CELEvaluator class in packages/policies/noetic_policies/cel_evaluator/__init__.py with mode configuration (safe/full/extended) and operation allowlists
- [ ] T023 Implement evaluate() method in packages/policies/noetic_policies/cel_evaluator/__init__.py using celpy library
- [ ] T024 Implement validate_syntax() method in packages/policies/noetic_policies/cel_evaluator/__init__.py for CEL expression syntax checking
- [ ] T025 Implement safe mode operation filter in packages/policies/noetic_policies/cel_evaluator/__init__.py (comparisons, logical, arithmetic, string/list - exclude I/O, time, random)
- [ ] T026 [P] Create CEL mode configuration schema in packages/policies/noetic_policies/cel_evaluator/modes.py with safe/full/extended definitions
- [ ] T026a [P] Create test_cel_mode_config.py in packages/policies/tests/unit/test_cel_mode_config.py - test system config file enforces cel_mode restrictions (FR-014a)
- [ ] T026b [P] Add test to test_cel_mode_config.py - test policy cel_mode field is parsed and validated (defaults to "safe" if unspecified)
- [ ] T026c [P] Add test to test_cel_mode_config.py - test validation rejects policy when cel_mode exceeds system-configured restrictions

**Checkpoint**: Foundation ready - all models, observability, and CEL infrastructure complete. User story implementation can now begin.

---

## Phase 3: User Story 1 - Write and Validate Policy Specifications (Priority: P1) 🎯 MVP

**Goal**: Enable developers to validate policy files for correctness (schema validation, constraint syntax, graph analysis)

**Independent Test**: Create a policy file, run validation, receive clear feedback on errors

### Tests for User Story 1 (TDD - Write FIRST, Must FAIL)

#### Unit Tests - Schema Validation

- [ ] T027 [P] [US1] Create test_schema_validator.py in packages/policies/tests/unit/test_schema_validator.py - test valid policy passes schema validation
- [ ] T028 [P] [US1] Add test to test_schema_validator.py - test missing constraints section fails with E001 error
- [ ] T029 [P] [US1] Add test to test_schema_validator.py - test missing state_graph section fails with error
- [ ] T030 [P] [US1] Add test to test_schema_validator.py - test invalid version format fails with error
- [ ] T031 [P] [US1] Add test to test_schema_validator.py - test goal states not in graph fails with error
- [ ] T031a [P] [US1] Add test to test_schema_validator.py - test transitions have well-formed preconditions and effects (FR-006)
- [ ] T031b [P] [US1] Add test to test_schema_validator.py - test state schema defines all referenced variables (FR-008a)
- [ ] T031c [P] [US1] Add test to test_schema_validator.py - test state schema uses valid types (number, string, boolean, address, enum)
- [ ] T031c-1 [P] [US1] Add test to test_schema_validator.py - test state schema enum type specifies valid values list
- [ ] T031d [P] [US1] Add test to test_schema_validator.py - test goal conditions reference only schema-defined variables (FR-008b)
- [ ] T031e [P] [US1] Add test to test_schema_validator.py - test goal conditions are satisfiable (FR-008c)
- [ ] T031f [P] [US1] Add test to test_schema_validator.py - test transition cost values are non-negative (FR-008d)
- [ ] T031g [P] [US1] Add test to test_schema_validator.py - test transition cost_expr is valid CEL evaluating to numeric (FR-008d)
- [ ] T031g-1 [P] [US1] Add test to test_schema_validator.py - test transition with both cost and cost_expr emits warning that cost_expr takes precedence
- [ ] T031h [P] [US1] Add test to test_schema_validator.py - test goal priority is integer and reward is positive (FR-008e)
- [ ] T031i [P] [US1] Add test to test_schema_validator.py - test progress conditions are valid CEL evaluating to numeric, referencing schema variables (FR-008f)
- [ ] T031j [P] [US1] Add test to test_schema_validator.py - test temporal bounds validation: max_steps > 0, deadline valid CEL, timeout_seconds > 0 (FR-008g)
- [ ] T031k [P] [US1] Add test to test_schema_validator.py - test goal temporal bounds do not exceed policy temporal bounds (FR-008h)

#### Unit Tests - Constraint Validation

- [ ] T032 [P] [US1] Create test_constraint_validator.py in packages/policies/tests/unit/test_constraint_validator.py - test valid CEL expression passes
- [ ] T033 [P] [US1] Add test to test_constraint_validator.py - test malformed CEL syntax fails with actionable error (line/column, fix suggestion)
- [ ] T034 [P] [US1] Add test to test_constraint_validator.py - test constraint references undefined variable fails
- [ ] T035 [P] [US1] Add test to test_constraint_validator.py - test CEL safe mode blocks disallowed operations (time, I/O, random)
- [ ] T036 [P] [US1] Add test to test_constraint_validator.py - test CEL full mode allows additional operations when enabled

#### Unit Tests - Graph Analysis

- [ ] T037 [P] [US1] Create test_graph_analyzer.py in packages/policies/tests/unit/test_graph_analyzer.py - test find_unreachable_states() detects orphaned states
- [ ] T038 [P] [US1] Add test to test_graph_analyzer.py - test detect_deadlocks() finds terminal SCCs without exits
- [ ] T039 [P] [US1] Add test to test_graph_analyzer.py - test verify_goal_reachable() confirms path to goal exists
- [ ] T040 [P] [US1] Add test to test_graph_analyzer.py - test unreachable goal state fails validation
- [ ] T041 [P] [US1] Add test to test_graph_analyzer.py - test circular state graph with exit is valid
- [ ] T041a [P] [US1] Add test to test_graph_analyzer.py - test goal_costs computed correctly using Dijkstra's with transition costs
- [ ] T041b [P] [US1] Add test to test_graph_analyzer.py - test goal_min_steps computed correctly (unweighted shortest path)
- [ ] T041c [P] [US1] Add test to test_graph_analyzer.py - test temporally_infeasible_goals detected when min_steps > max_steps
- [ ] T041d [P] [US1] Add test to test_graph_analyzer.py - test temporal feasibility passes when min_steps ≤ max_steps
- [ ] T041e [P] [US1] Add test to test_graph_analyzer.py - test goals ranked by priority then reward in analysis output
- [ ] T041f [P] [US1] Add test to test_graph_analyzer.py - test multiple goals with equal priority are disambiguated by reward value (higher reward preferred)

#### Unit Tests - Dual Mode Validation (FR-016)

- [ ] T042 [P] [US1] Create test_validation_modes.py in packages/policies/tests/unit/test_validation_modes.py - test fast mode completes in <1 second (SC-001)
- [ ] T043 [P] [US1] Add test to test_validation_modes.py - test fast mode runs schema (FR-002) + constraint syntax (FR-003) + transition well-formedness (FR-006) + basic reachability (FR-004 shallow BFS) only
- [ ] T044 [P] [US1] Add test to test_validation_modes.py - test thorough mode runs all checks (fast + cycle detection + deadlock detection FR-005 + invariant consistency + scoring consistency + temporal feasibility + edge cases)
- [ ] T044a [P] [US1] Add test to test_validation_modes.py - test fast mode SKIPS temporal feasibility analysis (verify no min-steps computation in fast mode)
- [ ] T044b [P] [US1] Add test to test_validation_modes.py - test fast mode SKIPS scoring consistency checks (verify no cost-aware pathfinding in fast mode)
- [ ] T045 [P] [US1] Add test to test_validation_modes.py - test thorough mode detects deadlocks missed by fast mode

#### Unit Tests - Resource Monitoring (FR-017)

- [ ] T046 [P] [US1] Create test_resource_monitoring.py in packages/policies/tests/unit/test_resource_monitoring.py - test CPU time warning at configurable threshold (default 5s)
- [ ] T047 [P] [US1] Add test to test_resource_monitoring.py - test memory usage warning at configurable threshold (default 1GB)
- [ ] T048 [P] [US1] Add test to test_resource_monitoring.py - test large policy (1000+ states) triggers soft limit warning

#### Unit Tests - Error Messages (FR-009, SC-003)

- [ ] T049 [P] [US1] Create test_error_formatting.py in packages/policies/tests/unit/test_error_formatting.py - test error includes code, line number, column, fix suggestion
- [ ] T050 [P] [US1] Add test to test_error_formatting.py - test JSON error format matches schema (code, severity, message, location, suggestion, docs_url)
- [ ] T050a [P] [US1] Add test to test_error_formatting.py - test error docs_url field points to valid documentation section for each error code (verify URLs are not broken)
- [ ] T051 [P] [US1] Add test to test_error_formatting.py - test human-readable error format is actionable

#### Integration Tests

- [ ] T052 [P] [US1] Create test_validation_workflow.py in packages/policies/tests/integration/test_validation_workflow.py - test end-to-end validation of valid policy
- [ ] T053 [P] [US1] Add test to test_validation_workflow.py - test end-to-end validation catches all error types in one run
- [ ] T054 [P] [US1] Add test to test_validation_workflow.py - test validation with OpenTelemetry creates spans
- [ ] T054a [P] [US1] Add test to test_validation_workflow.py - test all major validation operations (schema, constraint, graph analysis) emit OpenTelemetry spans with correct attributes (FR-019)
- [ ] T054b [P] [US1] Add test to test_validation_workflow.py - test validation metrics (duration, mode, error count) are recorded via OpenTelemetry (FR-019)

#### Property-Based Tests

- [ ] T055 [P] [US1] Create test_validation_properties.py in packages/policies/tests/property/test_validation_properties.py - test thorough mode always finds errors that fast mode finds
- [ ] T056 [P] [US1] Add test to test_validation_properties.py - test valid policy always passes both modes
- [ ] T057 [P] [US1] Add test to test_validation_properties.py - generate random policies and verify consistent validation results

#### Comparison Tests (Constitution Principle IV)

- [ ] T057a [P] [US1] Create test_validation_comparison.py in packages/policies/tests/comparison/test_validation_comparison.py - compare validation errors against hand-crafted expected error catalog for 10+ known-bad policies
- [ ] T057b [P] [US1] Add test to test_validation_comparison.py - compare fast mode vs thorough mode error detection completeness (thorough must be superset of fast)

#### Performance Tests (SC-001)

- [ ] T058 [P] [US1] Create test_validation_performance.py in packages/policies/tests/performance/test_validation_performance.py - benchmark fast mode <1s on policy sizes up to 100 states (5, 10, 20, 50, 100 states); verify performance warning emitted for >100 states
- [ ] T059 [P] [US1] Add test to test_validation_performance.py - benchmark thorough mode performance (no time constraint)

**⚠️ TDD APPROVAL GATE** (Constitution Principle IV): All US1 tests (T027-T059) must be written, reviewed by user, and verified to FAIL before proceeding to implementation tasks T060+. User must explicitly approve test suite completeness.

### Implementation for User Story 1

#### Schema Validator

- [ ] T060 [US1] Implement SchemaValidator class in packages/policies/noetic_policies/validator/schema_validator.py with validate() method (FR-002)
- [ ] T061 [US1] Add schema validation for required sections (state_schema, constraints, state_graph) in packages/policies/noetic_policies/validator/schema_validator.py
- [ ] T062 [US1] Add version validation in packages/policies/noetic_policies/validator/schema_validator.py (FR-020)
- [ ] T063 [US1] Add goal state existence check in packages/policies/noetic_policies/validator/schema_validator.py (FR-007)
- [ ] T063a [US1] Add state schema type validation in packages/policies/noetic_policies/validator/schema_validator.py (valid types: number, string, boolean, address, enum)
- [ ] T063b [US1] Add state schema coverage check in packages/policies/noetic_policies/validator/schema_validator.py - verify all variables in constraints/effects/invariants are defined (FR-008a)
- [ ] T063c [US1] Add goal condition validation in packages/policies/noetic_policies/validator/schema_validator.py - check CEL syntax and variable references (FR-008b)
- [ ] T063d [US1] Add goal condition satisfiability check in packages/policies/noetic_policies/validator/schema_validator.py - detect contradictions with constraints/invariants (FR-008c)
- [ ] T063e [US1] Add transition cost validation in packages/policies/noetic_policies/validator/schema_validator.py - validate cost ≥ 0 and cost_expr is valid numeric CEL (FR-008d)
- [ ] T063f [US1] Add goal scoring validation in packages/policies/noetic_policies/validator/schema_validator.py - validate priority is int, reward > 0 (FR-008e)
- [ ] T063g [US1] Add progress condition validation in packages/policies/noetic_policies/validator/schema_validator.py - validate CEL syntax, numeric type, schema variable references (FR-008f)
- [ ] T063h [US1] Add temporal bounds validation in packages/policies/noetic_policies/validator/schema_validator.py - validate max_steps, deadline CEL, timeout_seconds (FR-008g)
- [ ] T063i [US1] Add temporal bounds hierarchy check in packages/policies/noetic_policies/validator/schema_validator.py - goal bounds ≤ policy bounds (FR-008h)

#### Constraint Validator

- [ ] T064 [US1] Implement ConstraintValidator class in packages/policies/noetic_policies/validator/constraint_validator.py with validate() method (FR-003, FR-008)
- [ ] T065 [US1] Integrate CELEvaluator for syntax checking in packages/policies/noetic_policies/validator/constraint_validator.py
- [ ] T066 [US1] Add CEL mode enforcement in packages/policies/noetic_policies/validator/constraint_validator.py (FR-014, FR-014a)
- [ ] T067 [US1] Add invariant well-formedness checking in packages/policies/noetic_policies/validator/constraint_validator.py

#### Graph Analyzer

- [ ] T068 [US1] Implement GraphAnalyzer class in packages/policies/noetic_policies/validator/graph_analyzer.py using NetworkX (from research.md)
- [ ] T069 [US1] Implement find_unreachable_states() method in packages/policies/noetic_policies/validator/graph_analyzer.py (FR-004)
- [ ] T070 [US1] Implement detect_deadlocks() method using Tarjan's algorithm in packages/policies/noetic_policies/validator/graph_analyzer.py (FR-005)
- [ ] T071 [US1] Implement verify_goal_reachable() method in packages/policies/noetic_policies/validator/graph_analyzer.py (FR-007)
- [ ] T071a [US1] Implement compute_goal_costs() method using Dijkstra's algorithm with transition cost weights in packages/policies/noetic_policies/validator/graph_analyzer.py
- [ ] T071b [US1] Implement compute_goal_min_steps() method using BFS shortest path in packages/policies/noetic_policies/validator/graph_analyzer.py
- [ ] T071c [US1] Implement check_temporal_feasibility() method comparing min_steps to max_steps bounds in packages/policies/noetic_policies/validator/graph_analyzer.py
- [ ] T072 [US1] Implement analyze() method combining all checks (reachability, deadlocks, goal costs, temporal feasibility) in packages/policies/noetic_policies/validator/graph_analyzer.py

#### Validation Modes

- [ ] T073 [US1] Implement ValidationModes class in packages/policies/noetic_policies/validator/validation_modes.py with fast/thorough mode logic (FR-016)
- [ ] T074 [US1] Implement fast mode (schema + constraint syntax + basic reachability) in packages/policies/noetic_policies/validator/validation_modes.py
- [ ] T075 [US1] Implement thorough mode (fast + cycle detection + invariant consistency + scoring consistency + temporal feasibility + edge cases) in packages/policies/noetic_policies/validator/validation_modes.py

#### Resource Monitoring

- [ ] T076 [US1] Implement ResourceMonitor class in packages/policies/noetic_policies/validator/resource_monitor.py with configurable thresholds (FR-017)
- [ ] T077 [US1] Add CPU time tracking in packages/policies/noetic_policies/validator/resource_monitor.py (default 5s warning)
- [ ] T078 [US1] Add memory usage tracking in packages/policies/noetic_policies/validator/resource_monitor.py (default 1GB warning)

#### Main Validator Orchestration

- [ ] T079 [US1] Implement PolicyValidator class in packages/policies/noetic_policies/validator/__init__.py coordinating all validators
- [ ] T080 [US1] Add validate(policy, mode) method in packages/policies/noetic_policies/validator/__init__.py returning ValidationResult
- [ ] T081 [US1] Add validate_yaml(content, mode) convenience method in packages/policies/noetic_policies/validator/__init__.py
- [ ] T082 [US1] Add validate_file(path, mode) convenience method in packages/policies/noetic_policies/validator/__init__.py
- [ ] T083 [US1] Integrate OpenTelemetry tracing in packages/policies/noetic_policies/validator/__init__.py (FR-018, FR-019)
- [ ] T084 [US1] Add comprehensive logging in packages/policies/noetic_policies/validator/__init__.py (FR-018)

#### CLI for Validation

- [ ] T085 [US1] Implement validate command in packages/policies/noetic_policies/cli/validate.py (from cli-api.md)
- [ ] T086 [US1] Add --mode option (fast/thorough) in packages/policies/noetic_policies/cli/validate.py
- [ ] T087 [US1] Add --format option (human/json) in packages/policies/noetic_policies/cli/validate.py
- [ ] T088 [US1] Add --strict, --verbose, --no-color options in packages/policies/noetic_policies/cli/validate.py
- [ ] T089 [US1] Implement human-readable output formatter in packages/policies/noetic_policies/cli/validate.py
- [ ] T090 [US1] Implement JSON output formatter in packages/policies/noetic_policies/cli/validate.py
- [ ] T091 [US1] Add proper exit codes (0=valid, 1=invalid, 2=parse error, 3=not found, 4=invalid args) in packages/policies/noetic_policies/cli/validate.py

**Checkpoint**: User Story 1 complete - developers can validate policy files and receive actionable feedback. MVP ready!

---

## Phase 4: User Story 2 - Parse Policy into Structured Format (Priority: P2)

**Goal**: Enable loading policy files into Pydantic models for programmatic access

**Independent Test**: Load policy file, access parsed structures (constraints, state_graph), verify semantic preservation

### Tests for User Story 2 (TDD - Write FIRST, Must FAIL)

#### Unit Tests - YAML Parsing

- [ ] T092 [P] [US2] Create test_policy_parser.py in packages/policies/tests/unit/test_policy_parser.py - test parse valid YAML into Policy object
- [ ] T093 [P] [US2] Add test to test_policy_parser.py - test all policy sections parsed correctly (constraints, state_graph, invariants, goal_states)
- [ ] T094 [P] [US2] Add test to test_policy_parser.py - test malformed YAML fails with clear error (error must include: 1) what's invalid, 2) where (line/col), 3) expected format)
- [ ] T095 [P] [US2] Add test to test_policy_parser.py - test parse preserves constraint expressions exactly
- [ ] T096 [P] [US2] Add test to test_policy_parser.py - test parse preserves state graph structure (nodes, edges, preconditions, effects)

#### Unit Tests - CEL Parsing

- [ ] T097 [P] [US2] Create test_cel_parser.py in packages/policies/tests/unit/test_cel_parser.py - test parse CEL expression into AST
- [ ] T098 [P] [US2] Add test to test_cel_parser.py - test CEL expression round-trip (parse then evaluate)
- [ ] T099 [P] [US2] Add test to test_cel_parser.py - test CEL syntax error provides line/column info

#### Unit Tests - Pydantic Model Validation

- [ ] T100 [P] [US2] Create test_policy_models.py in packages/policies/tests/unit/test_policy_models.py - test Policy model validates all constraints
- [ ] T101 [P] [US2] Add test to test_policy_models.py - test StateGraph model checks unique state names
- [ ] T102 [P] [US2] Add test to test_policy_models.py - test StateGraph model validates initial state exists
- [ ] T103 [P] [US2] Add test to test_policy_models.py - test Constraint model validates name pattern

#### Integration Tests

- [ ] T104 [P] [US2] Create test_parsing_workflow.py in packages/policies/tests/integration/test_parsing_workflow.py - test parse_file() end-to-end
- [ ] T105 [P] [US2] Add test to test_parsing_workflow.py - test parse then validate workflow
- [ ] T106 [P] [US2] Add test to test_parsing_workflow.py - test parse invalid file returns clear error (not Python exception)

#### Property-Based Tests

- [ ] T107 [P] [US2] Create test_parsing_properties.py in packages/policies/tests/property/test_parsing_properties.py - generate random valid policies and verify parse succeeds
- [ ] T108 [P] [US2] Add test to test_parsing_properties.py - test parse is deterministic (same input always produces same output)

### Implementation for User Story 2

#### YAML Parser

- [ ] T109 [US2] Implement PolicyParser class in packages/policies/noetic_policies/parser/policy_parser.py with PyYAML
- [ ] T110 [US2] Implement parse_yaml(content) method in packages/policies/noetic_policies/parser/policy_parser.py (FR-001)
- [ ] T111 [US2] Implement parse_file(path) method in packages/policies/noetic_policies/parser/policy_parser.py
- [ ] T112 [US2] Implement parse_dict(data) method in packages/policies/noetic_policies/parser/policy_parser.py
- [ ] T113 [US2] Add YAML syntax error handling in packages/policies/noetic_policies/parser/policy_parser.py with line numbers

#### CEL Parser

- [ ] T114 [US2] Implement CELParser class in packages/policies/noetic_policies/parser/cel_parser.py wrapping celpy
- [ ] T115 [US2] Add parse_expression() method in packages/policies/noetic_policies/parser/cel_parser.py
- [ ] T116 [US2] Add CEL syntax error enrichment (line/column from YAML context) in packages/policies/noetic_policies/parser/cel_parser.py

#### Model Integration

- [ ] T117 [US2] Integrate PolicyParser with Policy Pydantic model in packages/policies/noetic_policies/parser/policy_parser.py
- [ ] T118 [US2] Add Pydantic validation error mapping to ValidationError format in packages/policies/noetic_policies/parser/policy_parser.py
- [ ] T119 [US2] Add programmatic access methods in packages/policies/noetic_policies/parser/__init__.py (FR-010)

#### Version Detection & Migration (FR-020, FR-021, FR-022)

- [ ] T120 [US2] Implement version detection in packages/policies/noetic_policies/parser/policy_parser.py
- [ ] T121 [US2] Add support for current version (1.0) in packages/policies/noetic_policies/parser/policy_parser.py
- [ ] T122 [US2] Add support for previous version (0.9) parsing in packages/policies/noetic_policies/parser/policy_parser.py
- [ ] T123 [US2] Add deprecation warnings for old versions in packages/policies/noetic_policies/parser/policy_parser.py

**Checkpoint**: User Story 2 complete - policies can be loaded and parsed into structured format. Both US1 and US2 work independently!

---

## Phase 5: User Story 3 - Use Pre-Built Verified Policies (Priority: P3)

**Goal**: Provide production-ready standard library policies (token transfer, voting, escrow) demonstrating best practices

**Independent Test**: Import stdlib policy, validate it passes all checks, use as template

### Tests for User Story 3 (TDD - Write FIRST, Must FAIL)

#### Standard Library Validation Tests (Multi-Layer Suite per FR-012)

- [ ] T124 [P] [US3] Create test_stdlib_token_transfer.py in packages/policies/tests/integration/test_stdlib_token_transfer.py - Layer 1: static verification passes thorough mode
- [ ] T125 [P] [US3] Add test to test_stdlib_token_transfer.py - Layer 2: property-based test for invariant preservation (total supply conserved)
- [ ] T126 [P] [US3] Add test to test_stdlib_token_transfer.py - Layer 3: scenario test for zero amount transfer (edge case)
- [ ] T127 [P] [US3] Add test to test_stdlib_token_transfer.py - Layer 3: scenario test for transfer to self
- [ ] T128 [P] [US3] Add test to test_stdlib_token_transfer.py - Layer 3: scenario test for insufficient balance
- [ ] T129 [P] [US3] Add test to test_stdlib_token_transfer.py - Layer 3: scenario test for max uint256 amount
- [ ] T130 [P] [US3] Add test to test_stdlib_token_transfer.py - Layer 4: security audit checklist (overflow, underflow, reentrancy considerations)

- [ ] T131 [P] [US3] Create test_stdlib_voting.py in packages/policies/tests/integration/test_stdlib_voting.py - Layer 1: static verification passes
- [ ] T132 [P] [US3] Add test to test_stdlib_voting.py - Layer 2: property-based test for quorum invariants
- [ ] T133 [P] [US3] Add test to test_stdlib_voting.py - Layer 3: scenario test for tie vote
- [ ] T134 [P] [US3] Add test to test_stdlib_voting.py - Layer 3: scenario test for unanimous vote
- [ ] T135 [P] [US3] Add test to test_stdlib_voting.py - Layer 3: scenario test for double voting prevention
- [ ] T136 [P] [US3] Add test to test_stdlib_voting.py - Layer 4: security audit checklist

- [ ] T137 [P] [US3] Create test_stdlib_escrow.py in packages/policies/tests/integration/test_stdlib_escrow.py - Layer 1: static verification passes
- [ ] T138 [P] [US3] Add test to test_stdlib_escrow.py - Layer 2: property-based test for fund conservation
- [ ] T139 [P] [US3] Add test to test_stdlib_escrow.py - Layer 3: scenario test for timeout expiry
- [ ] T140 [P] [US3] Add test to test_stdlib_escrow.py - Layer 3: scenario test for early release
- [ ] T141 [P] [US3] Add test to test_stdlib_escrow.py - Layer 3: scenario test for dispute resolution
- [ ] T142 [P] [US3] Add test to test_stdlib_escrow.py - Layer 4: security audit checklist

- [ ] T142a [P] [US3] Create test_stdlib_research_agent.py in packages/policies/tests/integration/test_stdlib_research_agent.py - Layer 1: static verification passes thorough mode
- [ ] T142b [P] [US3] Add test to test_stdlib_research_agent.py - Layer 2: property-based test for budget constraints (budget_spent <= max_budget throughout execution)
- [ ] T142c [P] [US3] Add test to test_stdlib_research_agent.py - Layer 3: scenario test for budget exhaustion (agent stops when budget depleted)
- [ ] T142d [P] [US3] Add test to test_stdlib_research_agent.py - Layer 3: scenario test for time deadline exceeded
- [ ] T142e [P] [US3] Add test to test_stdlib_research_agent.py - Layer 3: scenario test for quality threshold not met (retry logic)
- [ ] T142f [P] [US3] Add test to test_stdlib_research_agent.py - Layer 3: scenario test for successful completion within constraints
- [ ] T142g [P] [US3] Add test to test_stdlib_research_agent.py - Layer 4: security audit checklist (SC-007)
- [ ] T142h [P] [US3] Add test to test_stdlib_research_agent.py - Layer 3: scenario test for partial budget recovery on failure (verify budget tracking on incomplete execution)

#### Comparison Tests (Constitution Principle IV)

- [ ] T142h [P] [US3] Create test_stdlib_comparison.py in packages/policies/tests/comparison/test_stdlib_comparison.py - compare token_transfer.yaml against ERC-20 standard specification requirements (all standard operations covered)
- [ ] T142i [P] [US3] Add test to test_stdlib_comparison.py - compare voting.yaml against simple majority voting reference implementation behavior
- [ ] T142j [P] [US3] Add test to test_stdlib_comparison.py - compare escrow.yaml against time-locked escrow reference implementation behavior
- [ ] T142k [P] [US3] Add test to test_stdlib_comparison.py - compare research_agent.yaml against documented research agent requirements (budget/time/quality constraints)

#### Standard Library API Tests

- [ ] T143 [P] [US3] Create test_stdlib_api.py in packages/policies/tests/unit/test_stdlib_api.py - test StandardLibrary.get() returns policy
- [ ] T144 [P] [US3] Add test to test_stdlib_api.py - test StandardLibrary.list_policies() returns all 4 policies
- [ ] T145 [P] [US3] Add test to test_stdlib_api.py - test StandardLibrary.validate_all() passes for all policies
- [ ] T146 [P] [US3] Add test to test_stdlib_api.py - test StandardLibrary.get() with invalid name raises KeyError

#### CLI Tests

- [ ] T147 [P] [US3] Create test_stdlib_cli.py in packages/policies/tests/integration/test_stdlib_cli.py - test stdlib list command
- [ ] T148 [P] [US3] Add test to test_stdlib_cli.py - test stdlib show command displays policy
- [ ] T149 [P] [US3] Add test to test_stdlib_cli.py - test stdlib copy command creates file
- [ ] T150 [P] [US3] Add test to test_stdlib_cli.py - test stdlib validate command checks all policies

### Implementation for User Story 3

#### Standard Library Policies (Production-Ready per clarification)

- [ ] T151 [P] [US3] Create token_transfer.yaml in packages/policies/noetic_policies/stdlib/token_transfer.yaml - ERC-20 compliant with comprehensive edge cases (SC-006)
- [ ] T152 [P] [US3] Add constraints for sufficient balance, positive amount, valid recipient in token_transfer.yaml
- [ ] T153 [P] [US3] Add state graph (idle → transferring → complete) in token_transfer.yaml
- [ ] T154 [P] [US3] Add invariant for total supply conservation in token_transfer.yaml
- [ ] T155 [P] [US3] Add security hardening (overflow checks, reentrancy guards) in token_transfer.yaml

- [ ] T156 [P] [US3] Create voting.yaml in packages/policies/noetic_policies/stdlib/voting.yaml - simple majority voting with comprehensive validation
- [ ] T157 [P] [US3] Add constraints for quorum, majority, valid voter in voting.yaml
- [ ] T158 [P] [US3] Add state graph (setup → voting → tallying → complete) in voting.yaml
- [ ] T159 [P] [US3] Add invariants for vote count consistency in voting.yaml
- [ ] T160 [P] [US3] Add double-voting prevention in voting.yaml

- [ ] T161 [P] [US3] Create escrow.yaml in packages/policies/noetic_policies/stdlib/escrow.yaml - time-locked escrow with security hardening
- [ ] T162 [P] [US3] Add constraints for fund availability, timeout, release conditions in escrow.yaml
- [ ] T163 [P] [US3] Add state graph (funded → locked → [released|refunded]) in escrow.yaml
- [ ] T164 [P] [US3] Add invariant for fund conservation in escrow.yaml
- [ ] T165 [P] [US3] Add timeout and dispute resolution logic in escrow.yaml

- [ ] T165a [P] [US3] Create research_agent.yaml in packages/policies/noetic_policies/stdlib/research_agent.yaml - autonomous research agent with budget/time/quality constraints (SC-007)
- [ ] T165b [P] [US3] Add constraints for budget limits, time deadlines, quality thresholds in research_agent.yaml
- [ ] T165c [P] [US3] Add state graph (planning → searching → analyzing → reporting → complete|failed) with transition costs reflecting API call expenses in research_agent.yaml
- [ ] T165d [P] [US3] Add invariants for budget conservation and quality minimums in research_agent.yaml
- [ ] T165e [P] [US3] Add retry logic and resource management in research_agent.yaml
- [ ] T165f [P] [US3] Add goal scoring (priority/reward for complete vs failed, progress conditions for quality_score/papers_found) in research_agent.yaml
- [ ] T165g [P] [US3] Add temporal bounds (max_steps for API calls, timeout_seconds for wall-clock, deadline for budget expiry) in research_agent.yaml

#### Standard Library API

- [ ] T166 [US3] Implement StandardLibrary class in packages/policies/noetic_policies/stdlib/__init__.py
- [ ] T167 [US3] Implement get(name) method in packages/policies/noetic_policies/stdlib/__init__.py (from library-api.md)
- [ ] T168 [US3] Implement list_policies() method in packages/policies/noetic_policies/stdlib/__init__.py
- [ ] T169 [US3] Implement validate_all() method in packages/policies/noetic_policies/stdlib/__init__.py (FR-012)
- [ ] T170 [US3] Add policy loading from package resources in packages/policies/noetic_policies/stdlib/__init__.py

#### CLI for Standard Library

- [ ] T171 [US3] Implement stdlib list command in packages/policies/noetic_policies/cli/stdlib.py
- [ ] T172 [US3] Implement stdlib show command in packages/policies/noetic_policies/cli/stdlib.py
- [ ] T173 [US3] Implement stdlib copy command in packages/policies/noetic_policies/cli/stdlib.py
- [ ] T174 [US3] Implement stdlib validate command in packages/policies/noetic_policies/cli/stdlib.py

**Checkpoint**: All three user stories complete - full MVP with validation, parsing, and standard library!

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, migration, CLI improvements, and final quality checks

### Policy Migration (FR-021, FR-022)

- [ ] T175 [P] Create test_migration.py in packages/policies/tests/unit/test_migration.py - test migrate v0.9 to v1.0
- [ ] T176 [P] Add test to test_migration.py - test can_migrate() checks version compatibility
- [ ] T176a [P] Add test to test_migration.py - test loading v0.8 policy fails with clear version incompatibility error (only current + 1 previous supported per FR-020)
- [ ] T176b [P] Add test to test_migration.py - test deprecation warnings emitted when loading v0.9 policy (FR-022)
- [ ] T177 Implement PolicyMigrator class in packages/policies/noetic_policies/migration/migrator.py
- [ ] T178 Implement migrate(policy, target_version) method in packages/policies/noetic_policies/migration/migrator.py
- [ ] T179 Implement can_migrate() method in packages/policies/noetic_policies/migration/migrator.py
- [ ] T180 Add v0.9 → v1.0 migration logic in packages/policies/noetic_policies/migration/migrator.py
- [ ] T181 Implement migrate CLI command in packages/policies/noetic_policies/cli/migrate.py

### CLI Enhancements

- [ ] T181a [P] Create test_cli_enhancements.py in packages/policies/tests/integration/test_cli_enhancements.py - test version command output format
- [ ] T182 [P] Implement version command in packages/policies/noetic_policies/cli/version.py showing package and policy format versions
- [ ] T183 [P] Add configuration file support in packages/policies/noetic_policies/cli/__init__.py (~/.config/noetic/policies.yaml)
- [ ] T183a [P] Add test to test_cli_enhancements.py - test config file loading and precedence
- [ ] T184 [P] Add environment variable support in packages/policies/noetic_policies/cli/__init__.py (NOETIC_POLICIES_CONFIG, NOETIC_NO_COLOR, NOETIC_POLICIES_MODE)
- [ ] T184a [P] Add test to test_cli_enhancements.py - test environment variable override behavior
- [ ] T185 [P] Add shell completion support in packages/policies/noetic_policies/cli/__init__.py (bash, zsh, fish)
- [ ] T186 Setup CLI entry point in packages/policies/pyproject.toml (noetic-policies command)

### Documentation (FR-015, SC-009)

- [ ] T187 [P] Create policy-specification.md in packages/policies/docs/policy-specification.md - complete policy format reference with CEL modes
- [ ] T187a Verify policy-specification.md covers ALL FR requirements (FR-001 through FR-022) including: cel_mode field format (FR-015), transition cost semantics (static/dynamic/default) (FR-015a), temporal bounds semantics (max_steps/deadline/timeout_seconds at policy and goal level) (FR-015b), goal scoring semantics (priority/reward/progress_conditions) (FR-015c)
- [ ] T188 [P] Create cel-guide.md in packages/policies/docs/cel-guide.md - CEL expression syntax and examples for each mode (safe/full/extended)
- [ ] T189 [P] Create api-reference/ directory in packages/policies/docs/api-reference/ with auto-generated docs from docstrings
- [ ] T190 [P] Copy quickstart.md to packages/policies/docs/quickstart.md from specs/001-noetic-policies/quickstart.md
- [ ] T191 [P] Create error-codes.md in packages/policies/docs/error-codes.md documenting all error codes with examples

### Type Safety & Quality

- [ ] T193 [P] Run mypy strict mode on entire codebase and fix all type errors
- [ ] T194 [P] Run ruff linter and fix all issues
- [ ] T195 [P] Run black formatter on all files
- [ ] T196 Run pytest with coverage report and verify ≥80% coverage (constitution requirement)
- [ ] T197 [P] Add docstrings (Google style) to all public APIs
- [ ] T198 Check for TODO comments in main branch (none allowed per constitution)

### Final Integration

- [ ] T199 Run all 4 stdlib policies (token, voting, escrow, research agent) through complete 4-layer verification suite: (1) static verification in thorough mode, (2) property-based tests for invariant preservation, (3) scenario-based edge case tests, (4) security audit checklist - verify all layers pass (FR-012, SC-004)
- [ ] T200 Run performance benchmarks to verify fast mode <1s (SC-001) and thorough mode 100% accuracy (SC-002)
- [ ] T201 Create standardized error corpus with 20+ common policy mistakes (missing sections, malformed CEL, unreachable states, type mismatches, etc.)
- [ ] T201a Conduct user testing with 10+ developers: each developer attempts to fix errors from corpus using only error messages (no documentation access)
- [ ] T201b Measure SC-003: verify 90% of errors are fixed correctly without consulting external documentation
- [ ] T202 Verify OpenTelemetry spans are created for all major operations (FR-019)
- [ ] T203 Test CLI in all output modes (human, json) and verify exit codes
- [ ] T204 Run quickstart tutorial end-to-end to verify SC-009 (functional correctness and <30 minute completion time)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (Validation) can start immediately after Foundational
  - User Story 2 (Parsing) can start immediately after Foundational - independent of US1
  - User Story 3 (Standard Library) depends on US1 (needs validator) and US2 (needs parser)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Validation)**: Independent - depends only on Foundational phase
- **User Story 2 (P2 - Parsing)**: Independent - depends only on Foundational phase
- **User Story 3 (P3 - Standard Library)**: Depends on US1 and US2 (needs both validator and parser)

### Within Each User Story (TDD Workflow)

1. **Tests FIRST** - All tests for a story written and VERIFIED TO FAIL
2. **Models** - Pydantic models (already done in Foundational)
3. **Implementation** - Core logic to make tests pass
4. **Integration** - Wire components together
5. **CLI** - Expose functionality via command line
6. **Verify** - All tests pass, story independently testable

### Parallel Opportunities

**Phase 1 (Setup)**: All tasks T003-T008 can run in parallel

**Phase 2 (Foundational)**:
- All data model tasks T009-T018 can run in parallel
- All observability tasks T019-T021 can run in parallel
- CEL evaluator tasks T022-T026 must run sequentially (dependencies)

**Phase 3 (User Story 1)**:
- All unit test creation tasks T027-T059 can run in parallel (different test files)
- Implementation tasks have some dependencies (validators → orchestration → CLI)

**Phase 4 (User Story 2)**:
- All unit test tasks T092-T108 can run in parallel
- Can run ALL of User Story 2 in parallel with User Story 1 (different files)

**Phase 5 (User Story 3)**:
- All stdlib policy tests T124-T150 can run in parallel (different policies)
- All stdlib policy creation tasks T151-T165 can run in parallel (different files)

**Phase 6 (Polish)**:
- Documentation tasks T187-T192 can run in parallel
- Quality tasks T193-T198 can run in parallel

---

## Parallel Example: All User Stories After Foundation

Once Phase 2 (Foundational) is complete, a team could work on all three user stories simultaneously:

```bash
# Developer A: User Story 1 (Validation)
Tasks T027-T091: Write validation tests, implement validators, add CLI

# Developer B: User Story 2 (Parsing) - PARALLEL with A
Tasks T092-T123: Write parsing tests, implement parsers, add version support

# Developer C: User Story 3 (Standard Library) - Start after US1+US2 complete
Tasks T124-T174: Write stdlib tests, create production policies, add CLI
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T026) - CRITICAL
3. Complete Phase 3: User Story 1 (T027-T091, including T031a)
4. **STOP and VALIDATE**:
   - Run all US1 tests
   - Try quickstart validation examples
   - Test CLI validation commands
   - Verify <1s fast mode performance
5. **MVP READY** - Can validate policies!

### Incremental Delivery

1. **Foundation** (Phase 1+2) → Models, observability, CEL evaluator ready
2. **MVP** (Phase 3) → Validation works, can catch policy errors
3. **Parsing** (Phase 4) → Programmatic access to policies
4. **Standard Library** (Phase 5) → Production examples available
5. **Polish** (Phase 6) → Migration, docs, final quality

Each phase adds value without breaking previous phases.

### Parallel Team Strategy

With 3 developers:

1. **Together**: Complete Setup + Foundational (Phase 1+2)
2. **Split after Foundational**:
   - Dev A: User Story 1 (Validation)
   - Dev B: User Story 2 (Parsing)
   - Dev C: Wait for US1+US2, then start User Story 3
3. **Together**: Polish phase (Phase 6)

---

## Task Statistics

- **Total Tasks**: ~275 (updated after remediation analysis)
- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 24 tasks (BLOCKS user stories - includes state schema models, ProgressCondition, TemporalBounds, CEL mode config tests)
- **Phase 3 (US1 - Validation)**: ~100 tasks (~52 tests + ~48 implementation - includes scoring validation, temporal feasibility, cost-aware graph analysis, OpenTelemetry property tests, comparison tests)
- **Phase 4 (US2 - Parsing)**: 33 tasks (18 tests + 15 implementation)
- **Phase 5 (US3 - Standard Library)**: 70 tasks (39 tests + 31 implementation - includes scoring/temporal for research agent, comparison tests)
- **Phase 6 (Polish)**: 40 tasks (includes user testing for SC-003, documentation verification, CLI tests)

**Parallel Opportunities**: 140+ tasks marked [P] can run in parallel

**Test Tasks**: ~115 test tasks (TDD approach per constitution - includes Unit, Integration, Property-based, Comparison per Constitution IV)
**Implementation Tasks**: ~160 implementation tasks

---

## Notes

- **[P]** marker indicates tasks that can run in parallel (different files, no dependencies)
- **[US1]**, **[US2]**, **[US3]** markers map tasks to user stories for traceability
- **TDD Required**: Tests MUST be written first, MUST fail before implementation
- **80% Coverage**: Constitution requirement verified in T196
- **Fast Mode <1s**: Performance requirement verified in T058, T200
- All 4 standard library policies must pass multi-layer verification suite (T124-T142g, T199)
- Error messages must be actionable per SC-003 (verified in T201)
- Quickstart must complete in <30 minutes per SC-009 (verified in T204)
- Scoring validation (FR-008d/e/f): transition costs, goal priority/reward, progress conditions
- Temporal validation (FR-008g/h): max_steps, deadline, timeout_seconds; hierarchy checking
- Cost-aware graph analysis: Dijkstra's for goal costs, BFS for min steps, temporal feasibility (SC-012)
- Research agent stdlib must demonstrate scoring + temporal features (T165f, T165g)
