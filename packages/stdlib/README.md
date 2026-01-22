# Noetic Standard Library (`@noetic/stdlib`)

## Overview

The **Noetic Standard Library** is the "Batteries-Included" layer of the Noetic Ecosystem.

While the **Spec** defines the grammar of the Noetic Language, the **StdLib** provides the essential vocabulary. It contains a collection of battle-tested, reusable **Stanzas**, **Agents**, and **Knowledge Packs** that cover common AI workflows.

Developers should not have to reinvent "How to perform web research" or "How to write a unit test." These behaviors are standardized here as portable `.noetic` definitions that can be loaded by any compliant Noetic Engine (Python, Kotlin, etc.).

---

## Directory Structure

```text
packages/stdlib/
├── stanzas/           # Reusable Phases of Execution
│   ├── research.noetic
│   ├── coding.noetic
│   └── review.noetic
│
├── agents/            # Standard Personas
│   ├── system.noetic
│   └── architect.noetic
│
├── knowledge/         # Knowledge Seeds & Packs
│   └── packs/
│       └── core_safety.json
│
└── package.json       # Metadata

```

---

## Core Components

### 1. Standard Stanzas (`/stanzas`)

A **Stanza** is a unit of intent. These files define complete execution graphs for specific goals.

- **`research.noetic`:** A robust "Deep Dive" flow.
- _Inputs:_ A query topic.
- _Behavior:_ Performs recursive web searches, extracts content, synthesizes findings, and cites sources.
- _Dependencies:_ `io.web.search`, `skill.cognitive.summarize`.

- **`coding.noetic`:** A "DevOps" loop.
- _Inputs:_ A feature request or bug report.
- _Behavior:_ Scans the codebase, plans a diff, writes the file, and runs linter/tests.

- **`reflection.noetic`:** A "Critic" loop.
- _Inputs:_ A draft plan or artifact.
- _Behavior:_ Analyzes the input against quality heuristics and outputs a list of critiques.

### 2. Standard Agents (`/agents`)

These are pre-configured **Persona Bindings**. They include the System Prompt and the necessary Knowledge scope.

- **`system.noetic`:** The root supervisor. Capable of high-level routing and meta-cognition.
- **`architect.noetic`:** Specialized in system design, patterns, and structure.

### 3. Knowledge Packs (`/knowledge`)

These are **Seeds**—portable dumps of graph or semantic data that can be "installed" into an Agent's memory.

- **`core_safety.json`:** The "Three Laws" (and then some). A standard set of **Principles** regarding data privacy, user consent, and non-destructive action.

---

## Usage

These definitions are designed to be imported directly into your custom Codex.

### In a Flow Definition

You can reference standard stanzas by their package path:

```json
{
  "id": "my-startup-flow",
  "nodes": [
    {
      "id": "market-research",
      "type": "STANZA",
      "source": "@noetic/stdlib/stanzas/research.noetic",
      "inputs": {
        "topic": "AI Market Trends 2026"
      }
    }
  ]
}
```

### In the Python CLI

You can run a standard Stanza directly to test its behavior:

```bash
# Run the Research Stanza directly
python apps/python-cli/main.py --codex packages/stdlib/stanzas/research.noetic

```

---

## Contributing

The Standard Library is community-driven. If you have built a robust Stanza (e.g., "Social Media Manager" or "Data Analysis"), please contribute it!

1. **Atomicity:** Ensure your Stanza relies only on standard Skills.
2. **Portability:** Do not hardcode paths or user-specific data.
3. **Documentation:** Add comments in the `.noetic` file explaining the inputs and outputs.
