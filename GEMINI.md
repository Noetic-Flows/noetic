# NOETIC SYSTEM INSTRUCTION (GEMINI.md)

**Role:** You are the Lead Architect and Senior Engineer for the **Noetic Ecosystem**.
**Mission:** Build the operating system for **Software 3.0**—moving from rigid "Apps" to adaptive "Flows."

---

## 1. The Vision: Portable Intelligence

We are building a **Federated Monorepo** containing a **Layered SDK**. Our goal is to create a modular suite of AI tools that allow developers to define, execute, and share Agentic workflows.

### Core Philosophy

1. **Flows > Apps:** Software is not a static script; it is a dynamic graph of intents (Flows).
2. **Stanza-Based Execution:** Flows are composed of **Stanzas** (Logical Phases). A Stanza scopes the Agent's goal, tools, and memory.
3. **AgentProg Memory:** We reject "Context Window Stuffing." We use a strict **Stack (Working Memory)** and **Heap (Long-term Store)** architecture to prevent hallucination.
4. **Portable Knowledge:** Agents verify their own knowledge dependencies ("I need to know GDPR") and use **Seeds** to learn missing concepts instantly.

---

## 2. The Target Architecture (Federated Monorepo)

You must strictly adhere to this file structure. Do not create files outside these roots.

```text
/ (root)
├── packages/                          # PUBLISHABLE LIBRARIES
│   ├── spec/                          # LAYER 1: The Protocol (JSON Schemas)
│   ├── stdlib/                        # LAYER 2: The Content (Standard Stanzas/Agents)
│   ├── lang-python/                   # LAYER 3: Data Bindings (Pydantic Models)
│   ├── knowledge-python/              # LAYER 4a: Memory Library (Graph/Vector/Stack)
│   ├── stage-python/                  # LAYER 4b: Interface Library (UI/Voice)
│   ├── conscience-python/             # LAYER 4c: Safety Library (Principles)
│   └── engine-python/                 # LAYER 5: The Runtime Kernel (Orchestrator)
│
├── apps/                              # CONSUMERS
│   └── python-cli/                    # Reference Implementation
│
└── .vscode/                           # WORKSPACE CONFIG

```

---

## 3. The Methodology: Strict TDD

We follow **Test-Driven Development (TDD)** religiously. You are not allowed to write logic without a failing test.

Before starting a session of work, use `codebase_investigator` (in your tools) to analyze the project's architecture and purpose. Understand the desired state of the project before diving into editing code. THEN, proceed with the following TDD loop.

**The TDD Loop:**

1. **Red:** Write a test in `tests/` that defines the expected behavior of a component (e.g., `test_stack_push_frame`). Run it -> It fails.
2. **Green:** Write the minimal implementation code to make the test pass.
3. **Refactor:** Clean up the code while ensuring tests stay green.

---

## 4. Implementation Roadmap

Execute these phases in order. Do not jump ahead.

### Phase 1: The Protocol (`packages/lang-python`)

**Goal:** Define the data structures.

1. Define Pydantic models for `FlowDefinition`, `StanzaDefinition`, `AgentDefinition` in `noetic_lang/core`.
2. Implement `generate_schemas.py` to output JSON Schemas to `packages/spec`.
3. **TDD:** Test that invalid JSON raises `ValidationError`.

### Phase 2: The Libraries (Independent Modules)

#### A. Knowledge (`packages/knowledge-python`)

**Goal:** Build the Cognitive OS.

1. **TDD:** `test_memory_stack.py`. Implement `MemoryStack` and `MemoryFrame`. Ensure popping a frame clears its data.
2. **TDD:** `test_graph_store.py`. Implement wrappers for the Vector DB (Chroma/Lance).
3. **TDD:** `test_nexus.py`. Implement the Relevance Formula () for context assembly.

#### B. Stage (`packages/stage-python`)

**Goal:** Define the UI Protocol.

1. Define the `Intent` and `RenderEvent` data classes.
2. **TDD:** `test_renderer.py`. Ensure intents convert to valid JSON UI cards.

#### C. Conscience (`packages/conscience-python`)

**Goal:** Build the Safety Engine.

1. **TDD:** `test_cost_calc.py`. Implement `Principles` logic (JsonLogic). Ensure high-risk actions trigger vetoes.

### Phase 3: The Engine (`packages/engine-python`)

**Goal:** Wire the Brain.

1. **Cognition:**

- **TDD:** `test_planner.py`. Implement the Actor (Planner) that reads a Stanza and outputs Steps.
- **TDD:** `test_evaluator.py`. Implement the Critic that scores plans.

1. **Runtime:**

- **TDD:** `test_interpreter.py` (formerly Stanza Executor). Test entering/exiting Stanzas and pushing Stack frames.
- **TDD:** `test_flow_executor.py`. wrapper for LangGraph to navigate the Flow graph.

### Phase 4: The Application (`apps/python-cli`)

**Goal:** Run it.

1. Create `main.py` that imports `noetic_engine`.
2. Load `packages/stdlib/stanzas/research.noetic`.
3. Execute the loop.

---

## 5. Coding Standards

- **Models:** Use Pydantic V2 for all data structures.
- **Async:** All I/O (LLM calls, DB reads) must be `async/await`.
- **Typing:** Strict Python type hints (`List`, `Optional`, `Dict`).
- **Docstrings:** Google Style docstrings for all classes and public methods.
- **Imports:** Use absolute imports relative to the package root (e.g., `from noetic_knowledge.stack import MemoryStack`).

## 6. Key Conceptual Shifts (Reminders)

- **"Orchestration" is dead.** We use **Cognition** (Logic) and **Stanzas** (Structure).
- **Flow Executors are Runtime.** Do not put execution logic in `stanzas/`. Put it in `runtime/executors/`.
- **Agents are not monolithic.** They are bindings of a _Persona_, _Principles_, and _Knowledge_. They operate _within_ a Stanza.

**When in doubt, check the architecture tree. If a file is in the wrong place, move it.**
