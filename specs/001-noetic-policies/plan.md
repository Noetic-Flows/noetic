# Implementation Plan: Noetic Policies Package

**Branch**: `001-noetic-policies` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-noetic-policies/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build the noetic-policies package as the foundation of the Noetic ecosystem. This package provides policy specification format, parsing, validation, and a standard library of production-ready policies. The package enables developers to write declarative policies that govern autonomous AI agents and smart contracts, with comprehensive static analysis to catch errors before runtime. Dual validation modes (fast <1s, thorough complete analysis) with OpenTelemetry observability and format versioning support.

## Technical Context

**Language/Version**: Python 3.11+ (per constitution Technology Stack)
**Primary Dependencies**: PyYAML (policy parsing), celpy (CEL constraint evaluation), pydantic (data validation), opentelemetry-api (observability), opentelemetry-sdk (observability), networkx (state graph analysis - RESOLVED: NetworkX 3.6.1+ selected per research.md)
**Storage**: File-based policy files (YAML), no database
**Testing**: pytest (per constitution), pytest-cov (coverage), hypothesis (property-based testing for validation rules - RESOLVED: pytest + Hypothesis + pytest-benchmark per research.md)
**Target Platform**: Cross-platform (Linux, macOS, Windows) - local developer environments
**Project Type**: Python library package with CLI exposure (per constitution Principle V)
**Performance Goals**: Fast mode validation <1 second (SC-001), thorough mode no constraint (SC-002)
**Constraints**: Soft resource limits with warnings (clarification Q2), comprehensive logging always enabled (clarification Q3)
**Scale/Scope**: Support policies with thousands of states (edge case), production-ready standard library (4 policies: ERC-20 token, voting, escrow, research agent)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Policy-First Architecture ✅
- ✅ Feature separates policy specification (YAML+CEL declarative) from execution (kernel/compiler interpret)
- ✅ No business logic in this package - only parsing, validation, standard library
- ✅ Policies independently testable via validation

### II. Determinism & Reproducibility ✅
- ✅ CEL used for all constraint expressions (deterministic, sandboxed)
- ✅ No platform-specific functions - validation is platform-agnostic
- ✅ Validation results deterministic for same policy

### III. Type Safety & Static Verification ✅
- ✅ Static analysis of state graphs (FR-004, FR-005, FR-007)
- ✅ CEL type checking at validation time (FR-003, FR-014)
- ✅ Schema validation (FR-002)
- ✅ Python strict type hints (mypy strict mode per constitution)

### IV. Test-Driven Development (NON-NEGOTIABLE) ✅
- ✅ TDD workflow required: tests written → approved → fail → implement
- ✅ 80% coverage minimum (constitution)
- ✅ Test categories: Unit (parser, validator), Integration (end-to-end validation), Property-based (validation rules), Comparison (stdlib policies vs requirements)
- ✅ Standard library policies must pass all checks (FR-012)

### V. Library-First with CLI Exposure ✅
- ✅ Core implemented as importable library (FR-010: programmatic access)
- ✅ CLI tools for validation (text I/O: policy file in → validation results out)
- ✅ JSON + human-readable output formats
- ✅ Clear API boundary (no dependencies on kernel/compiler per constitution)

### VI. Standard Library as Proof of Quality ✅
- ✅ Stdlib policies demonstrate patterns (token, voting, escrow)
- ✅ Production-ready quality (clarification Q5: comprehensive coverage, security hardening)
- ✅ Serves as regression suite (FR-012: all pass static verification)
- ✅ Validates hypothesis 1: policy expressiveness (SC-006, SC-007)

### VII. Simplicity & YAGNI ✅
- ✅ Phase 1 scope: Single package, no multi-agent, no Data Mesh
- ✅ Local file-based policies, no database
- ✅ No abstractions for hypothetical features
- ✅ Complexity justified: dual validation modes needed for usability (clarification Q1)

### Architecture Constraints ✅
- ✅ Policies package: no dependencies on kernel/compiler
- ✅ Technology stack compliant: Python 3.11+, Poetry, celpy, pydantic, PyYAML, pytest
- ✅ OpenTelemetry for observability (clarification Q3, FR-019)

### Quality Standards ✅
- ✅ Type hints (mypy strict), docstrings (Google style), linting (ruff), formatting (black)
- ✅ 80% coverage, no TODOs in main
- ✅ Documentation: policy format spec (FR-015), getting started (SC-009)
- ✅ Observability: comprehensive logging (FR-018), OpenTelemetry (FR-019)
- ✅ Versioning: support current + 1 previous, auto-migration (FR-020, FR-021, FR-022)

