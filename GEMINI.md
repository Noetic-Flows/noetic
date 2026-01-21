# Gemini Context: The Noetic Ecosystem

## 1. Project Overview

The **Noetic Ecosystem** represents a shift from "Apps" (rigid logic) to "Flows" (adaptive intent), termed **Software 3.0**.

The project consists of two main pillars:

1. **Noetic Language (`noetic-lang`)**: A JSON-based protocol defining an Agent's "Codex" (Persona, Knowledge, Skills, Principles, UI).
2. **Noetic Engine (`noetic-python`)**: The reference runtime that executes the Codex. It operates on a **Dual-Loop Architecture** (Reflex vs. Cognitive) to ensure fluid UI performance alongside complex reasoning.

### Core Modules

- **`noetic.knowledge` (Memory):** A Temporal Knowledge Graph combining SQL (structure/time) and ChromaDB (semantics).
- **`noetic.orchestration` (Brain):** The decision layer fusing deterministic Flows (LangGraph) and probabilistic Planning (GOAP/A\*).
- **`noetic.runtime` (Body):** The execution kernel managing the 60Hz Reflex Loop and the async Cognitive Loop.
- **`noetic.canvas` (Face):** A Server-Driven UI system using the A2UI standard and JSON Pointer data binding.

---

## 2. Development Guidelines

- **Test-Driven Development (TDD):** Write unit tests for logic (e.g., Planner, JSON Pointer resolution) before implementation.
- **Asyncio Discipline:**
  - The **Reflex Loop** must never block. Use `asyncio.create_task` for cognitive operations.
  - The **Cognitive Loop** must be robust. Failures in reasoning should log errors, not crash the engine.
- **Type Safety:** Use `Pydantic` for all data schemas and `MyPy` compatible type hinting.
- **Dependency Isolation:**
  - `orchestration` must not import `runtime`.
  - `canvas` must not import `orchestration`.
  - All modules communicate via the `KnowledgeStore` (Blackboard Pattern).
- **Code Style:** Follow PEP 8. Use descriptive variable names.

---

## 3. Current Status (Jan 20, 2026)

The project is currently in the **Scaffolding Phase**.

- **Architecture:** Fully defined in READMEs.
- **Knowledge:** Basic SQL store exists (`store.py`), but the Semantic (Vector) layer is missing.
- **Orchestration:** `CognitiveSystem` bridge exists, but the `Planner` is a stub returning static actions.
- **Runtime:** The async skeleton is in place, but the main "Tick" loop (Reflex) is not implemented.
- **Canvas:** Basic structure exists, but the JSON Pointer data binding logic is unimplemented.

---

## 4. Next Steps

Development should focus on filling the implementation gaps defined in the module READMEs.

### A. Knowledge Module (`noetic.knowledge`)

1. **Vector Store Integration:**
    - Implement `ChromaDB` integration in `store.py`.
    - Update `ingest_fact` to generate embeddings and upsert to Chroma.
2. **Hybrid Search:**
    - Implement `hybrid_search(query)`: Query Chroma for candidates -> Hydrate via SQL -> Filter by `valid_until IS NULL`.
3. **Graph Cache:**
    - Integrate `NetworkX` to load active facts on startup for pathfinding.

### B. Orchestration Module (`noetic.orchestration`)

1. **GOAP Planner:**
    - Replace the `planner.py` stub.
    - Implement **Skill Discovery** (match skills to state changes).
    - Implement **A\* Pathfinding** to generate a sequence of skills from Current State to Goal State.
2. **Principle Engine:**
    - Implement `principles.py` using `json-logic`.
    - Ensure it calculates "Moral Cost" for edges during planning.
3. **Flow Engine:**
    - Implement `flows.py` wrapping `LangGraph` for deterministic state machines.

### C. Runtime Module (`noetic.runtime`)

1. **Reflex Loop (System 1):**
    - Implement `reflex.py` and the main `run_loop` in `engine.py`.
    - Ensure it runs at 60Hz (using monotonic clock).
    - It must poll inputs and update the UI (Optimistic UI) independent of the Cognitive Loop.
2. **Task Management:**
    - Ensure `CognitiveSystem` tasks are tracked.
    - Implement graceful cancellation of pending tasks on engine stop.

### D. Canvas Module (`noetic.canvas`)

1. **Data Binding:**
    - Implement `jsonpointer` logic in `renderer.py`.
    - Resolve bindings (e.g., `"/entities/plant-1/species"`) against the `WorldState` snapshot.
    - Handle missing paths gracefully (use `fallback`).
2. **Generative Lists:**
    - Implement the `ForEach` component logic to iterate over collections in the World State.

### E. Skills & I/O (`noetic.skills`)

1. **MCP Adapter:**
    - Implement `adapter_mcp.py` to connect to Model Context Protocol servers.
2. **Internal Skills:**
    - Implement `skill.memory.recall` and `skill.memory.memorize` to allow the Orchestrator to access the Knowledge Store.
