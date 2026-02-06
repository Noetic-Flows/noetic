# Quickstart: Noetic Policies Package

**Feature**: Build the noetic-policies package
**Branch**: 001-noetic-policies
**Date**: 2026-02-05

## Goal

This quickstart demonstrates the noetic-policies package end-to-end in under 30 minutes (SC-009: documentation allows new developer to write first valid policy in under 30 minutes).

---

## Installation

```bash
# Install via pip
pip install noetic-policies

# Or install from source
cd packages/policies
poetry install
```

**Verify installation**:
```bash
noetic-policies version
```

Expected output:
```
Noetic Policies v0.1.0
Policy Format Version: 1.0
```

---

## Step 1: Explore Standard Library (5 minutes)

List available standard library policies:

```bash
noetic-policies stdlib list
```

Output:
```
Standard Library Policies:

  token_transfer    - ERC-20 compliant token transfer
  voting            - Simple majority voting
  escrow            - Time-locked escrow
```

View the token transfer policy:

```bash
noetic-policies stdlib show token_transfer
```

This displays a complete, production-ready ERC-20 policy with:
- Constraints (sufficient balance, positive amount, valid recipient)
- State graph (idle → transferring → complete)
- Invariants (total supply conservation)

**Key Insight**: Standard library policies demonstrate best practices and serve as templates.

---

## Step 2: Create Your First Policy (10 minutes)

Create a simple policy for a counter that increments up to a limit.

**File**: `counter_policy.yaml`

```yaml
version: "1.0"
name: counter
description: Simple counter with max limit

state_schema:
  count: number
  max_limit: number

constraints:
  - name: below_limit
    expr: "count < max_limit"
    description: Counter must be below maximum

  - name: non_negative
    expr: "count >= 0"
    description: Counter cannot go negative

state_graph:
  initial: ready
  states:
    - name: ready
      description: Ready to increment
      preconditions:
        - non_negative
      transitions:
        - to: incrementing
          preconditions:
            - below_limit
          description: Start incrementing
        - to: max_reached
          description: Counter at maximum

    - name: incrementing
      description: Incrementing counter
      transitions:
        - to: ready
          effects:
            - "count = count + 1"
          description: Increment complete

    - name: max_reached
      description: Maximum value reached

invariants:
  - name: count_in_range
    expr: "count >= 0 && count <= max_limit"
    description: Count always within valid range

goal_states:
  - name: max_reached
    conditions:
      - "count == max_limit"
    description: Counter has reached its maximum value
```

**What this demonstrates**:
- **Version**: Policy format version
- **State Schema**: Defines runtime state variables and their types
- **Constraints**: CEL expressions for validation
- **State Graph**: Transitions between states with preconditions
- **Invariants**: Global rules that must always hold
- **Goal States**: Success states with target conditions (enables goal-directed execution)

---

## Step 3: Validate Your Policy (5 minutes)

**Fast validation** (for quick feedback during development):

```bash
noetic-policies validate counter_policy.yaml
```

Expected output:
```
✓ Policy validation successful

Version: 1.0
States: 3
Constraints: 2
Mode: fast
Duration: 0.08s
```

**Thorough validation** (for comprehensive checks):

```bash
noetic-policies validate counter_policy.yaml --mode thorough
```

Expected output:
```
✓ Policy validation successful

Version: 1.0
States: 3
Constraints: 2
Unreachable States: 0
Deadlocks: 0
Goal Reachable: Yes
Mode: thorough
Duration: 0.15s
```

**Verbose output** (see all checks performed):

```bash
noetic-policies validate counter_policy.yaml --mode thorough --verbose
```

---

## Step 4: Programmatic Usage (5 minutes)

Use the policy in Python code:

```python
from noetic_policies.parser import PolicyParser
from noetic_policies.validator import PolicyValidator

# Parse policy file
parser = PolicyParser()
policy = parser.parse_file("counter_policy.yaml")

# Validate policy
validator = PolicyValidator()
result = validator.validate(policy, mode="thorough")

# Check validation result
if result.is_valid:
    print(f"✓ Policy '{policy.name}' is valid!")
    print(f"  States: {len(policy.state_graph.states)}")
    print(f"  Constraints: {len(policy.constraints)}")
else:
    print(f"✗ Policy validation failed:")
    for error in result.errors:
        print(f"  {error.format()}")
```

Expected output:
```
✓ Policy 'counter' is valid!
  States: 3
  Constraints: 2
```

---

## Step 5: Handle Validation Errors (5 minutes)

Create an intentionally invalid policy to see error reporting:

**File**: `invalid_policy.yaml`

```yaml
version: "1.0"
# Missing constraints section (ERROR)

state_graph:
  initial: nonexistent_state  # ERROR: state doesn't exist
  states:
    - name: start
      transitions:
        - to: orphan  # ERROR: orphan is unreachable

    - name: orphan
      # No transitions - deadlock
```

Validate:

