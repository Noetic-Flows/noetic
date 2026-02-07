"""Structured logging configuration."""

import logging
import sys
from typing import Any


# T020: Logger module
def get_logger(name: str = "noetic_policies") -> logging.Logger:
    """
    Get or create a structured logger for the noetic-policies package.

    Args:
        name: Logger name (default: "noetic_policies")

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger


def log_validation_operation(
    logger: logging.Logger,
    operation: str,
    policy_name: str | None = None,
    **kwargs: Any,
) -> None:
    """
    Log a validation operation with structured context.

    Args:
        logger: Logger instance
        operation: Operation name (e.g., "schema_validation", "graph_analysis")
        policy_name: Policy name if available
        **kwargs: Additional structured context
    """
    context = {"operation": operation}
    if policy_name:
        context["policy_name"] = policy_name
    context.update(kwargs)

    # Log as structured message
    logger.info(
        f"Validation operation: {operation}",
        extra={"structured": context},
    )
