"""Policy parser for YAML files (T109-T113)."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError as PydanticValidationError

from noetic_policies.models.policy import Policy

__all__ = ["PolicyParser", "PolicyParseError"]


class PolicyParseError(Exception):
    """Raised when policy parsing fails."""

    pass


class PolicyParser:
    """
    Parse policy files (YAML format) into structured Pydantic models.

    Implements FR-001 (parse policy files).
    """

    def __init__(self):
        """Initialize policy parser."""
        pass

    def parse_yaml(self, content: str) -> Policy:
        """
        Parse YAML string into Policy object.

        Args:
            content: YAML policy specification

        Returns:
            Parsed and validated Policy object

        Raises:
            PolicyParseError: If YAML is malformed or validation fails
        """
        try:
            # Parse YAML
            data = yaml.safe_load(content)

            if not isinstance(data, dict):
                raise PolicyParseError("Policy must be a YAML dictionary")

            # Parse into Policy model
            return self.parse_dict(data)

        except yaml.YAMLError as e:
            raise PolicyParseError(f"YAML syntax error: {e}") from e

    def parse_file(self, file_path: Path | str) -> Policy:
        """
        Parse policy file from filesystem.

        Args:
            file_path: Path to YAML policy file

        Returns:
            Parsed and validated Policy object

        Raises:
            FileNotFoundError: If file doesn't exist
            PolicyParseError: If parsing fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Policy file not found: {file_path}")

        try:
            content = file_path.read_text()
            return self.parse_yaml(content)
        except Exception as e:
            if isinstance(e, (PolicyParseError, FileNotFoundError)):
                raise
            raise PolicyParseError(f"Failed to parse {file_path}: {e}") from e

    def parse_dict(self, data: dict[str, Any]) -> Policy:
        """
        Parse policy from dictionary (already loaded YAML/JSON).

        Args:
            data: Policy data as dictionary

        Returns:
            Parsed and validated Policy object

        Raises:
            PolicyParseError: If validation fails
        """
        try:
            return Policy(**data)
        except PydanticValidationError as e:
            # Convert Pydantic errors to friendly messages
            error_messages = []
            for error in e.errors():
                loc = " -> ".join(str(x) for x in error["loc"])
                msg = error["msg"]
                error_messages.append(f"{loc}: {msg}")

            raise PolicyParseError(
                f"Policy validation failed:\n" + "\n".join(error_messages)
            ) from e
        except Exception as e:
            raise PolicyParseError(f"Failed to parse policy: {e}") from e