```bash
noetic-policies validate invalid_policy.yaml --mode thorough
```

Expected output (demonstrates SC-003: error messages are actionable):

```
✗ Policy validation failed (3 errors)

ERROR [E001]: Missing required 'constraints' section
  Line 2: Policy must define at least one constraint
  Suggestion: Add constraints: []

ERROR [E002]: Initial state 'nonexistent_state' not found
  Line 5: State not defined in states list
  Suggestion: Change initial to 'start' or define 'nonexistent_state'

ERROR [E004]: Unreachable state 'orphan'
  Line 11: No path from initial state to 'orphan'
  Suggestion: Add transition to 'orphan' or remove it

Mode: thorough
Duration: 0.12s
```

**Fix the errors** based on suggestions:

```yaml
version: "1.0"

constraints:
  - name: always_true
    expr: "true"

state_graph:
  initial: start  # Fixed: use existing state
  states:
    - name: start
      transitions:
        - to: orphan  # Added transition to make 'orphan' reachable

    - name: orphan
      transitions:
        - to: end  # Added exit to prevent deadlock

    - name: end
```

Validate again:

```bash
noetic-policies validate invalid_policy.yaml
```

Now it passes:
```
✓ Policy validation successful
```

---

## Common Patterns

### Pattern 1: Using Standard Library as Template

```bash
# Copy standard library policy
noetic-policies stdlib copy token_transfer my_token.yaml

# Customize my_token.yaml for your needs
# ...

# Validate customized policy
noetic-policies validate my_token.yaml --mode thorough
```

### Pattern 2: CI/CD Integration

```yaml
# .github/workflows/validate-policies.yml
name: Validate Policies

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install noetic-policies
        run: pip install noetic-policies

      - name: Validate all policies
        run: |
          for policy in policies/*.yaml; do
            noetic-policies validate "$policy" --mode thorough --format json
          done
```

### Pattern 3: Pre-commit Hook

```bash
# Install pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
for policy in $(git diff --cached --name-only | grep '\.yaml$'); do
  noetic-policies validate "$policy" --mode fast --quiet || exit 1
done
EOF

chmod +x .git/hooks/pre-commit
```

---

## Troubleshooting

### "Policy validation too slow in fast mode"

Fast mode should complete in <1 second. If not:
- Check policy size (thousands of states may trigger soft limit warning)
- Run with `--verbose` to see which check is slow
- Consider simplifying state graph

### "Unreachable state detected"

This means a state cannot be reached from the initial state:
1. Check state graph transitions
2. Ensure every state (except initial) has an incoming transition
3. Use `--verbose` to see reachability analysis

### "Deadlock detected"

This means states form a cycle with no exit:
1. Identify the cycle from error message
2. Add a transition out of the cycle
3. Ensure all non-goal states have paths to goal states

### "CEL expression syntax error"

Common CEL syntax issues:
- Use `&&` and `||` (not `and`/`or`)
- Use `==` for equality (not `=`)
- Strings need double quotes: `"hello"`
- Check variable names match context

---

## Next Steps

1. **Read Policy Specification**: See `docs/policy-specification.md` for complete format reference
2. **CEL Guide**: Learn CEL expression syntax in `docs/cel-guide.md`
3. **Explore Standard Library**: Study production-ready policies:
   ```bash
   noetic-policies stdlib show token_transfer
   noetic-policies stdlib show voting
   noetic-policies stdlib show escrow
   ```
4. **Advanced Validation**: Learn about dual modes (fast vs thorough) and resource limits
5. **Integration**: Use policies with noetic-kernel (agent execution) or noetic-compiler (Solidity generation)

---

## Summary

In this quickstart, you:

✅ Installed noetic-policies package
✅ Explored standard library policies
✅ Created your first policy (counter example)
✅ Validated policies using CLI (fast and thorough modes)
✅ Used the Python API programmatically
✅ Fixed validation errors using actionable error messages
✅ Learned common patterns (CI/CD, pre-commit hooks)

**Time**: ~25 minutes (under 30-minute requirement for SC-009)

**Next**: Build a production-ready policy for your use case!

---

## Quick Reference

| Task | Command |
|------|---------|
| Validate policy (fast) | `noetic-policies validate policy.yaml` |
| Validate policy (thorough) | `noetic-policies validate policy.yaml --mode thorough` |
| List standard library | `noetic-policies stdlib list` |
| View stdlib policy | `noetic-policies stdlib show token_transfer` |
| Copy stdlib policy | `noetic-policies stdlib copy voting my_voting.yaml` |
| JSON output | `noetic-policies validate policy.yaml --format json` |
| Migrate old policy | `noetic-policies migrate old_policy.yaml --in-place` |
| Show version | `noetic-policies version` |

---

## Support

- **Documentation**: https://docs.noetic.ai/policies
- **Issues**: https://github.com/noetic/noetic-policies/issues
- **Examples**: See `examples/` directory in repository
