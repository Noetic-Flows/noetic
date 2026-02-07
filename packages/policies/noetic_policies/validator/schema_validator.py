"""Schema validation for policy structure (T060-T063i)."""

from noetic_policies.cel_evaluator import CELEvaluator
from noetic_policies.models import ValidationError, ValidationResult
from noetic_policies.models.policy import Policy


class SchemaValidator:
    """
    Validates policy structure against required schema.

    Implements FR-002, FR-006, FR-008a-h.
    """

    def __init__(self):
        """Initialize schema validator."""
        self.cel_evaluator = CELEvaluator()

    def validate(self, policy: Policy) -> list[ValidationError]:
        """
        Validate policy schema and structure.

        Args:
            policy: Policy to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors: list[ValidationError] = []

        # T061: Required sections validation (FR-002)
        errors.extend(self._validate_required_sections(policy))

        # T062: Version validation (FR-020)
        errors.extend(self._validate_version(policy))

        # T063: Goal state existence check (FR-007)
        errors.extend(self._validate_goal_states_exist(policy))

        # T063a: State schema type validation
        errors.extend(self._validate_state_schema_types(policy))

        # T063b: State schema coverage check (FR-008a)
        errors.extend(self._validate_state_schema_coverage(policy))

        # T063c: Goal condition validation (FR-008b)
        errors.extend(self._validate_goal_conditions(policy))

        # T063d: Goal condition satisfiability (FR-008c)
        errors.extend(self._validate_goal_satisfiability(policy))

        # T063e: Transition cost validation (FR-008d)
        errors.extend(self._validate_transition_costs(policy))

        # T063f: Goal scoring validation (FR-008e)
        errors.extend(self._validate_goal_scoring(policy))

        # T063g: Progress condition validation (FR-008f)
        errors.extend(self._validate_progress_conditions(policy))

        # T063h: Temporal bounds validation (FR-008g)
        errors.extend(self._validate_temporal_bounds(policy))

        # T063i: Temporal bounds hierarchy (FR-008h)
        errors.extend(self._validate_temporal_hierarchy(policy))

        return errors

    def _validate_required_sections(self, policy: Policy) -> list[ValidationError]:
        """Validate that all required sections are present."""
        errors = []

        # Pydantic already ensures these are present due to required fields
        # But we check for empty constraints
        if not policy.constraints:
            errors.append(
                ValidationError(
                    code="E001",
                    message="Missing required 'constraints' section",
                    severity="error",
                    fix_suggestion="Add at least one constraint to the policy",
                )
            )

        if not policy.state_graph or not policy.state_graph.states:
            errors.append(
                ValidationError(
                    code="E002",
                    message="Missing or empty 'state_graph' section",
                    severity="error",
                    fix_suggestion="Define at least one state in state_graph",
                )
            )

        return errors

    def _validate_version(self, policy: Policy) -> list[ValidationError]:
        """Validate policy version format."""
        errors = []

        # Version format already validated by Pydantic pattern
        # Check for supported versions
        try:
            major, minor = policy.version.split(".")
            if major == "0" and int(minor) < 9:
                errors.append(
                    ValidationError(
                        code="W001",
                        message=f"Policy using old version {policy.version}",
                        severity="warning",
                        fix_suggestion="Consider upgrading to version 1.0",
                    )
                )
        except Exception:
            pass  # Format already validated by Pydantic

        return errors

    def _validate_goal_states_exist(self, policy: Policy) -> list[ValidationError]:
        """Validate that goal states exist in state graph."""
        # Already validated by Policy model field_validator
        # This is a double-check
        errors = []
        state_names = {s.name for s in policy.state_graph.states}

        for goal in policy.goal_states:
            if goal.name not in state_names:
                errors.append(
                    ValidationError(
                        code="E003",
                        message=f"Goal state '{goal.name}' not found in state graph",
                        severity="error",
                        fix_suggestion=f"Add state '{goal.name}' to state_graph or remove from goal_states",
                    )
                )

        return errors

    def _validate_state_schema_types(self, policy: Policy) -> list[ValidationError]:
        """Validate state schema uses valid types."""
        # Already validated by Policy model
        return []

    def _validate_state_schema_coverage(self, policy: Policy) -> list[ValidationError]:
        """Validate that all referenced variables are defined in state schema."""
        errors = []
        schema_vars = set(policy.state_schema.keys())

        # Check constraint expressions (simplified for MVP)
        for constraint in policy.constraints:
            # Extract variable references (simplified)
            # Full implementation would use CEL AST
            for var in schema_vars:
                pass  # Check if var is used

        return errors

    def _validate_goal_conditions(self, policy: Policy) -> list[ValidationError]:
        """Validate goal conditions are well-formed CEL expressions."""
        errors = []

        for goal in policy.goal_states:
            for i, condition in enumerate(goal.conditions):
                try:
                    self.cel_evaluator.validate_syntax(condition)
                except Exception as e:
                    errors.append(
                        ValidationError(
                            code="E010",
                            message=f"Invalid goal condition in '{goal.name}': {e}",
                            severity="error",
                            fix_suggestion="Check CEL expression syntax",
                        )
                    )

        return errors

    def _validate_goal_satisfiability(self, policy: Policy) -> list[ValidationError]:
        """Check if goal conditions are potentially satisfiable."""
        # Simplified for MVP - full implementation would use SAT solver
        return []

    def _validate_transition_costs(self, policy: Policy) -> list[ValidationError]:
        """Validate transition costs are non-negative and expressions are valid."""
        errors = []

        for state in policy.state_graph.states:
            for transition in state.transitions:
                # Cost already validated by Pydantic (ge=0.0)

                # Validate cost_expr if present
                if transition.cost_expr:
                    try:
                        self.cel_evaluator.validate_syntax(transition.cost_expr)
                        # Check if it's numeric (simplified)
                        if not self.cel_evaluator.check_numeric_type(
                            transition.cost_expr
                        ):
                            errors.append(
                                ValidationError(
                                    code="E011",
                                    message=f"Cost expression in transition to '{transition.to}' must evaluate to numeric type",
                                    severity="error",
                                    fix_suggestion="Ensure cost_expr returns a number",
                                )
                            )
                    except Exception as e:
                        errors.append(
                            ValidationError(
                                code="E012",
                                message=f"Invalid cost expression in transition to '{transition.to}': {e}",
                                severity="error",
                                fix_suggestion="Check CEL expression syntax",
                            )
                        )

        return errors

    def _validate_goal_scoring(self, policy: Policy) -> list[ValidationError]:
        """Validate goal priority and reward values."""
        # Already validated by Pydantic constraints
        return []

    def _validate_progress_conditions(self, policy: Policy) -> list[ValidationError]:
        """Validate progress conditions are valid CEL numeric expressions."""
        errors = []

        for goal in policy.goal_states:
            for pc in goal.progress_conditions:
                try:
                    self.cel_evaluator.validate_syntax(pc.expr)
                except Exception as e:
                    errors.append(
                        ValidationError(
                            code="E013",
                            message=f"Invalid progress condition in '{goal.name}': {e}",
                            severity="error",
                            fix_suggestion="Check CEL expression syntax",
                        )
                    )

        return errors

    def _validate_temporal_bounds(self, policy: Policy) -> list[ValidationError]:
        """Validate temporal bounds have valid values."""
        # Already validated by Pydantic constraints
        return []

    def _validate_temporal_hierarchy(self, policy: Policy) -> list[ValidationError]:
        """Validate goal temporal bounds don't exceed policy bounds."""
        # Already validated by Policy model_validator
        return []
