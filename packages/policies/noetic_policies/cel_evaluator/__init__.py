"""CEL (Common Expression Language) evaluator for constraint expressions."""

from typing import Any

# Note: celpy will be imported when actually implementing CEL evaluation
# For now, we provide a minimal implementation structure

__all__ = ["CELEvaluator", "CELMode", "CELSyntaxError", "CELEvaluationError"]


# Custom exceptions
class CELSyntaxError(Exception):
    """Raised when a CEL expression has invalid syntax."""

    pass


class CELEvaluationError(Exception):
    """Raised when CEL expression evaluation fails."""

    pass


# T026: CEL mode configuration
class CELMode:
    """CEL evaluation mode configuration."""

    SAFE = "safe"  # Deterministic operations only (default)
    FULL = "full"  # Complete CEL standard library
    EXTENDED = "extended"  # Custom extensions allowed

    # T025: Safe mode operations (deterministic subset)
    SAFE_OPERATIONS = {
        # Comparison operators
        "==",
        "!=",
        "<",
        "<=",
        ">",
        ">=",
        # Logical operators
        "&&",
        "||",
        "!",
        # Arithmetic operators
        "+",
        "-",
        "*",
        "/",
        "%",
        # String operations
        "contains",
        "startsWith",
        "endsWith",
        "matches",
        # List operations
        "size",
        "in",
        # Type conversions
        "int",
        "double",
        "string",
        "bool",
    }

    # Operations excluded in safe mode
    UNSAFE_OPERATIONS = {
        # I/O operations
        "print",
        "read",
        "write",
        # Time-dependent (non-deterministic)
        "now",
        "timestamp",
        # Random (non-deterministic)
        "random",
        # External calls
        "call",
        "invoke",
    }


# T022-T024: CELEvaluator class
class CELEvaluator:
    """
    Evaluator for CEL constraint expressions.

    Provides deterministic constraint evaluation with configurable restriction modes.
    """

    def __init__(self, mode: str = CELMode.SAFE):
        """
        Initialize CEL evaluator.

        Args:
            mode: Evaluation mode - "safe" (default), "full", or "extended"
        """
        self.mode = mode
        if mode not in {CELMode.SAFE, CELMode.FULL, CELMode.EXTENDED}:
            raise ValueError(f"Invalid CEL mode: {mode}")

    def evaluate(self, expr: str, context: dict[str, Any]) -> Any:
        """
        Evaluate CEL expression in given context.

        Args:
            expr: CEL expression string
            context: Variable context dictionary

        Returns:
            Expression result (typically bool for constraints)

        Raises:
            CELSyntaxError: If expression syntax is invalid
            CELEvaluationError: If evaluation fails
        """
        # T023: Implement evaluate() method
        # For MVP: Basic expression evaluation
        # This is a placeholder - full CEL implementation will use celpy library

        try:
            # Validate syntax first
            self.validate_syntax(expr)

            # Simple evaluation for basic expressions
            # In full implementation, this will use celpy
            # For now, we support basic comparisons and logic

            # Strip whitespace
            expr = expr.strip()

            # Handle boolean literals
            if expr == "true":
                return True
            if expr == "false":
                return False

            # For MVP, we'll need to implement full celpy integration
            # This is a minimal stub to allow testing of the structure
            raise NotImplementedError(
                "Full CEL evaluation requires celpy integration - to be implemented"
            )

        except SyntaxError as e:
            raise CELSyntaxError(f"Invalid CEL syntax: {e}") from e
        except Exception as e:
            raise CELEvaluationError(f"CEL evaluation failed: {e}") from e

    def validate_syntax(self, expr: str) -> bool:
        """
        Check if CEL expression is syntactically valid.

        Args:
            expr: CEL expression string

        Returns:
            True if syntax is valid

        Raises:
            CELSyntaxError: If expression is malformed with details
        """
        # T024: Implement validate_syntax() method
        if not expr or not expr.strip():
            raise CELSyntaxError("Empty expression")

        # Check for unsafe operations in safe mode
        if self.mode == CELMode.SAFE:
            for unsafe_op in CELMode.UNSAFE_OPERATIONS:
                if unsafe_op in expr:
                    raise CELSyntaxError(
                        f"Operation '{unsafe_op}' not allowed in safe mode. "
                        f"Use 'full' or 'extended' mode to enable."
                    )

        # Basic syntax checks
        # Full implementation will use celpy parser
        # For MVP, check balanced parentheses
        if expr.count("(") != expr.count(")"):
            raise CELSyntaxError("Unbalanced parentheses")

        if expr.count("[") != expr.count("]"):
            raise CELSyntaxError("Unbalanced brackets")

        if expr.count("{") != expr.count("}"):
            raise CELSyntaxError("Unbalanced braces")

        return True

    def check_numeric_type(self, expr: str) -> bool:
        """
        Check if expression evaluates to numeric type.

        Args:
            expr: CEL expression

        Returns:
            True if expression is numeric

        Note:
            This is used for validating transition costs and progress conditions.
            Full implementation will use celpy type inference.
        """
        # For MVP: Basic type checking
        # Full implementation will use celpy type system
        self.validate_syntax(expr)

        # Check if expression contains numeric operators
        numeric_indicators = ["+", "-", "*", "/", "%", ".", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        return any(indicator in expr for indicator in numeric_indicators)
