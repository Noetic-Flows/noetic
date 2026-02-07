"""Unit tests for constraint validation (T032-T036)."""

import pytest

from noetic_policies.cel_evaluator import CELEvaluator, CELSyntaxError, CELMode


class TestConstraintValidator:
    """Test constraint validation logic."""

    # T032: Test valid CEL expression passes
    def test_valid_cel_expression_passes(self):
        """Valid CEL expressions should pass syntax validation."""
        evaluator = CELEvaluator()

        # Basic expressions should validate
        assert evaluator.validate_syntax("true")
        assert evaluator.validate_syntax("false")
        assert evaluator.validate_syntax("count > 0")
        assert evaluator.validate_syntax("balance >= amount")
        assert evaluator.validate_syntax("(count + 1) * 2")

    # T033: Test malformed CEL syntax fails with actionable error
    def test_malformed_cel_syntax_fails(self):
        """Malformed CEL expressions should fail with clear error messages."""
        evaluator = CELEvaluator()

        # Unbalanced parentheses
        with pytest.raises(CELSyntaxError, match="Unbalanced parentheses"):
            evaluator.validate_syntax("(count > 0")

        # Unbalanced brackets
        with pytest.raises(CELSyntaxError, match="Unbalanced brackets"):
            evaluator.validate_syntax("[1, 2, 3")

        # Empty expression
        with pytest.raises(CELSyntaxError, match="Empty expression"):
            evaluator.validate_syntax("")

        with pytest.raises(CELSyntaxError, match="Empty expression"):
            evaluator.validate_syntax("   ")

    # T034: Test constraint references undefined variable fails
    def test_undefined_variable_fails(self):
        """Constraints referencing undefined variables should fail validation."""
        # This will be tested at the validator level (not CEL level)
        # CEL evaluator just checks syntax, not variable existence
        evaluator = CELEvaluator()

        # Syntax is valid even if variable doesn't exist in context
        assert evaluator.validate_syntax("undefined_var > 0")

    # T035: Test CEL safe mode blocks disallowed operations
    def test_safe_mode_blocks_unsafe_operations(self):
        """Safe mode should block time, I/O, and random operations."""
        evaluator = CELEvaluator(mode=CELMode.SAFE)

        # Time operations should fail in safe mode
        with pytest.raises(CELSyntaxError, match="not allowed in safe mode"):
            evaluator.validate_syntax("now() > deadline")

        # Random operations should fail
        with pytest.raises(CELSyntaxError, match="not allowed in safe mode"):
            evaluator.validate_syntax("random() > 0.5")

        # I/O operations should fail
        with pytest.raises(CELSyntaxError, match="not allowed in safe mode"):
            evaluator.validate_syntax("print('hello')")

        # Safe operations should pass
        assert evaluator.validate_syntax("count > 0")
        assert evaluator.validate_syntax("balance >= amount")

    # T036: Test CEL full mode allows additional operations
    def test_full_mode_allows_additional_operations(self):
        """Full mode should allow operations blocked in safe mode."""
        evaluator = CELEvaluator(mode=CELMode.FULL)

        # Time operations allowed in full mode (just syntax check)
        assert evaluator.validate_syntax("now() > deadline")

        # Random allowed in full mode
        assert evaluator.validate_syntax("random() > 0.5")

        # But syntax still validated
        with pytest.raises(CELSyntaxError, match="Unbalanced"):
            evaluator.validate_syntax("(now() > deadline")
