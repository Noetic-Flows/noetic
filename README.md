# The Noetic Ecosystem

### Redefining Software: From "Apps" to "Flows"

Welcome to the **Noetic Monorepo**. This repository houses the foundation for a new generation of intelligent software—Software 3.0.

For the past decade, we have built "Apps": rigid, pre-compiled logic silos where a developer has to predict every possible user interaction.

**We are building the alternative.**

We believe software shouldn't be a script the user follows; it should be a **Flow** that adapts to the user's intent. The Noetic Ecosystem allows you to describe _what_ you want an AI agent to achieve, and provides the runtime to let the agent decide _how_ to achieve it.

---

## What is in this Repository?

This monorepo contains the two pillars required to make Agentic AI a reality:

### 1. The Noetic Language (`/noetic-lang`)

**The Protocol.**
Just as HTML defines the structure of the web, the Noetic Language is a standard, open JSON protocol for defining an Agent. It captures the Agent's brain, values, memories, and interface in a single, portable format called a **Codex**.

### 2. The Noetic Engine (`/noetic-python`)

**The Player.**
This is the reference implementation of the runtime. It reads a Codex and simulates the agent in real-time. It handles the heavy lifting—memory management, planning, and UI rendering—so you can focus on designing the intelligence.

> _Note: While the reference engine is currently built in Python, the Noetic Language is platform-agnostic. Future engines will bring Noetic Flows to mobile and other environments._

---

## The Vision: The "App" is Dead. Long Live the Flow

In the Noetic model, you don't "code an app." You **compose a Flow**.

A **Noetic Flow** is a portable definition of an agent's purpose. Because it is defined in data (JSON), not code, it is transparent, remixable, and safe.

- **Traditional App:** A developer hard-codes a "Save" button. If the database changes, the app breaks.
- **Noetic Flow:** You define a Goal ("Persist user data") and a Principle ("Protect user privacy"). The Agent dynamically figures out how to save the data using the tools available to it.

### Coming Soon: The Noetic Flow Library

Because Noetic Flows are just text files, they can be shared as easily as a document.

We are building the **Noetic Flow Library**, a decentralized community hub where users can browse, download, and remix Flows.

- Download a "Fitness Coach" Flow.
- Tweak its **Values** to be less "Aggressive" and more "Supportive."
- Run it instantly on your Noetic Engine.

**No compilation. No app stores. Just pure intent.**

---

## Getting Started

You don't need to be a machine learning engineer to build a Noetic Flow. If you can edit a text file, you can build an agent.

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
python main.py --codex ../noetic-lang/examples/TODO.noetic

```

### 3. Create Your Own

Create a `my-agent.noetic` file. Define your agent's **Persona**, **Goals**, and **UI** using the Noetic Language. Run it immediately.

---

## Contributing

We are building the operating system for the age of AI. We need architects, dreamers, and engineers.

- **For Protocol Designers:** Check out `/noetic-lang` to help evolve the schema.
- **For Pythonistas:** Dive into `/noetic-python` to optimize the decision loops and memory systems.
- **For Visionaries:** Help us design the first set of Community Flows.

Join us in redefining what software can be.

**[License](./LICENSE)**
