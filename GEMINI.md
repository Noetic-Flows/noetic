# Gemini Context: The Noetic Ecosystem (V3.0)

## 1. Project Overview

The **Noetic Ecosystem** represents a shift from "Apps" (rigid logic) to "Flows" (adaptive intent), termed **Software 3.0**.

The project consists of two main pillars:

1. **Noetic Language (`noetic-lang`)**: A JSON-based protocol defining an Agent's "Codex" (Persona, Knowledge, Skills, Principles, UI).
2. **Noetic Engine (`noetic-python`)**: The reference runtime that executes the Codex.

### Core Modules (V3 Architecture)

- **`noetic.knowledge` (Memory):** The Cognitive Operating System.
  - **Working Memory (Stack):** AgentProg implementation using `MemoryFrames`.
  - **The Store (Heap):** Tri-Store (Semantic, Episodic, Procedural).
  - **Nexus:** Relevance assembly.
  - **Sync:** Shared Semantic Environment (SSE).
- **`noetic.cognition` (Mind):** The algorithmic core. Pure reasoning.
  - **Components:** `Planner` (Actor), `Evaluator` (Critic), `Metacognition`.
- **`noetic.stanzas` (Structure):** Static definitions of execution phases.
  - **Components:** `Flow` (Graph), `Stanza` (Intent Unit), `Step` (Instruction).
- **`noetic.stage` (Interface):** Generative UI, Voice, and Avatar rendering. (Was `canvas`).
- **`noetic.conscience` (Value System):** The Axiological Engine that evaluates actions against Principles.
- **`noetic.runtime` (Kernel):** Execution and Lifecycle.
  - **Components:** `Interpreter` (Stanza execution), `Lifecycle` (Awake/Idle/Sleep).

---

## 2. Development Guidelines

- **Test-Driven Development (TDD):** Write unit tests for logic (e.g., Stack, Planner) before implementation.
- **Asyncio Discipline:**
  - The **Reflex Loop** must never block.
  - The **Cognitive Loop** must be robust.
- **Type Safety:** Use `Pydantic` for all data schemas and `MyPy` compatible type hinting.
- **Dependency Isolation:**
  - `cognition` relies on `stanzas` and `knowledge`.
  - `stage` renders state but contains no logic.
  - All modules communicate via the `KnowledgeStore` (Blackboard Pattern).
- **Code Style:** Follow PEP 8. Use descriptive variable names.

---

## 3. Current Status (Jan 22, 2026)

The project is implementing **Noetic Architecture V3.0**.

- **Refactoring:** Completed directory restructure (Orchestration split, Canvas rename).
- **Knowledge:** Moving to Stack/Heap architecture.
- **Cognition:** Logic moved from Orchestration.
- **Stanzas:** Definitions moved from Orchestration.

---

## 4. Next Steps

### A. Knowledge Module (`noetic.knowledge`)

1. **Working Memory (The Stack):**
    - Implement `MemoryFrame` and `Stack` logic (TDD in progress).
    - Implement garbage collection on frame exit.
2. **The Store (The Heap):**
    - Refine Tri-Store implementation.

### B. Cognition Module (`noetic.cognition`)

1. **Planner:**
    - Update to use `stanzas` definitions.
2. **Evaluator:**
    - Update to use `stanzas` definitions.

### C. Runtime Module (`noetic.runtime`)

1. **Interpreter:**
    - Implement the bridge that executes Stanzas (pushes stack frames, routes flow).
2. **Lifecycle:**
    - Manage AWAKE, IDLE, and SLEEP states.

### D. Stage Module (`noetic.stage`)

1. **Renderer:**
    - Ensure compatibility with new Knowledge structure.