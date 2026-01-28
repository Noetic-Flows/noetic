# The Noetic Ecosystem


## Redefining Software: From "Apps" to "Flows"

Welcome to the **Noetic Monorepo**. This repository houses the foundation for a new generation of intelligent software—**Software 3.0**.

> **[Read the Maximally Ambitious Vision](notes/vision.md)**  
> **[Read the Technical Architecture (v2)](notes/architecture/noetic_v2.md)**

For the past decade, we have built "Apps": rigid, pre-compiled logic silos where a developer has to predict every possible user interaction.

**We are building the alternative.**

We believe software shouldn't be a script the user follows; it should be a **Flow** that adapts to the user's intent. The Noetic Ecosystem allows you to describe _what_ you want to achieve, and provides the runtime to let a team of AI Agents decide _how_ to achieve it.

---

## Features Highlights by Target Audience

### **1. For Developers & Architects**

_Target Audience: Software Engineers, AI Researchers, System Designers_

- **The Federated Monorepo:** A "Layered SDK" architecture that decouples data from logic. Developers can use the entire Engine or just individual libraries (e.g., just the Memory module or just the Safety module).
- **The Noetic Protocol (Language-Agnostic):** A standard JSON specification (`packages/spec`) for defining Agents and Flows. This ensures that a Flow written today can eventually run on Python, Kotlin, Swift, or Rust engines without rewriting the logic.
- **The Codex ("The Burrito"):** A single, portable file format (`.noetic`) that wraps everything an agent needs—its Persona, Principles, Knowledge dependencies, and Stanza definitions—into one transportable unit.
- **AgentProg Memory (Stack & Heap):** A rigid memory architecture that solves context window pollution.
- **Working Memory (Stack):** Scoped to the current "Stanza" (task). Automatically garbage collected when the task ends.
- **Long-Term Store (Heap):** A "Tri-Store" of Semantic (Graph), Episodic (Logs), and Procedural (Skills) memory.

- **Hybrid Orchestration (Stanzas):** The ability to mix **Agentic Stanzas** (LLM decides the steps) and **Procedural Stanzas** (Hard-coded SOPs) in the same Flow.
- **Agent Server Protocol (ASP):** A "Sidecar" architecture (similar to LSP) allowing the heavy AI engine to run as a separate local server (Desktop App) while lightweight clients (VSCode, Browser, CLI) connect to it via WebSocket.

### **2. For Enterprise & Business Leaders**

_Target Audience: CTOs, Compliance Officers, Product Managers_

- **The Conscience Module (Safety):** A dedicated library (`noetic-conscience`) that acts as an "Employee Handbook." It evaluates every proposed action against a set of weighted **Principles** (e.g., "Data Privacy," "Frugality") and vetoes plans that are unsafe or too expensive, _before_ they execute.
- **Portable Knowledge Seeds:** The ability to "install" knowledge into an agent instantly. Instead of training a model, you load a **Knowledge Pack** (e.g., "GDPR Compliance JSON") that gives the agent immediate proficiency in a specific domain.
- **Local-First / Privacy:** The architecture supports running the entire "Brain" (LLM inference + Vector DB) locally on the user's machine via the Desktop Server, ensuring sensitive corporate data never leaves the device.
- **Cost Simulation:** The Conscience module can simulate the token/dollar cost of a plan before execution, allowing for budget-aware autonomy.

### **3. For End Users & Creatives**

_Target Audience: Daily Users, Writers, Non-Technical Creators_

- **Noetic Stage (Generative UI):** The interface isn't a static set of buttons; it is a **Projection** of the agent's intent. The agent can "hallucinate" the UI it needs—rendering a chart, a form, or a map on the fly—depending on the context.
- **Flows vs. Apps:** Users don't open "Apps" to do work; they initiate "Flows." A Flow adapts to the user's goal. If you want to write a blog post, the Flow might spin up a "Research Stanza" followed by a "Writing Stanza," seamlessly switching tools for you.
- **The Omnipresent Agent:** Because the Brain runs as a background server, the same Agent persists across different views. You can start a task in your IDE (VSCode), continue it in a Terminal, and finish it in a Browser, with the Agent maintaining full context of the journey.
- **"Visage" / Presence:** A unified module that handles Voice, Avatar, and Tone, making the agent feel like a cohesive entity rather than a text bot.

### **4. For the Community & Ecosystem**

_Target Audience: Modders, Plugin Developers, Early Adopters_

- **The Noetic Marketplace:** A decentralized hub where users can share and download **Flows**, **Stanzas**, and **Knowledge Packs**.
- _Example:_ Download a generic "Startup Founder" Flow, then remix it by swapping the "Generic Marketing Stanza" for a "Guerrilla Marketing Stanza" downloaded from another user.

- **The Standard Library (`stdlib`):** A "Batteries-Included" set of high-quality, pre-built behaviors (Research, Coding, Reflection) that ensure every Noetic Engine has a baseline level of competence out of the box.

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
