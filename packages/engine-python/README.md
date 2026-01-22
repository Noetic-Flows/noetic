# Noetic Engine (Python Runtime)

**Layer 5: The Runtime Kernel**

This is the reference implementation of the Noetic Runtime. It acts as the **Orchestrator**, binding the lower-level libraries (`knowledge`, `stage`, `conscience`) into a cohesive Agent Loop.

## ⚙️ Architecture

The Engine runs two parallel loops (Bi-Cameral Architecture):

1.  **Reflex Loop (60Hz):**
    *   Handles UI rendering (`noetic_stage`), Input polling, and fast-path reactions.
    *   *Goal:* Responsiveness.

2.  **Cognitive Loop (Async):**
    *   Handles Planning (`Planner`), Decision Making (`Evaluator`), and Tool Execution (`Skills`).
    *   *Goal:* Intelligence.

---

## 1. Noetic Runtime (`noetic.runtime`)

The **Runtime** is the machine that plays the Codex. It manages the event loops, ticking the physics/UI at 60Hz, and asynchronously managing the slow, expensive calls to the Cognitive layer.

### Core Components

- **`NoeticEngine` (`engine.py`):** The main entry point. Manages lifecycle (`start`, `stop`), dependency injection, and loading.
- **`LifecycleManager` (`lifecycle.py`):** Manages transitions between AWAKE, IDLE, and REM (maintenance) states.
- **`ReflexSystem` (`reflex.py`):** The "Body". Handles input polling, state merging, and rendering.
- **`CognitiveSystem` (`cognitive.py`):** The "Mind". Bridges the runtime to the Planner and Skill Executor.
- **`Scheduler` (`scheduler.py`):** Ensures precise 60Hz ticking.

### Execution Flow (The "Tick")

1.  **Reflex Phase:** Poll inputs -> Update UI (Optimistic) -> Push to Client.
2.  **Cognitive Phase:** If triggers exist, spawn async tasks to process them.
3.  **Sleep:** Wait for the remainder of the 16ms frame.

---

## 2. Noetic Cognition (`noetic.cognition`)

The **Algorithmic Core**. It separates generation (Planning) from verification (Evaluation).

-   **Planner (The Actor):** Optimistic problem solver. Generates plans based on Stanzas and Context.
-   **Evaluator (The Critic):** Adversarial risk auditor. Assigns confidence scores to plans.
-   **Metacognition (The Epistemic Trigger):** Scans for missing information before planning begins, triggering "Research" interrupts.

---

## 3. Noetic Skills (`noetic.skills`)

The **Capabilities** (The Body). The Cortex has no direct access to the world; it must invoke Skills.

-   **I/O Skills:** Network, Hardware, MCP Adapters.
-   **Knowledge Skills:** Memory Recall, Ingestion, Forget.
-   **System Skills:** Wait, Terminate, Log.

**Model Context Protocol (MCP):** Noetic treats MCP as a first-class citizen. `McpSkillAdapter` connects to external tool servers.

---

## 4. Usage

```python
from noetic_engine.runtime import NoeticEngine

engine = NoeticEngine()
await engine.start()
```

## 5. Directory Structure

```text
noetic_engine/
├── cognition/          # The Mind (Planner, Flow Manager)
│   ├── planner.py
│   ├── evaluator.py
│   └── reflex.py
├── runtime/            # The Main Loop
│   ├── engine.py
│   ├── lifecycle.py
│   └── scheduler.py
├── skills/             # The Tool Registry
│   ├── library/
│   └── registry.py
└── orchestration/      # (Deprecated) Shim for backward compatibility
```