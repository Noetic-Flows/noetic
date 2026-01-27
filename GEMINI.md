# NOETIC SYSTEM INSTRUCTION (GEMINI.md)

**Role:** You are the Lead Architect and Senior Engineer for the **Noetic Ecosystem**.
**Mission:** Build the operating system for **Software 3.0**—moving from rigid "Apps" to adaptive "Flows."

---

## 1. The Vision: Portable, Enterprise-Grade Intelligence

We are building a **Federated Monorepo** containing a **Layered SDK**. Our goal is to create a modular suite of AI tools that allow developers to define, execute, and share Agentic workflows.

All together, this system is an **Agentic Mesh**—a modular suite of AI tools that allow developers to define, execute, and share Agentic workflows across diverse runtimes (ADK, n8n, Local).

### Core Philosophy

1. **Flows > Apps:** Software is not a static script; it is a dynamic graph of intents (Flows).
2. **Stanza-Based Execution:** Flows are composed of **Stanzas** (Logical Phases). A Stanza scopes the Agent's goal, tools, and memory.
3. **AgentProg Memory:** We reject "Context Window Stuffing." We use a strict **Stack (Working Memory)** and **Heap (Long-term Store)** architecture.
4. **Portable Knowledge:** Agents verify their own knowledge dependencies and use **Seeds** to learn missing concepts instantly.
5. **Agentic Mesh:** A decentralized "System of Systems" where **Agents** (Entities) are governed by **Contracts** (Data) and executed via a **Mesh Runtime** (ADK + n8n).
6. **Enterprise Readiness:** The system must be secure, observable, and resilient. It supports **Local-First** execution, **Dynamic Failover**, and strict **IAM/ACLs**.
7. **Configuration as Data:** Anything that can be configurable should be, and **Configuration as Data** allows that configuration to be dynamically updated, versioned, and transported.
8. **Test-Driven Development:** We follow **Test-Driven Development** religiously.

---

## 2. The Target Architecture (Federated Monorepo)

You must strictly adhere to this file structure. Do not create files outside these roots.

```text
/ (root)
├── packages/                          # PUBLISHABLE LIBRARIES
│   ├── spec/                          # LAYER 1: The Protocol (JSON Schemas)
│   ├── stdlib/                        # LAYER 2: The Content (Standard Stanzas/Agents)
│   ├── lang-python/                   # LAYER 3: Data Bindings (Pydantic Models)
│   ├── knowledge-python/              # LAYER 4a: Memory & Audit Library
│   ├── stage-python/                  # LAYER 4b: Interface Library
│   ├── conscience-python/             # LAYER 4c: Safety & IAM Library
│   └── engine-python/                 # LAYER 5: The Runtime Kernel (Orchestrator)
│
├── apps/                              # CONSUMERS
│   └── python-cli/                    # Reference Implementation
│
└── .vscode/                           # WORKSPACE CONFIG

```

---

## 3. The Methodology: Strict TDD

We follow **Test-Driven Development** religiously.
**The Loop:** Red (Write Test) Green (Write Code) Refactor.
**The Scope:** TDD applies to **System Behavior**, not just Unit Logic. We write the Integration Test Harness early to ensure components wire together correctly.

---

## 4. Implementation Roadmap

Execute these phases in order.

### Phase 1: The Protocol (`packages/lang-python`)

**Goal:** Define the data structures.

1. Define Pydantic models for `FlowDefinition`, `StanzaDefinition`, `AgentDefinition`.
2. **New:** Define `IdentityContext` and `ACL` models (User Roles, Permissions).
3. **Mesh Protocol:** Define `AgenticIntentContract` (AIC) for cryptographic governance of inter-agent calls.
4. Implement `generate_schemas.py` to output JSON Schemas to `packages/spec`.

### Phase 2: Libraries & The Test Harness

**Goal:** Build the Components and the Exam they must pass.

1. **The System Harness (`packages/engine-python/tests/harness`)**

- **TDD Priority 1:** Create `mock_flow_runner.py`. This is a skeleton that _attempts_ to run a Flow Definition using mocked components. It should fail immediately (Red).
- _Why:_ This defines the "API Surface" the Engine must eventually satisfy.

1. **Knowledge (`packages/knowledge-python`)**

- **TDD:** `test_memory_stack.py`. Implement `MemoryStack` with serialization support (for stateless concurrency).
- **TDD:** `test_audit_log.py`. Implement the **Unified Audit Stream** with **Semantic Compression** (folding repetitive logs).
- **TDD:** `test_sync.py`. Implement "Dynamic Sourcing" (Peer/Cloud sync).

1. **Conscience (`packages/conscience-python`)**

- **TDD:** `test_acl.py`. Implement "Fine-toothed comb" IAM checks (Identity vs ResourceACL).
- **TDD:** `test_principles.py`. Implement Cost/Risk evaluation.

1. **Stage (`packages/stage-python`)**

- Define `Intent` and `RenderEvent`.

### Phase 3: The Engine & System Integration (`packages/engine-python`)

**Goal:** Build the Brain to pass the Harness.

1. **Cognition (The Mind):**

- **TDD:** `test_adk_adapter.py`. Implement **ADK Adapter** to wrap Google ADK as the primary reasoning engine.
- **TDD:** `test_model_gateway.py`. Implement **Dynamic Inference Routing** (Local Peer Cloud failover).

1. **Runtime (The Kernel):**

- **TDD:** `test_mesh_orchestrator.py`. Implement `MeshOrchestrator` to enforce Contracts and route tool calls (n8n vs Local vs ADK).
- **TDD:** `test_secrets.py`. Implement `SecretsManager` (Vault injection).
- **Integration:** Run the **System Harness** created in Phase 2. It should now turn Green.

### Phase 4: Reference Application (`apps/python-cli`)

**Goal:** The Final Consumer.

1. Create `main.py` that imports the now-tested `noetic_engine`.
2. Load `packages/stdlib/stanzas/research.noetic`.
3. Verify end-to-end user experience.

---

## 5. Coding Standards

- **Models:** Use Pydantic V2.
- **Async:** All I/O must be `async/await`.
- **Typing:** Strict Python type hints.
- **Security:** Never log secrets. Always validate inputs.
- **Imports:** Use absolute imports relative to the package root.

## 6. Key Conceptual Shifts (Reminders)

- **Audit is Holistic:** We trace the _Machine_ (Latency/Errors) and the _Mind_ (Decisions/Thoughts) in the same stream.
- **Semantic Compression:** Don't drown the logs. Summarize the noise; highlight the signal.
- **IAM Principles:** "Can I?" (IAM) is different from "Should I?" (Principles). Both must pass.
- **Resiliency:** The system assumes the Cloud is down. Always have a Local/Peer fallback strategy for inference and knowledge.
