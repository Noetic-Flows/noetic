# The Maximally Ambitious Noetic Vision

**Status:** Aspirational / North Star
**Source:** Synthesis of `AI Chat Export` (Burrito evolution) + Current Architecture

This document defines the "Platinum Standard" for the Noetic system—incorporating the most powerful patterns identified during the project's evolution. It centers on the **"Software 3.0"** paradigm: transitioning from rigid apps (Software 1.0) and opaque models (Software 2.0) to **Intent-Driven Flows** orchestrated by agents.

---

## 1. Core Architecture: The "Event-Driven Spine"

The system is defined by a strict separation between **Blocking Core Logic** and **Asynchronous Side Effects**.

*   **The "Spine" (Direct Calls):**
    *   **The Guard/Conscience:** Security checks must be blocking. A request never reaches the Kernel until it passes the Guard.
    *   **Inference Loop:** The "Think → Act → Observe" loop is synchronous and strictly ordered.
    *   **Skill Execution:** Tool calls are direct dependencies of the thought process.
*   **The "Peripheral" (Event Bus):**
    *   **Event Schema:** All events use strictly typed Sealed Interfaces (e.g., `AgentEvent`, `DataEvent`, `UiEvent`) with `correlationId` and `causationId` for perfect "Time-Travel Debugging."
    *   **Tracing & Observability:** The "Performance Tracker" passively listens to the bus. It never slows down execution.
    *   **Generative UI (Canvas):** The UI observes the agent's state and renders reactively. It does not control the agent.
    *   **Data Sync (Collab):** Local writes happen instantly. Background listeners sync to the mesh/cloud.

## 2. Memory: The "Mock Graph" & Hybrid Integration

Memory isn't just a database; it's a unified abstraction layer that mocks complex graph behavior on simple local hardware.

*   **Hybrid Interface Composition:**
    *   `AgentMemory` interface extends both `Database` (SQL) and `VectorStore`.
    *   **Implementation:** Leverages engines (like LibSQL or Chroma+SQLite) that allow **Single-Pass Hybrid Search** (filtering by metadata + vector distance simultaneously).
*   **The "Mock Graph":**
    *   Nodes are stored in Relational Tables (robust, semantic).
    *   Edges are implicit (via Vector Similarity) or explicit (Foreign Keys).
    *   **Benefit:** Gives the agent "Graph Thinking" without the overhead of a dedicated GraphDB on the client.
*   **Reactive Indexing:**
    *   Writing to memory is fast (SQL INSERT).
    *   Indexing (generating embeddings) happens via an event listener (`MemoryCreated`), ensuring the user never waits for the "Spinning Wheel."

## 3. Extensibility: The "Unified Registry" Pattern

The system makes no distinction between "Built-in" and "User-Created" capabilities. All are equal citizens in the Registry.

*   **Unified Skill Registry:**
    *   **AOT Skills:** Compiled, system-level tools (e.g., "File System Access") annotated with `@Skill`.
    *   **Runtime Skills:** User scripts (Python, JS) loaded dynamically.
    *   **Adapter Pattern:** The Registry adapts both into a standard `SkillDefinition` (Schema + Invoker) for the Agent.
*   **Workflow Engine:**
    *   Separates the "Recipe" (Workflow Registry) from the "Chef" (Workflow Engine).
    *   Allows swapping the orchestration logic (e.g., moving from "ReAct" to "Tree of Thoughts") without breaking the skills.

## 4. Interface: Generative UI & "Recursive Safety"

The UI is not a static web page; it is generated via Agents, strictly controlled by the Guard.

*   **Generative Components (Canvas):**
    *   The Agent emits "UI Events" (e.g., `RenderChart`, `ShowForm`).
    *   The Client (Hub) renders these using a library of "Primitive Components" (not raw HTML, for safety).
*   **Recursive Safety (The Loop):**
    *   **Crucial Pattern:** When a user interacts with a generated component (e.g., acts on a "Delete" button), the request **must go back through the Guard**.
    *   The UI cannot call system functions directly; it submits a new "Intent" that the Agent validates (potentially triggering a **Shadow Action Card** for confirmation).

## 5. Deployment: The "Sidecar" Protocol (ASP)

Noetic is designed to run anywhere—CLI, Mobile, Desktop, or Server.

*   **Agent Server Protocol (ASP):**
    *   Formalized WebSocket protocol for "Headless" operation.
    *   Allows the "Brain" (Engine) to run as a background daemon (Sidecar).
    *   Clients (VS Code, Obsidian, Terminal) connect via ASP to "rent" intelligence without hosting it.
