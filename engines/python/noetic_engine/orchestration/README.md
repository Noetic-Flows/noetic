# Noetic Orchestration (`noetic.orchestration`)

## 1. Overview

The `noetic.orchestration` module is the **Decision Layer** of the Noetic Engine.

While `noetic.runtime` manages the physics of the simulation (the tick loop, thread management, and event polling), `noetic.orchestration` provides the **Intelligence**. It allows the system to look at the _World State_ and decide _What to do next_.

This module implements a **Hybrid Cognitive Architecture** that fuses two disparate approaches to AI control:

1. **Deterministic Orchestration:** Explicit **Flows** (State Machines) for rigid procedures (e.g., "User Onboarding").
2. **Probabilistic Planning:** Dynamic **GOAP** (Goal-Oriented Action Planning) for fluid problem solving.

It is governed by **Principles** (Policy-as-Data), ensuring that all decisions—whether scripted or planned—adhere to the Agent's values.

---

## 2. Architecture: The "Score"

In the Noetic ecosystem, we treat the logic definition as a musical **Score**. The `orchestration` module is the Conductor that reads the Score (from the Codex) and directs the Musicians (Agents).

### The Input/Output Contract

- **Input:** `WorldState` (Snapshot from Knowledge) + `Trigger` (Event).
- **Process:** Evaluate Constraints Select Goal Generate Plan.
- **Output:** `Plan` (A sequence of `Skill` executions).

---

## 3. Core Sub-Systems

### A. The Agent Manager (`agents.py`)

Responsible for hydrating the `Agent` entities defined in the Codex. An Agent is not just a prompt; it is a **Binding Context**.

- **Persona:** The System Prompt (Role, Backstory).
- **Capabilities:** The allowlist of **Skills** this agent can access.
- **Constraints:** The list of **Principles** this agent must obey.

```python
class AgentContext:
    id: str
    system_prompt: str
    allowed_skills: List[str] # e.g. ["skill.email.send", "skill.knowledge.recall"]
    principles: List[Principle]

```

### B. The Principle Engine (`principles.py`)

_Formerly "Blueprints"._
This is the **Conscience** of the system. It uses **JsonLogic** to evaluate the "Moral Cost" of an action dynamically.

- **Function:** `evaluate_cost(action: Action, context: State) -> float`
- **Logic:**
- If `Action` uses `skill.delete_db` AND `Agent` values `safety`: Cost += 1000.0.
- If `Action` uses `skill.cache` AND `Agent` values `speed`: Cost -= 50.0.

### C. The Flow Engine (`flows.py`)

Responsible for executing explicit **Intent Flows** defined in the Codex.

- **Backend:** Wraps **LangGraph**.
- **Role:** Translates the JSON State Machine definition into a compiled Graph.
- **Behavior:** It steps through nodes (`Interaction`, `Choice`, `Action`) deterministically until it hits a `PlannerNode` or an `End` state.

### D. The Planner (`planner.py`)

The implementation of **Goal-Oriented Action Planning (GOAP)**.

- **Role:** When there is no explicit Flow, or when a Flow requests dynamic problem solving, the Planner takes over.
- **Algorithm:**

1. **Goal Selection:** What is the desired state? (e.g., `entity.plant.health > 80`).
2. **Skill Discovery:** Which available Skills affect `entity.plant.health`? (e.g., `skill.water_plant`).
3. **Pathfinding (A\*):** Find the sequence of Skills that leads from _Current State_ to _Goal State_.
4. **Weighting:** Apply the **Principle Engine** to every edge in the graph. Choose the path with the lowest _Principle Cost_ (not just the shortest path).

---

## 4. Interaction with Other Modules

The Orchestration layer sits in the middle of the stack.

1. **Reads from `noetic.knowledge`:**

- It queries the Graph to understand the current context.
- _Constraint:_ It must treat Knowledge as "ReadOnly" during the planning phase. Writes only happen during execution.

1. **Invokes `noetic.skills`:**

- The Planner does not execute code. It selects a **Skill ID**.
- The `noetic.runtime` is responsible for actually calling `skill.execute()`.

1. **Driven by `noetic.runtime`:**

- This module is **passive**. It does not run its own loop.
- It is invoked by the `CognitiveLoop` in the Runtime: `plan = orchestration.plan(state)`.

---

## 5. Implementation Directives (For AI Assistant)

### Directive 1: Principle Implementation

Implement `principles.py` using the `json-logic-qubit` or standard `json-logic` library.

- **Input:** A dictionary context containing `{ "action": {...}, "state": {...}, "tags": [...] }`.
- **Output:** A generic scalar (Float).
- **Requirement:** Ensure strict error handling. If a Principle's logic is malformed, it should default to `0.0` cost (neutral) and log a warning, rather than crashing the decision loop.

### Directive 2: The Agent "Hydrator"

In `loader.py`, when parsing `orchestration.agents`:

- **Validation:** Check that every `adheres_to` ID corresponds to a valid Principle.
- **Validation:** Check that every `skills` ID corresponds to a valid Skill defined in `noetic.skills`.
- **Failure:** Raise a `CodexIntegrityError` if an Agent references a missing Skill.

### Directive 3: LangGraph Abstraction

Do not expose LangGraph types directly to the rest of the engine.

- Create a `FlowExecutor` class that wraps the compiled graph.
- The Runtime should only call `executor.step(inputs)`.
- **State Injection:** Ensure that the LangGraph state is purely a pointer (Snapshot ID) to `noetic.knowledge`. Do not duplicate the World State inside the Graph State.

### Directive 4: Planner Interface

Implement the Planner as a standalone service.

```python
class Planner:
    async def generate_plan(self, agent: Agent, goal: Goal, state: WorldState) -> Plan:
        # 1. Identify relevant skills
        # 2. Run A* search
        # 3. Apply Principle costs
        # 4. Return list of Steps

```

---

## 6. Directory Structure

```text
/noetic/orchestration
├── __init__.py         # Exports AgentManager, Planner, FlowEngine
├── agents.py           # Agent definition and context management
├── principles.py       # JsonLogic evaluator for Values
├── planner.py          # GOAP / A* logic
├── flows.py            # LangGraph wrapper for State Machines
├── prompts.py          # Jinja2 templates for System Prompts
└── utils/
    └── cost.py         # Helpers for calculating weighted costs

```

This structure ensures that the "Intelligence" of the system is modular, grounded in data (The Codex), and strictly separated from the low-level execution loop (The Runtime).
