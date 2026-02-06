# CLI API Contract: Noetic Policies Package

**Feature**: Build the noetic-policies package
**Branch**: 001-noetic-policies
**Date**: 2026-02-05

## Overview

This document defines the CLI interface for the noetic-policies package. Per constitution Principle V (Library-First with CLI Exposure), the CLI exposes library functionality via text I/O (stdin/args → stdout, errors → stderr).

---

## Command: `noetic-policies validate`

**Purpose**: Validate policy files

### Synopsis

```bash
noetic-policies validate [OPTIONS] FILE
```

### Arguments

- `FILE`: Path to policy file (YAML format)

### Options

- `-m, --mode MODE`: Validation mode ("fast" or "thorough", default: "fast")
- `-f, --format FORMAT`: Output format ("human", "json", default: "human")
- `--strict`: Treat warnings as errors
- `--no-color`: Disable colored output
- `--verbose, -v`: Verbose output (show all checks performed)
- `--version`: Show policy format version being validated against

### Exit Codes

- `0`: Validation successful (policy is valid)
- `1`: Validation failed (policy has errors)
- `2`: Parse error (invalid YAML or unsupported version)
- `3`: File not found
- `4`: Invalid arguments

### Output Formats

#### Human-Readable (default)

```bash
$ noetic-policies validate policy.yaml

✓ Policy validation successful

Version: 1.0
States: 3
Constraints: 2
Mode: fast
Duration: 0.12s
```

With errors:

```bash
$ noetic-policies validate invalid_policy.yaml

✗ Policy validation failed (2 errors, 1 warning)

ERROR [E001]: Missing required 'constraints' section
  Line 2: Suggestion: Add constraints: []

ERROR [E004]: Unreachable state 'orphan'
  Line 15: No path from initial state 'start' to 'orphan'
  Suggestion: Add transition to 'orphan' or remove it

WARNING [W001]: Policy using deprecated version 0.9
  Suggestion: Upgrade to version 1.0 using: noetic-policies migrate

Mode: fast
Duration: 0.08s

Exit code: 1
```

#### JSON Format

```bash
$ noetic-policies validate policy.yaml --format json

{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "metadata": {
    "version": "1.0",
    "mode": "fast",
    "duration_ms": 120,
    "checks_performed": ["schema", "constraints", "basic_graph", "scoring", "temporal_bounds"],
    "goals_summary": {
      "count": 1,
      "scored": true,
      "temporally_bounded": true
    }
  }
}
```

With errors:

```json
{
  "is_valid": false,
  "errors": [
    {
      "code": "E001",
      "message": "Missing required 'constraints' section",
      "line_number": 2,
      "severity": "error",
      "fix_suggestion": "Add constraints: []"
    }
  ],
  "warnings": [],
  "metadata": {
    "mode": "fast",
    "duration_ms": 80
  }
}
```

### Examples

**Fast validation** (development):
```bash
noetic-policies validate my_policy.yaml
```

**Thorough validation** (CI/CD):
```bash
noetic-policies validate my_policy.yaml --mode thorough
```

**Strict mode** (treat warnings as errors):
```bash
noetic-policies validate my_policy.yaml --strict
```

**JSON output** (for tooling):
```bash
noetic-policies validate my_policy.yaml --format json | jq '.is_valid'
```

**Verbose output**:
```bash
noetic-policies validate my_policy.yaml --verbose
```

Output:
```
Validating policy...
✓ Schema validation passed
✓ Constraint syntax check passed (2 constraints)
✓ State graph structure validated (3 states, cost range: 0.0–1.0)
✓ Reachability check passed
✓ Goal state reachable (1 goal: max_reached)
✓ Goal scoring validated (priority=1, reward=10.0, 1 progress condition)
✓ Temporal bounds validated (goal: 100 steps/30s, policy: 200 steps/60s)
✓ Temporal feasibility passed (min_steps=2 ≤ max_steps=100)

✓ Policy validation successful
```

---

## Command: `noetic-policies migrate`

