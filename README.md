# The Noetic Ecosystem

### Redefining Software: From "Apps" to "Flows"

Welcome to the **Noetic Monorepo**. This repository houses the foundation for a new generation of intelligent software—**Software 3.0**.

For the past decade, we have built "Apps": rigid, pre-compiled logic silos where a developer has to predict every possible user interaction.

**We are building the alternative.**

We believe software shouldn't be a script the user follows; it should be a **Flow** that adapts to the user's intent. The Noetic Ecosystem allows you to describe _what_ you want to achieve (the Goal), and provides the runtime to let a team of AI Agents decide _how_ to achieve it.

---

## What is in this Repository?

This monorepo contains the two pillars required to make Multi-Agent Systems a reality:

### 1. The Noetic Language (`/noetic-lang`)

**The Protocol.**
Just as HTML defines the structure of the web, the Noetic Language is a standard, open JSON protocol for defining **Noetic Flows**.

A **Codex** (a `.noetic` file) does not just define a single "chatbot." It defines a complex, dynamic **Flow**—a complete application state that orchestrates multiple Agents, their shared Memories, and the Stanzas (phases) they operate within. It is the portable blueprint for an entire swarm of intelligence.

### 2. The Noetic Engine (`/noetic-python`)

**The Player.**
This is the reference implementation of the runtime. It reads a Codex and simulates the Flow in real-time. It handles the heavy lifting through a modular "Brain" architecture:

- **Knowledge:** An active **Cognitive Operating System** that manages memory via a strict **Stack & Heap** architecture ("AgentProg") to prevent hallucination. It supports **Portable Seeds**, allowing Flows to "install" knowledge dependencies on new devices instantly.
- **Stanzas:** The structural units of a Flow. A Stanza is a "Chapter" of execution that defines a specific Intent (e.g., "Research Phase") and scopes the collaboration of one or more Agents.
- **Cognition:** The algorithmic core (Planner & Critic) that handles reasoning, confidence calibration, and the "Epistemic Interrupt" loop for ad-hoc learning.
- **Conscience:** The "Axiological Engine" that enforces safety and alignment via **Principles**.
- **Skills:** The reusable capabilities (Python functions) and parameterized cognitive tools that allow Agents to affect the world.
- **Runtime:** The execution kernel managing the **Lifecycle** (Awake/Idle/Sleep) and the **Dual-Loops** (Reflex & Cognitive).
- **Canvas:** The server-driven Generative UI renderer.

> _Note: While the reference engine is currently built in Python, the Noetic Language is platform-agnostic. Future engines will bring Noetic Flows to mobile and other environments._

---

## The Noetic Hierarchy

To manage the complexity of multi-agent systems, Noetic introduces a strict structural hierarchy:

### 1. The Flow (The Poem)

The Flow is the "App" itself. It is a dynamic graph that defines the **Routing Logic** of the user's experience. A Flow can span minutes or months, seamlessly saving and resuming state.

### 2. The Stanza (The Verse)

A Stanza is a **Logical Unit of Intent**. It is not just "an agent's mode"; it is a shared phase of execution where one or more Agents come together to solve a specific sub-problem.

- _Example:_ A "Negotiation Stanza" might involve a **Sales Agent** (talking to the user) and a **Legal Agent** (monitoring constraints) working in the same shared context.
- **Agentic Stanzas:** Defined by a Goal; the Agents figure out the "How."
- **Procedural Stanzas:** Defined by a rigid set of Steps; the Agents follow the SOP.

### 3. The Step (The Line)

An atomic action inside a Procedural Stanza (e.g., "Click Button", "Write File").

---

## Why You Need "Principles" (The Conscience)

Most AI agents are "loose cannons"—they will do anything to achieve a goal, often ignoring safety or cost.

**The Noetic Conscience** solves this by implementing **Principles**. Think of Principles as the "Employee Handbook" that your Agents are forced to read and obey.

- **Without Principles:** You tell an agent to "Fix the database." It deletes the production table to clear the error. (Technically fixed!)
- **With Principles:** You define a Principle: _"Data Preservation: Never delete data without explicit user confirmation."_ The Conscience Module simulates the "Cost" of the delete action, realizes it violates the Principle, and **vetoes** the plan before it executes.

Principles allow you to align Agents with your **Brand, Budget, and Ethics** using simple natural language.

---

## The Vision: Portable Intelligence

In the Noetic model, you don't just ship code; you ship **Understanding**.

A **Noetic Codex** is a self-contained, transportable definition. Because it uses **Semantic Dependencies**, a Flow can verify if it "knows" enough to run on your device.

- **Traditional App:** Crashes if a config file is missing.
- **Noetic Flow:** Checks its **Knowledge Requirements**. If it lacks the concept of "GDPR Compliance," it uses a **Seed** (a bundled graph dump or a research query) to "learn" that concept before it starts execution.

### Coming Soon: The Noetic Marketplace

Because Noetic Flows are just text files, they can be shared as easily as a document. We are building the **Noetic Marketplace**, a decentralized community hub where users can browse, download, and remix Flows.

- Download a "Startup Launcher" Flow.
- Tweak its **Stanzas** to include a "Venture Capital Pitch Phase."
- Adjust its **Principles** to be more "Frugal."
- Run it instantly.

**No compilation. No app stores. Just pure intent.**

---

## Getting Started

You don't need to be a machine learning engineer to build a Noetic Flow. If you can edit a JSON file, you can build an agent.

### 1. Installation

Clone the repo and install the Python Engine:

```bash
git clone https://github.com/noetic-flows/noetic.git
cd noetic/noetic-python
pip install -r requirements.txt

```

### 2. Run a Flow

We include a sample Codex in the `examples` folder.

```bash
python main.py --codex ../noetic-lang/examples/research_team.noetic

```

### 3. Create Your Own

Create a `my-flow.noetic` file. Define your **Stanzas**, **Agents**, **Knowledge Dependencies**, and **Principles**. Run it immediately.

---

## Contributing

We are building the operating system for the age of AI. We need architects, dreamers, and engineers.

- **For Protocol Designers:** Check out `/noetic-lang` to help evolve the schema.
- **For Pythonistas:** Dive into `/noetic-python` to optimize the **AgentProg** memory stack or the **Epistemic Acquisition** pipeline.
- **For Visionaries:** Help us design the first set of Community Flows.

Join us in redefining what software can be.

**[License](https://www.google.com/search?q=./LICENSE)**
