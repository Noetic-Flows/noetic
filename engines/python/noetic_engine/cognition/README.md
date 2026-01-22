# Noetic Cognition (`noetic.cognition`)

## 1. Overview

The `noetic.cognition` module is the **Algorithmic Core** (The Mind) of the Noetic Engine.

While `noetic.knowledge` remembers the past and `noetic.stanzas` defines the goal, **Cognition** is the active process of reasoning. It is responsible for taking a Goal and a Context, and synthesizing a valid path forward.

This module abandons the naive "Chain of Thought" single-pass approach in favor of a robust **Actor-Critic Architecture**. It separates _generation_ (Planning) from _verification_ (Evaluation), and introduces **Metacognition** to detect when the agent needs to stop and learn before acting.

---

## 2. Architecture: The "Reasoning Engine"

Cognition is not a single function; it is a pipeline of competing neural processes.

### A. The Planner (The Actor)

- **Role:** Optimistic Problem Solver.
- **Input:** Current `Stanza` (Goal) + `Knowledge.nexus` (Context).
- **Process:** Uses the Stanza's System Prompt to generate a sequence of actions.
- **Philosophy:** "How can I solve this?"

### B. The Evaluator (The Critic)

- **Role:** Pessimistic Risk Auditor.
- **Input:** The proposed `Plan`.
- **Process:** An adversarial pass that looks for hallucinations, logic gaps, and dangerous assumptions.
- **Output:** A calibrated **Confidence Score** (0.0 - 1.0).
- **Philosophy:** "Why might this fail?"

### C. The Epistemic Trigger (Metacognition)

- **Role:** The Curiosity Circuit.
- **Process:** Runs _before_ the Planner. It scans the Context for missing variables required by the Goal.
- **Action:** If a gap is found (e.g., "I need the API key but don't see it"), it triggers an **Epistemic Interrupt**, forcing the Runtime to switch to a `ResearchStanza`.
- **Philosophy:** "Do I know enough to proceed?"

---

## 3. Core Components

### `planner.py` (The Actor)

This component generates the `Plan` object. It handles the translation of the abstract Stanza Goal into concrete Steps.

- **Dynamic Routing:** If the Stanza is _Agentic_, the Planner uses an LLM to invent the steps.
- **Deterministic Routing:** If the Stanza is _Procedural_, the Planner simply hydrates the pre-defined Steps from the definition.

### `evaluator.py` (The Critic)

Implements the **Confidence Calibration** logic.

- **Risk Gating:** It interacts with `noetic.conscience` to determine the "Stakes." High-stakes plans trigger a deeper, more expensive critique.
- **Feedback Loop:** If the Confidence Score is below the threshold, the Evaluator rejects the plan and feeds the specific critique back to the Planner for a retry.

### `metacognition.py` (The Curiosity)

Implements the **Ad-Hoc Knowledge Acquisition** logic.

- **Pre-Flight Check:** Analyzes the prompt for specific nouns/entities and verifies their existence in the `Knowledge` graph.
- **Interrupt Signal:** Emits a `Signal.REQUIRE_KNOWLEDGE` event if dependencies are missing, pausing the current execution frame.

### `reflex.py` (The Spinal Cord)

A fast-path logic engine for immediate I/O processing that requires no LLM reasoning.

- **Role:** Handles "Hot" inputs like "Stop!", "Pause", or UI button clicks that route directly to pre-defined handlers.
- **Latency:** < 10ms.

---

## 4. Interaction Flow

The `noetic.runtime.interpreter` calls Cognition during the **Cognitive Loop**:

1. **Metacognition Check:**

- `metacognition.assess(stanza, context)`
- _Result:_ Proceed or Interrupt (to Research).

1. **Generate (Actor):**

- `plan = planner.generate(stanza, context)`

1. **Evaluate (Critic):**

- `risk = conscience.calculate_risk(plan)`
- `if risk > THRESHOLD: confidence = evaluator.score(plan)`

1. **Output:**

- Returns the vetted `Plan` to the Runtime for execution.

---

## 5. Implementation Directives (For AI Assistant)

### Directive 1: Separation of Concerns

This module **does not contain definitions**.

- **Do not** define `Agent` or `Flow` classes here. (See `noetic.stanzas`).
- **Do not** define `Fact` or `Graph` classes here. (See `noetic.knowledge`).
- **Do not** define `Principle` logic here. (See `noetic.conscience`).

This module is strictly for the **Functions** that process those objects.

### Directive 2: Confidence Propagation

Ensure that the `Evaluator` outputs a structured object containing both the `score` (float) and the `rationale` (string). This rationale must be available to the UI (`noetic.stage`) to display "Why I am hesitant" to the user.

### Directive 3: The Interrupt Protocol

The `Metacognition` module must not "fix" the problem itself. It must raise a specific Exception or Signal (`EpistemicInterrupt`) that the Runtime catches. The Runtime is responsible for pushing the new `ResearchStanza` to the stack.

---

## 6. Directory Structure

```text
noetic/cognition
├── __init__.py         # Exports Planner, Evaluator, Metacognition
├── planner.py          # The Actor: Generates Plans
├── evaluator.py        # The Critic: Scores Plans (Confidence)
├── metacognition.py    # The Trigger: Epistemic Interrupts
└── reflex.py           # The Spinal Cord: Fast-path logic

```
