# Noetic Conscience (Python Library)

**Layer 4c: The Safety Library**

The `noetic.conscience` module is the **Axiological Engine** (Value System) of the Noetic runtime.

In "Software 2.0" (Standard Code), safety is enforced by hard-coded `if/else` statements scattered throughout the codebase. In **Software 3.0** (Noetic), safety and alignment are architectural concerns separated from the business logic.

**The Conscience has one job:** To evaluate a proposed **Action** against the Agent's **Principles** and return a **Cost**.

- **The Orchestrator** asks: _"How do I achieve Goal X?"_ (It finds the path of least resistance).
- **The Conscience** asks: _"What is the moral/value cost of that path?"_ (It adds friction to undesirable actions).

If the Conscience determines the cost is too high (exceeding a defined `risk_threshold`), the Action is **intercepted**.
*   It may be **Vetoed** (Hard Stop).
*   It may trigger a **Shadow Action Card** (Human-in-the-Loop Approval).

---

## 1. Core Philosophy: Dynamic Alignment

The Noetic Engine does not believe in "Three Laws of Robotics" hard-coded in English. We believe in **Weighted Mathematical Alignment**.

### The Equation

This allows for nuance.

- **Scenario:** An agent wants to restart a production server to fix a bug.
- **Principle A (Uptime):** "Do not restart prod." (Cost: 500)
- **Principle B (Security):** "Fix critical CVEs immediately." (Cost: 1000)
- **Result:** The Security principle outweighs the Uptime principle. The Agent chooses to restart the server, accepting the cost because the alternative (hack) is worse.

---

## 2. Data Model

The Conscience operates on three primitives defined in the `orchestration` section of the Codex.

### A. Values (The Abstract)

Simple identifiers representing what the Agent cares about.

- `val.privacy`
- `val.frugality`
- `val.safety`

### B. Principles (The Logic)

The executable rules that map context to cost. We use **JsonLogic** to ensure these are safe, portable, and non-Turing-complete.

```json
{
  "id": "principle.frugal_compute",
  "affects": "val.frugality",
  "logic": {
    "if": [
      { ">": [{ "var": "action.estimated_cost_usd" }, 0.5] },
      100.0, // High penalty for expensive actions
      0.0 // No penalty for cheap actions
    ]
  }
}
```

### C. The Context (The Input)

When the Planner proposes a step, it sends a `JudgementContext` to the Conscience:

```python
class JudgementContext(BaseModel):
    agent_id: str
    action_id: str          # e.g., "skill.aws.restart_instance"
    action_args: Dict       # e.g., { "instance_id": "i-123" }
    tags: List[str]         # e.g., ["tag.destructive", "tag.remote"]
    world_state: Dict       # Snapshot of relevant memory
```

---

## 3. Core Components

### `Evaluator` (`evaluator.py`)

The main engine class.

1. **Load:** It pulls the `adheres_to` list of Principles for the current Agent.
2. **Filter:** It discards Principles that don't apply to the current Action tags.
3. **Execute:** It runs the `JsonLogic` engine for every active Principle.
4. **Aggregate:** It sums the results into a `JudgementResult`.

### `AuditLogger` (`audit.py`)

This is critical for Enterprise Trust.

- It does not just return the score; it records the **"Why."**
- It emits an OpenTelemetry event for every Principle that triggered a non-zero cost.

### `VetoSwitch` (`veto.py`)

A safety mechanism.

- If a Principle returns a cost of `INFINITY` (or a specific "Hard Block" signal), the VetoSwitch throws a `PolicyViolationError`.
- This immediately terminates the Planning branch, forcing the Agent to find a different way.

---

## 4. Implementation Details

### JsonLogic Integration

We use the `json-logic-qubit` library (or a robust equivalent).

- **Safety:** Wrap the evaluation in a `try/except` block. If a user writes bad logic in their Codex, the Conscience logs a warning and returns `0.0` (Fail Open) or `MAX_INT` (Fail Closed), depending on the `manifest.safety_mode` setting. **Default to Fail Closed for safety.**

### Caching

Principle evaluation happens inside the "Hot Loop" of the Planner (A\* search).

- **Performance:** A complex plan might evaluate constraints 1,000 times per second.
- **Requirement:** `functools.lru_cache` is implemented for the JsonLogic evaluation. If the `context` hash hasn't changed, the previous cost is returned instantly.

### Tag Inheritance

The Evaluator respects the **Ontology**.

- If an action has tag `tag.database.write`, and the Ontology says `tag.database.write` IS-A `tag.destructive`, then Principles targeting `tag.destructive` **must** trigger.
- The Tag hierarchy from `noetic.knowledge` is traversed during evaluation.

## 5. Usage

```python
from noetic_conscience import Evaluator, JudgementContext

evaluator = Evaluator()
result = evaluator.judge(
    context=JudgementContext(action_id="delete_db", ...),
    principles=[principle_safety_first]
)

if result.cost > 1000:
    raise VetoError("Action too dangerous")
```

## 6. Directory Structure

```text
noetic_conscience/
├── __init__.py         # Exports Evaluator, JudgementContext
├── evaluator.py        # The core logic engine
├── logic.py            # JsonLogic wrapper and custom operators
├── veto.py             # Logic for hard-stops
├── audit.py            # Telemetry/Explanation generation
└── tests/
    └── test_logic.py   # Unit tests for rule variations
```