*   **Local-First Sovereignty:**
    *   The "Collab Layer" is an observer, not a gatekeeper.
    *   **Optimistic UI:** Interactions are instant, assuming success locally and syncing in the background.
    *   The system functions 100% offline. Sync is a "nice to have" that happens when connectivity is available.
    *   (Reference the local-first manifesto from Ink & Switch: https://www.inkandswitch.com/local-first/)

### C. The Noetic Network & Deployment Strategy
The **Noetic Network** is the unified mesh of compute resources available to you—comprising your personal devices (Laptop, Desktop, Mobile) and optional managed cloud runners (e.g., AWS).

*   **The Hub Concept:**
    *   **Universal Access:** A Hub is a *Portal* into your Noetic Network. You can log in to a Hub on *any* device and access the full power of your backing Network.
    *   **Autonomous Presence:** Agents lives on the Network, not just the device. They run autonomously on your "Workhorse" nodes even when your frontend Hubs are closed.
*   **Topology for the "Power User":**
    *   **The Workhorse (Desktop/Laptop):** Runs the heavy `noetic-engine` daemon (LLM inference, Vector Store, Tool Execution).
    *   **The Mobile Hub (Full Peer):** A full-featured interface. It runs what it can locally and transparently delegates heavy tasks to the Workhorse/Cloud. It is not just a remote control; it is your full agentic workspace in your pocket.
*   **Implementation Strategy (Python-First):**
    *   To rapidly implement this ecosystem, we use **Python** for the initial implementation of all Hubs (Web, Desktop, Mobile).
    *   We accept the trade-off of "non-native" mobile UI in exchange for feature parity and velocity across the Network.
    *   Future efforts will shift focus to Kotlin.

## 6. The "Hooks" Ecosystem (Interceptors vs. Listeners)

The ADK (Agent Development Kit) specifically *enables* hooks by providing two distinct integration points. It does not get in the way; it orchestrates them.

*   **Active Hooks (Interceptors):**
    *   *Mechanism:* Middleware Chain.
    *   *Behavior:* Blocking. Can modify, reject, or redirect a request *before* it processes.
    *   *Use Cases:*
        *   **PII Sanitizer:** Intercepts `Prompt` -> Redacts emails -> Forwards to Kernel.
        *   **Policy Enforcer:** Intercepts `ToolCall` -> Checks budget -> Approves/Denies.
*   **Passive Hooks (Listeners):**
    *   *Mechanism:* Event Bus Subscribers.
    *   *Behavior:* Non-blocking. Fire-and-forget.
    *   *Use Cases:*
        *   **"Zapier-style" Triggers:** "When `NoteCreated`, send email."
        *   **Analytics:** "Log every `TokenUsage` event."

## 7. The Noetic Codex & Principles ("The Constitution")

The **Noetic Codex** is the enabling mechanism for **Software 3.0**. It is the declarative, portable source of truth for the Agent's behavior. We standardize **Codex** as the name for this package/format. It is the "Language" that defines the user's sovereign AI context.

*   **The Codex Format:**
    *   A `.noetic` bundle (zip/folder) containing `markdown`, `yaml`, and `sql` dump.
    *   **Human-Readable:** You can edit your agent's brain in a text editor.
    *   **Portable:** Drop your Codex into a new device, and your Agent is instantly restored.
*   **Principles (The Conscience):**
    *   Unlike generic system prompts ("Be helpful"), Principles are **Weighted Values** stored in the Codex.
    *   **The Guard's Role:** The Guard reads the Codex to enforce these principles *before* execution.
    *   *Example:*
        *   `Principle: Frugality (Weight: 0.9)` -> "Do not use paid APIs unless explicitly authorized."
        *   `Principle: Privacy (Weight: 1.0)` -> "Never transmit health data."

---

### Summary Checklist for the "Maximal" Version

- [ ] **Event Bus**: Typed, sealed, with correlation IDs.
- [ ] **Hybrid Store**: Single-query access to Vector + SQL.
- [ ] **Registries**: Unified AOT/Runtime handling for Skills.
- [ ] **Workflow Engine**: Decoupled from the Core loop.
- [ ] **Recursive Guard**: UI interactions pass through safety checks.
- [ ] **ASP Sidecar**: Robust, headless server mode.
- [ ] **Middleware Hooks**: Interceptor chains for deep system extension.
- [ ] **Noetic Codex**: Portable, human-readable brain dump.
- [ ] **Conscience Engine**: Weighted principle enforcement.