**Purpose**: Migrate policy to newer version

### Synopsis

```bash
noetic-policies migrate [OPTIONS] FILE
```

### Arguments

- `FILE`: Path to policy file to migrate

### Options

- `--to-version VERSION`: Target version (default: latest)
- `-o, --output FILE`: Write migrated policy to file (default: stdout)
- `--in-place`: Modify file in place
- `--format FORMAT`: Output format ("yaml", "json", default: "yaml")
- `--dry-run`: Show what would be migrated without applying changes

### Exit Codes

- `0`: Migration successful
- `1`: Migration failed (unsupported version or migration error)
- `2`: Parse error
- `3`: File not found
- `4`: Invalid arguments

### Examples

**Migrate to latest version**:
```bash
noetic-policies migrate old_policy.yaml
```

**Migrate in-place**:
```bash
noetic-policies migrate old_policy.yaml --in-place
```

**Dry run** (see what would change):
```bash
noetic-policies migrate old_policy.yaml --dry-run
```

**Output to file**:
```bash
noetic-policies migrate old_policy.yaml --output new_policy.yaml
```

---

## Command: `noetic-policies stdlib`

**Purpose**: Interact with standard library policies

### Synopsis

```bash
noetic-policies stdlib [COMMAND]
```

### Subcommands

#### `list`

List all standard library policies.

```bash
$ noetic-policies stdlib list

Standard Library Policies:

  token_transfer    - ERC-20 compliant token transfer
  voting            - Simple majority voting
  escrow            - Time-locked escrow

Use 'noetic-policies stdlib show <name>' to view policy details
```

#### `show NAME`

Display a standard library policy.

```bash
$ noetic-policies stdlib show token_transfer

# ERC-20 Token Transfer Policy

Version: 1.0
Description: Production-ready ERC-20 compliant token transfer policy

Constraints:
  - sufficient_balance: sender_balance >= amount
  - positive_amount: amount > 0
  - valid_recipient: recipient != null

States: 3 (idle, transferring, complete)
Goal State: complete

[Full YAML content follows...]
```

#### `copy NAME OUTPUT`

Copy standard library policy to file for customization.

```bash
$ noetic-policies stdlib copy token_transfer my_token.yaml

✓ Copied 'token_transfer' policy to my_token.yaml

You can now customize this policy and validate with:
  noetic-policies validate my_token.yaml
```

#### `validate`

Validate all standard library policies (FR-012: all must pass).

```bash
$ noetic-policies stdlib validate

Validating standard library policies...

✓ token_transfer: PASS (thorough mode, 0.25s)
✓ voting: PASS (thorough mode, 0.18s)
✓ escrow: PASS (thorough mode, 0.22s)

All standard library policies validated successfully.
```

---

## Command: `noetic-policies version`

**Purpose**: Show version information

### Synopsis

```bash
noetic-policies version
```

### Output

```bash
$ noetic-policies version

Noetic Policies v0.1.0

Policy Format Version: 1.0
Supported Versions: 1.0, 0.9 (deprecated)
Python Version: 3.11.5
Dependencies:
  - networkx: 3.6.1
  - pydantic: 2.5.3
  - celpy: 0.20.1
  - opentelemetry-api: 1.22.0
```

---

## Global Options

Available for all commands:

- `--help, -h`: Show help message
- `--version`: Show version information (equivalent to `noetic-policies version`)
- `--config FILE`: Use custom configuration file
- `--no-color`: Disable colored output
- `--quiet, -q`: Suppress non-error output

---

## Environment Variables

### `NOETIC_POLICIES_CONFIG`

Path to configuration file (alternative to `--config`).

**Example**:
```bash
export NOETIC_POLICIES_CONFIG=~/.config/noetic/policies.yaml
noetic-policies validate my_policy.yaml
```

### `NOETIC_NO_COLOR`

Disable colored output (alternative to `--no-color`).

**Example**:
```bash
export NOETIC_NO_COLOR=1
noetic-policies validate my_policy.yaml
```

