"""CLI interface for noetic-policies (T085-T091)."""

import sys
from pathlib import Path

from noetic_policies.validator import PolicyValidator

__all__ = ["main"]


def main() -> None:
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: noetic-policies <command> [options]")
        print("\nCommands:")
        print("  validate <file>       - Validate a policy file")
        print("  version              - Show version information")
        sys.exit(1)

    command = sys.argv[1]

    if command == "validate":
        handle_validate()
    elif command == "version":
        handle_version()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


def handle_validate() -> None:
    """Handle validate command."""
    if len(sys.argv) < 3:
        print("Usage: noetic-policies validate <file> [--mode fast|thorough]")
        sys.exit(1)

    file_path = sys.argv[2]

    # Parse mode option
    mode = "fast"
    if "--mode" in sys.argv:
        mode_index = sys.argv.index("--mode")
        if mode_index + 1 < len(sys.argv):
            mode = sys.argv[mode_index + 1]

    # Validate policy
    validator = PolicyValidator()
    result = validator.validate_file(file_path, mode=mode)

    # Output results
    if result.is_valid:
        print("✓ Policy validation successful\n")
        print(f"Mode: {mode}")
        print(f"Duration: {result.metadata.get('duration_ms', 0):.2f}ms")
        sys.exit(0)
    else:
        print("✗ Policy validation failed\n")
        for error in result.errors:
            print(error.format())
            print()
        print(f"Mode: {mode}")
        print(f"Errors: {len(result.errors)}")
        sys.exit(1)


def handle_version() -> None:
    """Handle version command."""
    print("Noetic Policies v0.1.0")
    print("Policy Format Version: 1.0")
    sys.exit(0)


if __name__ == "__main__":
    main()