**GATE STATUS**: ✅ PASSED - All constitution principles satisfied, no violations to justify

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
packages/policies/              # noetic-policies package
├── noetic_policies/           # Python package
│   ├── __init__.py
│   ├── parser/                # Policy file parsing (YAML + CEL)
│   │   ├── __init__.py
│   │   ├── policy_parser.py
│   │   └── cel_parser.py
│   ├── validator/             # Static analysis & validation
│   │   ├── __init__.py
│   │   ├── schema_validator.py
│   │   ├── constraint_validator.py
│   │   ├── graph_analyzer.py  # State graph reachability/deadlock
│   │   └── validation_modes.py # Fast vs thorough modes
│   ├── models/                # Pydantic models for policy entities
│   │   ├── __init__.py
│   │   ├── policy.py
│   │   ├── constraint.py
│   │   ├── state_graph.py
│   │   └── version.py
│   ├── stdlib/                # Standard library policies
│   │   ├── __init__.py
│   │   ├── token_transfer.yaml
│   │   ├── voting.yaml
│   │   ├── escrow.yaml
│   │   └── research_agent.yaml
│   ├── observability/         # OpenTelemetry integration
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── tracer.py
│   │   └── metrics.py
│   ├── migration/             # Policy format migration
│   │   ├── __init__.py
│   │   └── migrator.py
│   └── cli/                   # CLI interface
│       ├── __init__.py
│       └── validate.py
├── tests/
│   ├── unit/
│   │   ├── test_parser.py
│   │   ├── test_validator.py
│   │   ├── test_graph_analyzer.py
│   │   └── test_migration.py
│   ├── integration/
│   │   ├── test_validation_workflow.py
│   │   └── test_stdlib_policies.py
│   └── property/              # Property-based tests
│       └── test_validation_properties.py
├── docs/
│   ├── policy-specification.md
│   ├── cel-guide.md
│   └── api-reference/
├── pyproject.toml             # Poetry configuration
└── README.md
```

**Structure Decision**: Monorepo package structure per constitution. The `packages/policies/` directory contains the complete noetic-policies package as a standalone Python library with CLI exposure. This follows constitution Principle V (Library-First with CLI Exposure) and Architecture Constraints (clear package boundaries, no dependencies on kernel/compiler).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations - all constitution principles satisfied.

---

## Planning Phase Complete

**Date**: 2026-02-05

### Artifacts Generated

**Phase 0 - Research**:
- ✅ `research.md`: Technical decisions for graph analysis (NetworkX), testing patterns (pytest + Hypothesis + pytest-benchmark), CEL evaluation, OpenTelemetry integration

**Phase 1 - Design & Contracts**:
- ✅ `data-model.md`: Pydantic models for Policy, Constraint, StateGraph, State, Transition, Invariant, ValidationResult, ValidationError
- ✅ `contracts/library-api.md`: Python API (PolicyParser, PolicyValidator, GraphAnalyzer, CELEvaluator, StandardLibrary, PolicyMigrator)
- ✅ `contracts/cli-api.md`: CLI commands (validate, migrate, stdlib, version)
- ✅ `quickstart.md`: 30-minute tutorial for SC-009
- ✅ Agent context updated: CLAUDE.md with technology stack

### Key Technical Decisions

1. **Graph Analysis**: NetworkX 3.6.1+ (pure Python, excellent type hints, meets performance requirements)
2. **Testing**: pytest + Hypothesis + pytest-benchmark (property-based, performance, observability testing)
3. **CEL Evaluation**: celpy library (deterministic, Python 3.11+ compatible)
4. **Dual Validation Modes**: Fast (<1s) for development, Thorough (complete analysis) for CI/CD
5. **OpenTelemetry**: Comprehensive logging via opentelemetry-api/sdk (clarification Q3)
6. **Versioning**: Semantic versioning with migration support (clarification Q4)
7. **Standard Library**: Production-ready policies (token, voting, escrow) per clarification Q5

### Constitution Compliance

All 7 core principles satisfied:
- ✅ Policy-First Architecture
- ✅ Determinism & Reproducibility (CEL)
- ✅ Type Safety & Static Verification (Pydantic + mypy strict)
- ✅ Test-Driven Development (80% coverage, pytest suite)
- ✅ Library-First with CLI Exposure
- ✅ Standard Library as Proof of Quality
- ✅ Simplicity & YAGNI (Phase 1 scope validated)

### Next Step

Run `/speckit.tasks` to generate implementation tasks from this plan.
