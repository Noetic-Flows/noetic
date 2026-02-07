"""Policy validator orchestration (T079-T084)."""

import time
from typing import Any

from opentelemetry import trace

from noetic_policies.models import ValidationResult, ValidationError
from noetic_policies.models.policy import Policy
from noetic_policies.observability.logger import get_logger
from noetic_policies.observability.tracer import get_tracer
from noetic_policies.validator.graph_analyzer import GraphAnalyzer
from noetic_policies.validator.schema_validator import SchemaValidator

__all__ = ["PolicyValidator"]


class PolicyValidator:
    """
    Main policy validator coordinating all validation components.

    Implements FR-016 (dual validation modes).
    """

    def __init__(self, tracer: trace.Tracer | None = None):
        """
        Initialize policy validator.

        Args:
            tracer: Optional OpenTelemetry tracer for observability
        """
        self.tracer = tracer or get_tracer()
        self.logger = get_logger()
        self.schema_validator = SchemaValidator()
        self.graph_analyzer = GraphAnalyzer()

    def validate(self, policy: Policy, mode: str = "fast") -> ValidationResult:
        """
        Validate a policy.

        Args:
            policy: Parsed policy object
            mode: Validation mode - "fast" or "thorough"

        Returns:
            ValidationResult with errors, warnings, and metadata
        """
        with self.tracer.start_as_current_span("policy.validate") as span:
            span.set_attribute("policy.name", policy.name or "unnamed")
            span.set_attribute("policy.version", policy.version)
            span.set_attribute("validation.mode", mode)

            start_time = time.perf_counter()
            errors: list[ValidationError] = []
            warnings: list[ValidationError] = []

            # Schema validation (both modes)
            with self.tracer.start_as_current_span("policy.validate.schema"):
                errors.extend(self.schema_validator.validate(policy))

            # Graph analysis
            if mode == "fast":
                # Fast mode: Basic reachability only
                with self.tracer.start_as_current_span("policy.validate.graph.basic"):
                    unreachable = self.graph_analyzer.find_unreachable_states(
                        policy.state_graph, policy.state_graph.initial
                    )
                    if unreachable:
                        errors.append(
                            ValidationError(
                                code="E004",
                                message=f"Unreachable states detected: {unreachable}",
                                severity="error",
                                fix_suggestion="Add transitions to make states reachable or remove them",
                            )
                        )

            elif mode == "thorough":
                # Thorough mode: Complete analysis
                with self.tracer.start_as_current_span("policy.validate.graph.thorough"):
                    result = self.graph_analyzer.analyze(
                        policy.state_graph,
                        policy.state_graph.initial,
                        policy.goal_states,
                        policy.temporal_bounds,
                    )

                    # Report unreachable states
                    if result.unreachable_states:
                        errors.append(
                            ValidationError(
                                code="E004",
                                message=f"Unreachable states: {result.unreachable_states}",
                                severity="error",
                                fix_suggestion="Add transitions or remove unreachable states",
                            )
                        )

                    # Report deadlocks
                    if result.deadlock_sccs:
                        for scc in result.deadlock_sccs:
                            errors.append(
                                ValidationError(
                                    code="E005",
                                    message=f"Deadlock detected in states: {scc}",
                                    severity="error",
                                    fix_suggestion="Add exit transition from the cycle",
                                )
                            )

                    # Report unreachable goals
                    if policy.goal_states and not result.goal_reachable:
                        errors.append(
                            ValidationError(
                                code="E006",
                                message="No goal states are reachable from initial state",
                                severity="error",
                                fix_suggestion="Add transitions to make goal states reachable",
                            )
                        )

                    # Report temporally infeasible goals
                    if result.temporally_infeasible_goals:
                        for goal_name in result.temporally_infeasible_goals:
                            min_steps = result.goal_min_steps.get(goal_name, 0)
                            errors.append(
                                ValidationError(
                                    code="W002",
                                    message=f"Goal '{goal_name}' is temporally infeasible: requires {min_steps} steps",
                                    severity="warning",
                                    fix_suggestion="Increase max_steps or reduce path length to goal",
                                )
                            )

            duration_ms = (time.perf_counter() - start_time) * 1000
            span.set_attribute("validation.duration_ms", duration_ms)
            span.set_attribute("validation.error_count", len(errors))

            # Build result
            is_valid = len(errors) == 0
            metadata: dict[str, Any] = {
                "mode": mode,
                "duration_ms": duration_ms,
                "checks_performed": self._get_checks_performed(mode),
            }

            return ValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                metadata=metadata,
            )

    def validate_yaml(self, content: str, mode: str = "fast") -> ValidationResult:
        """
        Parse and validate YAML in one step.

        Args:
            content: YAML policy specification
            mode: Validation mode

        Returns:
            ValidationResult
        """
        # Import here to avoid circular dependency
        from noetic_policies.parser import PolicyParser

        parser = PolicyParser()
        try:
            policy = parser.parse_yaml(content)
            return self.validate(policy, mode)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        code="E100",
                        message=f"Parse error: {e}",
                        severity="error",
                        fix_suggestion="Check YAML syntax and policy structure",
                    )
                ],
                warnings=[],
                metadata={"mode": mode},
            )

    def validate_file(self, file_path: str, mode: str = "fast") -> ValidationResult:
        """
        Parse and validate file in one step.

        Args:
            file_path: Path to policy file
            mode: Validation mode

        Returns:
            ValidationResult
        """
        from pathlib import Path

        from noetic_policies.parser import PolicyParser

        parser = PolicyParser()
        try:
            policy = parser.parse_file(Path(file_path))
            return self.validate(policy, mode)
        except FileNotFoundError:
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        code="E101",
                        message=f"File not found: {file_path}",
                        severity="error",
                    )
                ],
                warnings=[],
                metadata={"mode": mode},
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        code="E100",
                        message=f"Parse error: {e}",
                        severity="error",
                        fix_suggestion="Check YAML syntax and policy structure",
                    )
                ],
                warnings=[],
                metadata={"mode": mode},
            )

    def _get_checks_performed(self, mode: str) -> list[str]:
        """Get list of checks performed in this mode."""
        checks = ["schema", "constraints", "basic_graph"]

        if mode == "thorough":
            checks.extend(
                [
                    "deadlock_detection",
                    "goal_reachability",
                    "temporal_feasibility",
                    "cost_analysis",
                ]
            )

        return checks
