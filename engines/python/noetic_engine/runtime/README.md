# Noetic Runtime (`noetic.runtime`)

## 1. Overview

The `noetic.runtime` module is the **Kernel** of the Noetic Engine. It is the machine that plays the Codex.

While `noetic.cognition` decides _what_ to do (The Brain), and `noetic.stage` decides _how_ it looks (The Face), the **Runtime** is responsible for keeping the simulation alive. It manages the event loops, ticking the physics/UI at 60Hz, and asynchronously managing the slow, expensive calls to the Cognitive layer.

**Core Responsibility:** To maintain a fluid, responsive simulation (System 1) that never freezes, even while complex reasoning (System 2) is occurring in the background.

---

## 2. Architecture: The Dual-Loop Engine

The Runtime implements a **Bi-Cameral Execution Model**. We do not use a single `while True` loop that blocks on LLM calls. We use two decoupled systems running in parallel.

### A. The Reflex Loop (System 1)

- **Frequency:** Fixed Time Step (Target: 16ms / 60Hz).
- **Nature:** Synchronous, Non-blocking.
- **Role:** The "Body."
- **Tasks:**

1. **Poll Senses:** Check for raw inputs (mouse, keyboard, sensors) from `noetic.skills`.
2. **Update Stage:** Re-render the A2UI tree based on current Memory (Optimistic UI).
3. **Client-Side Prediction:** If the user types, update the local state immediately.
4. **Dispatch:** Push significant events (e.g., "Submit Button Clicked") to the Cognitive Queue.

### B. The Cognitive Loop (System 2)

- **Frequency:** Event-Driven (Variable).
- **Nature:** Asynchronous, Long-running.
- **Role:** The "Mind."
- **Tasks:**

1. **Observe:** Watch `noetic.memory.event_queue`.
2. **Plan:** When an event occurs, invoke `noetic.cognition` to generate a Plan.
3. **Act:** Execute the **Skills** dictated by the Plan.
4. **Write:** Commit results back to Memory.

### C. The Lifecycle Manager (The Clock)

- **Nature:** State Machine.
- **Role:** Manages the "Circadian Rhythm" of the engine.
- **States:**
  1. **AWAKE (Active):** High CPU, full attention.
  2. **IDLE (Standby):** Low CPU, waiting for input.
  3. **REM (Maintenance):** Background processing (Memory Consolidation, Graph Optimization).

---

## 3. Core Components

### `NoeticEngine` (`engine.py`)

The main entry point for the application.

- **Lifecycle Management:** `load()`, `start()`, `pause()`, `stop()`.
- **Dependency Injection:** It instantiates the singletons (`KnowledgeStore`, `SkillRegistry`, `AgentManager`) and injects them into the loops.
- **Codex Loading:** Uses `NoeticLoader` to read the JSON bundle and hydrate the subsystems.

### `LifecycleManager` (`lifecycle.py`)

Manages the transition between Awake, Idle, and REM states.

- **Idleness Tracking:** Monitors time since last interaction.
- **Interrupts:** Handles `SIG_WAKE` to transition from REM to AWAKE upon user activity.
- **Background Jobs:** Triggers maintenance tasks in `KnowledgeStore` when in REM sleep.

### `ReflexSystem` (`reflex.py`)

Manages the fast loop.

- **Input Buffer:** Aggregates raw inputs from the Senses layer.
- **State Merging:** Overlays "Local UI State" (e.g., scroll position, partial text) on top of "World State" before rendering.
- **Renderer Bridge:** Calls `noetic.stage.render()` and pushes the result to the client (FastUI).

### `CognitiveSystem` (`cognitive.py`)

Manages the slow loop.

- **Cognition Bridge:** It holds the reference to the active `FlowExecutor` or `Planner`.
- **Skill Executor:** This is the **only** component allowed to call `skill.execute()`.
- _Why?_ To ensure that side effects are strictly ordered and recorded in the Knowledge Graph.

### `Scheduler` (`scheduler.py`)

A precise timing mechanism for the Reflex Loop.

- Instead of `sleep(0.016)`, it uses monotonic clocks to ensure consistent tick deltas (`dt`), preventing "spiral of death" lag scenarios.

---

## 4. The Execution Flow (The "Tick")

Here is the pseudocode logic that the AI Assistant must implement in `engine.py`:

```python
async def run_loop(self):
    while self.running:
        start_time = time.monotonic()

        # --- 1. REFLEX PHASE (Fast) ---
        # Fetch generic I/O events (mouse moves, sensor stream updates)
        events = self.skills.poll_inputs()

        # Update the UI layer (Optimistic)
        ui_tree = self.reflex.tick(events, self.memory.world_state)
        self.surface.push(ui_tree)

        # --- 2. COGNITIVE PHASE (Async Check) ---
        # If there are "meaningful" events (triggers), wake up the brain
        if self.memory.has_pending_triggers():
            # We do NOT await this. We fire it as a background task.
            asyncio.create_task(self.cognitive.process_next())

        # --- 3. SLEEP ---
        # Maintain 60Hz cadence
        elapsed = time.monotonic() - start_time
        await asyncio.sleep(max(0, 0.016 - elapsed))

```

---

## 5. Interaction with Other Modules

- **Cognition:** The Runtime _calls_ Cognition. Cognition never calls Runtime.
- `plan = cognition.plan(state)`

- **Skills:** The Runtime acts as the **Invoker**.
- `result = await skill.execute(context)`

- **Stage:** The Runtime acts as the **Driver**.
- `stage.render(state)`

---

## 6. Implementation Directives (For AI Assistant)

### Directive 1: Asyncio Task Management

The Cognitive Loop must be non-blocking.

- Use `asyncio.create_task()` to spawn planning/skill execution.
- **Critical:** Keep track of running tasks. If the engine is stopped, `cancel()` all pending cognitive tasks gracefully.

### Directive 2: Error Isolation

- If the **Reflex Loop** crashes, the application is dead. Log immediately and exit.
- If the **Cognitive Loop** crashes (e.g., LLM failure), the application **must stay alive**.
- Catch the exception.
- Log the error to `noetic.memory` (so the UI can show an error toaster).
- Continue the loop.

### Directive 3: Skill Execution & Cost Tracking

When the `CognitiveSystem` executes a Skill:

1. Start a timer.
2. Run `skill.execute()`.
3. Stop timer.
4. Log a `Fact` to Memory: `(Agent) -[USED]-> (Skill) { cost: $0.05, duration: 200ms }`.

- This allows the agent to "introspect" its own resource usage later.

---

## 7. Directory Structure

```text
/noetic/runtime
├── __init__.py         # Exports NoeticEngine
├── engine.py           # Main Loop & Lifecycle
├── reflex.py           # System 1 Logic (UI/Input)
├── cognitive.py        # System 2 Logic (Planner Bridge)
├── scheduler.py        # Ticking mechanism
└── exceptions.py       # Runtime-specific errors (Crash, Timeout)

```

This architecture ensures the Noetic Engine feels like a **Video Game Engine** (responsive, alive) rather than a **Web Server** (request/response), fulfilling the vision of "Software 3.0."