### `NOETIC_POLICIES_MODE`

Default validation mode ("fast" or "thorough").

**Example**:
```bash
export NOETIC_POLICIES_MODE=thorough
noetic-policies validate my_policy.yaml  # Uses thorough mode
```

---

## Configuration File

Optional YAML configuration file to customize behavior.

**Location**: `~/.config/noetic/policies.yaml` or via `--config` / `NOETIC_POLICIES_CONFIG`

**Format**:
```yaml
# Default validation mode
default_mode: fast

# Strict mode by default
strict: false

# Output format
output_format: human

# Auto-migration settings
auto_migrate: true
migration_target_version: "1.0"

# Observability
tracing:
  enabled: false
  endpoint: "http://localhost:4318"

# Resource limits (soft warnings)
resource_limits:
  max_validation_time_ms: 5000
  max_memory_mb: 500
```

---

## Pipeline Integration Examples

### CI/CD (GitHub Actions)

```yaml
- name: Validate Policy
  run: |
    noetic-policies validate policy.yaml --mode thorough --format json > result.json

- name: Check Result
  run: |
    if [ $(jq '.is_valid' result.json) != "true" ]; then
      echo "Policy validation failed"
      exit 1
    fi
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

for policy in $(git diff --cached --name-only --diff-filter=ACM | grep '\.yaml$'); do
  if ! noetic-policies validate "$policy" --mode fast --quiet; then
    echo "Policy validation failed: $policy"
    exit 1
  fi
done
```

### Makefile

```makefile
.PHONY: validate-policies
validate-policies:
	find policies/ -name '*.yaml' -exec noetic-policies validate {} --mode thorough \;
```

---

## Error Message Format

All error messages follow a consistent format for SC-003 (90% fixable without docs):

```
<SEVERITY> [<CODE>]: <MESSAGE>
  Line <N>[, Column <M>]: <CONTEXT>
  Suggestion: <FIX_SUGGESTION>
  [See: <DOCUMENTATION_URL>]
```

**Example**:
```
ERROR [E004]: Unreachable state 'orphan'
  Line 15: No path from initial state 'start' to 'orphan'
  Suggestion: Add transition to 'orphan' or remove it
  See: https://docs.noetic.ai/errors#E004
```

---

## Text I/O Protocol

Per constitution Principle V:

- **Input**: CLI arguments, file paths, or stdin
- **Output**: Human-readable or JSON to stdout
- **Errors**: Error messages to stderr
- **Exit codes**: Indicate success/failure for scripting

**Example with stdin**:
```bash
cat policy.yaml | noetic-policies validate -

✓ Policy validation successful
```

**Example with stdout redirection**:
```bash
noetic-policies validate policy.yaml --format json > result.json
```

**Example with stderr**:
```bash
noetic-policies validate invalid.yaml 2> errors.log
```

---

## Observability via CLI

When tracing is enabled in config:

```yaml
tracing:
  enabled: true
  endpoint: "http://localhost:4318"
```

All CLI commands automatically create OpenTelemetry spans and export to configured endpoint.

**View traces**:
```bash
# Spans created:
# - cli.validate
#   - policy.parse
#   - policy.validate
#     - policy.validate.schema
#     - policy.validate.constraints
#     - policy.validate.scoring
#     - policy.validate.temporal_bounds
#     - policy.validate.state_graph
```

---

## Shell Completion

Install shell completion for better UX:

**Bash**:
```bash
noetic-policies --install-completion bash
```

**Zsh**:
```bash
noetic-policies --install-completion zsh
```

**Fish**:
```bash
noetic-policies --install-completion fish
```

---

## Notes

- All commands follow Unix philosophy (text in/out, composable, single responsibility)
- JSON output for machine readability / tooling integration
- Human-readable output for developer experience
- Exit codes for script integration
- Colored output (disable with `--no-color` or `NOETIC_NO_COLOR=1`)
- Error messages designed for SC-003 (90% fixable without docs)
