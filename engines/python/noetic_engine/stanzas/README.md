# Noetic Stanzas (`noetic.stanzas`)

## 1. Overview

The `noetic.stanzas` module defines the **Structural Grammar** of a Noetic Flow.

If `noetic.cognition` is the "Mind" that processes thought, `noetic.stanzas` is the "Sheet Music" it plays. This module contains the Pydantic definitions and configuration logic for the hierarchical units of execution: **Flows**, **Stanzas**, and **Steps**.

It is a **Data-Only Module**. It does not contain execution logic, planners, or runtime loops. It strictly defines the schema and validation logic for the Noetic Language entities.

---

## 2. Core Concepts: The Hierarchy

The Noetic architecture organizes complex agentic behavior into three nested layers.

### A. The Flow (The Graph)

The **Flow** is the top-level container (the "App"). It defines the routing logic between different phases of work.

- **Structure:** A Directed Graph where nodes are Stanzas/Agents and edges are transitions.
- **Role:** Orchestrates long-horizon tasks that span multiple domains (e.g., "Build a Startup" Research Stanza Coding Stanza Marketing Stanza).

### B. The Stanza (The Node)

The **Stanza** is the fundamental unit of execution. It represents a "Context Frame" or a "Phase of Work."

- **Role:** Entering a Stanza pushes a new **MemoryFrame** to the `noetic.knowledge` Stack.
- **Dual Modes:**

1. **Agentic Stanza:** Defined by a **Goal**. The Agent uses `noetic.cognition` to figure out the path.
2. **Procedural Stanza:** Defined by **Steps**. The Agent executes a deterministic Standard Operating Procedure (SOP).

### C. The Step (The Instruction)

The **Step** is an atomic instruction within a Procedural Stanza.

- **Role:** Wraps a specific `Skill` call with hard-coded or templated arguments.
- **Scope:** Steps are private to their Stanza.

---

## 3. Data Models (`definitions.py`)

This module exports the Pydantic models used by the rest of the engine to type-check the Codex.

### Stanza Definition

```python
class StanzaDefinition(BaseModel):
    id: str
    mode: Literal["AGENTIC", "PROCEDURAL"]

    # --- Agentic Config ---
    goal: Optional[str]
    system_prompt: Optional[str] # Overrides the Agent's base persona

    # --- Procedural Config ---
    steps: List[StepDefinition]

    # --- Scope Config ---
    allowed_tools: List[str]    # Permissions
    knowledge_mounts: List[str] # Graph access

```

### Flow Definition

```python
class FlowDefinition(BaseModel):
    id: str
    nodes: List[Union[StanzaRef, AgentRef]]
    edges: List[FlowTransition]

```

---

## 4. Sub-Systems

### A. The Stanza Library (`library/`)

Contains built-in, reusable Stanza definitions that solve common meta-problems.

- **`research.py`:** A Stanza configured for Web Search, Summary, and Synthesis.
- **`coding.py`:** A Stanza configured for File I/O, Linting, and Testing.
- **`review.py`:** A Stanza configured for the "Critic" persona (High Evaluation, Low Generation).

### B. The Validator (`validation.py`)

Responsible for ensuring the integrity of a loaded Codex.

- **Checks:**
- Do all `Step` tool references exist in `noetic.skills`?
- Do all `Flow` transitions point to valid Stanza IDs?
- Are there circular dependencies in procedural definitions?

---

## 5. Interaction with Other Modules

This module provides the **Static Configuration** to the dynamic Runtime.

1. **Fed to `noetic.runtime.interpreter`:**

- The Interpreter reads the `StanzaDefinition` to know which Tools to enable and which Prompt to load.

1. **Fed to `noetic.knowledge`:**

- The Stanza's `goal` becomes the label for the **MemoryFrame** pushed to the stack.

1. **Fed to `noetic.stage`:**

- The UI renders the current Stanza as the "Active Phase" in the progress tracker.

---

## 6. Implementation Directives (For AI Assistant)

### Directive 1: Pydantic Everything

All classes in this module must inherit from `pydantic.BaseModel`. This ensures that our internal Python objects match the JSON schema of the Noetic Language exactly.

### Directive 2: No Execution Logic

**Crucial:** Do not put `run()`, `execute()`, or `plan()` methods on these models.

- _Bad:_ `stanza.run(context)`
- _Good:_ `interpreter.run(stanza, context)`

### Directive 3: Reusable Templates

Implement a `StanzaTemplate` mechanism in `definitions.py`. This should allow users to define a Stanza with variables (e.g., `goal: "Research {{topic}}"`) that are hydrated at runtime by the Flow.

---

## 7. Directory Structure

```text
noetic/stanzas
├── __init__.py           # Exports definitions and library
├── definitions.py        # The Pydantic Models (Stanza, Flow, Step)
├── validation.py         # Integrity checks for the Codex
└── library/              # Built-in Stanza Configs
    ├── __init__.py
    ├── research.py
    ├── coding.py
    └── reflection.py

```
