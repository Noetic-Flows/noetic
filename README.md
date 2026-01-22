# The Noetic Ecosystem

### Redefining Software: From "Apps" to "Flows"

Welcome to the **Noetic Monorepo**. This repository houses the foundation for a new generation of intelligent software—**Software 3.0**.

For the past decade, we have built "Apps": rigid, pre-compiled logic silos where a developer has to predict every possible user interaction.

**We are building the alternative.**

We believe software shouldn't be a script the user follows; it should be a **Flow** that adapts to the user's intent. The Noetic Ecosystem allows you to describe _what_ you want to achieve, and provides the runtime to let a team of AI Agents decide _how_ to achieve it.

---

## Architecture: The Federated Monorepo

We have moved beyond a monolithic engine. Noetic is designed as a **Layered SDK Architecture**. This means distinct parts of the "Brain"—like Memory, Safety, or UI—are built as standalone, publishable libraries.

**Why is this beneficial?**

- **Modularity:** You can use the **Conscience** library to add safety guardrails to a standard chatbot without needing the full Noetic Engine.
- **Portability:** The core logic is separated from the application, allowing the same Agent to run in a CLI, a Desktop App, or a VSCode Extension.
- **Polyglot Future:** The architecture supports future language bindings (e.g., Kotlin for mobile) sharing the same core Protocol.

### The Repository Structure

The repo is organized by abstraction layer in the `packages/` directory:

| Layer            | Package             | Description                                                                                    |
| ---------------- | ------------------- | ---------------------------------------------------------------------------------------------- |
| **1. Protocol**  | `spec`              | The language-agnostic **JSON Schemas**. The Source of Truth.                                   |
| **2. Content**   | `stdlib`            | The **Standard Library** of reusable Stanzas (`research.noetic`), Agents, and Knowledge Packs. |
| **3. Bindings**  | `lang-python`       | The **Data Layer**. Pure Pydantic models that implement the Spec.                              |
| **4. Libraries** | `knowledge-python`  | **The Memory.** A standalone Graph/Vector store with AgentProg-style stack logic.              |
|                  | `stage-python`      | **The Interface.** A protocol for Generative UI, Voice, and Presence.                          |
|                  | `conscience-python` | **The Safety.** An engine for evaluating actions against ethical Principles.                   |
| **5. Kernel**    | `engine-python`     | **The Brain.** The orchestrator that binds Cognition, Memory, and Runtime together.            |

Applications (consumers of these packages) live in the `apps/` directory, such as the Reference CLI or the VSCode Extension.

---

## The Core Components

### 1. The Noetic Language (`packages/spec`)

Just as HTML defines the structure of the web, the Noetic Language is a standard, open JSON protocol for defining **Noetic Flows**.
A **Codex** (a `.noetic` file) defines a dynamic **Flow**—a complete application state that orchestrates multiple Agents, their shared Memories, and the Stanzas they operate within.

### 2. The Noetic Hierarchy

To manage the complexity of multi-agent systems, Noetic introduces a strict structural hierarchy:

- **The Flow (The Poem):** The high-level application definition. A graph of Stanzas and Agents.
- **The Stanza (The Verse):** A distinct phase of execution with its own Goal and Scope.
- _Agentic Stanza:_ "Here is the goal, figure it out."
- _Procedural Stanza:_ "Follow these exact steps."

- **The Step (The Line):** An atomic instruction inside a Procedural Stanza.

### 3. The "Brain" Modules

- **Knowledge (`noetic_knowledge`):** An active **Cognitive Operating System**. It manages memory via a strict **Stack & Heap** architecture (inspired by "AgentProg") to prevent hallucination. It supports **Portable Seeds**, allowing Flows to "install" knowledge dependencies on new devices instantly.
- **Cognition (`noetic_engine.cognition`):** The algorithmic core. It features an **Actor-Critic** architecture (Planner & Evaluator) and **Metacognition** (Epistemic Interrupts) to detect when the agent needs to stop and learn before acting.
- **Conscience (`noetic_conscience`):** The "Employee Handbook" for Agents. It evaluates the "Moral Cost" of actions against weighted **Principles** (e.g., "Data Privacy"), vetoing unsafe plans before they execute.
- **Stage (`noetic_stage`):** The "Front Stage" of the agent. It manages the **Generative UI**, rendering intents into JSON cards, Voice, or Avatars.

---

## The Vision: Portable Intelligence

In the Noetic model, you don't just ship code; you ship **Understanding**.

A **Noetic Codex** is a self-contained, transportable definition. Because it uses **Semantic Dependencies**, a Flow can verify if it "knows" enough to run on your device.

- **Traditional App:** Crashes if a config file is missing.
- **Noetic Flow:** Checks its **Knowledge Requirements**. If it lacks the concept of "GDPR Compliance," it uses a **Seed** (a bundled graph dump or a research query) to "learn" that concept before it starts execution.

---

## Getting Started

### 1. Installation

Clone the monorepo and install the CLI application:

```bash
git clone https://github.com/noetic-flows/noetic.git
cd noetic
pip install -e packages/engine-python  # Install the engine logic
pip install -r apps/python-cli/requirements.txt

```

### 2. Run a Flow

Use the Python CLI app to run a sample Flow from the Standard Library:

```bash
python apps/python-cli/main.py --codex packages/stdlib/stanzas/research.noetic

```

---

## Contributing

We are building the operating system for the age of AI. We need architects, dreamers, and engineers.

- **For Protocol Designers:** Check out `packages/spec` to help evolve the JSON schema.
- **For Pythonistas:** Dive into `packages/engine-python` or individual libraries like `knowledge-python`.
- **For Visionaries:** Help us build the `stdlib` by designing the first set of Community Flows.

Join us in redefining what software can be.

**[License](https://www.google.com/search?q=./LICENSE)**
