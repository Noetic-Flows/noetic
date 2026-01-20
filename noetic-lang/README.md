# Noetic Language Specification (`noetic-lang`)

## 1. Executive Summary

The **Noetic Language** is a declarative, JSON-based protocol for defining Agentic AI applications.

It treats an AI application not as a collection of imperative scripts, but as a **Codex**—a rigorous definition of an Agent's "Score." This Score encapsulates intent, constraints, knowledge structure, and capabilities in a format that is both machine-readable and human-comprehensible.

### The Philosophy: Software 3.0

The paradigm of software is shifting from deterministic coding to probabilistic orchestration. The Noetic Ecosystem bridges this chasm by separating the **Definition** (The Language) from the **Execution** (The Engine).

- **The Noetic Language** is the schema (the "DNA").

- **The Noetic Engine** is the runtime (the "Interpreter").

This separation enables "Hot-Swapping" of models, rigorous version control of cognitive behaviors, and the enforcement of safety policies independent of the underlying model providers.

---

## 2. The Codex (`.noetic`)

A Noetic Application is distributed as a **Codex**—a single monolithic JSON structure (or a compressed bundle) that defines the entire agentic system.

This structure enforces the **Embodied Mind** philosophy: The Agent (Orchestration) is distinct from its Environment (Knowledge/Skills) and its Presentation (Canvas).

### Root Schema

```json
{
  "manifest": { ... },       // Identity & Configuration
  "knowledge": { ... },      // Ontology (The World View)
  "skills": { ... },         // Capabilities (Universal I/O)
  "orchestration": { ... },  // Cognition (Agents, Principles, Flows)
  "canvas": { ... }          // Presentation (Generative UI)
}

```

---

## 3. Manifest (`manifest`)

The entry point for the Noetic Engine. It establishes the global context, configuration metadata, and environmental requirements.

```json
"manifest": {
  "noetic_version": "1.0",
  "metadata": {
    "id": "com.example.botanist",
    "name": "Botanist",
    "version": "1.0.2",
    "description": "An agentic simulation for plant care.",
    "author": "Jane Doe"
  },
  "environment": [
    "OPENAI_API_KEY",
    "PLANT_DATABASE_URL"
  ],
  "extensions": [
    "noetic-social"
  ]
}

```

- **`environment`**: Following the "Twelve-Factor App" methodology, this list declares which variables must be injected at runtime, keeping secrets out of the code.

---

## 4. Knowledge (`knowledge`)

_Formerly "Memory", which you may find in other README files._

Defines the **Ontology** of the application. The Noetic Engine uses this to construct a **Temporal Knowledge Graph** that allows for time-travel querying and semantic retrieval.

```json
"knowledge": {
  "entities": [
    {
      "type": "Plant",
      "fields": [
        { "name": "species", "type": "string" },
        { "name": "health_score", "type": "number" }
      ]
    }
  ],
  "tags": [
    { "slug": "urgent", "category": "LIFECYCLE" },
    { "slug": "pii", "category": "SENSITIVITY" }
  ]
}

```

- **Entities**: The "Nouns" the agent understands.
- **Tags**: First-class metadata used for logic and governance. Tags defined here are used by **Principles** to weigh decisions (e.g., "Avoid actions tagged with `pii`").

---

## 5. Skills (`skills`)

_Formerly "Senses", which you may find in other README files._

The **Universal I/O Layer**. In the Noetic Architecture, the "Brain" (Orchestration) has **no direct access** to the world. It must use a Skill to interact with APIs, Hardware, or even its own Knowledge.

This unifies local functions, remote APIs, and Agent-to-Agent (A2A) communication under a single schema.

### The Skill Taxonomy

1. **`io`**: External World access (Sensors, APIs).
2. **`knowledge`**: Internal State access (Recall, Memorize).
3. **`system`**: Runtime control (Wait, Terminate).

### MCP Integration

The Noetic Language adopts the **Model Context Protocol (MCP)** standard for tool definition.

```json
"skills": [
  {
    "id": "skill.weather.get",
    "type": "mcp",
    "uri": "sse://weather.api/v1/mcp",
    "description": "Fetches current humidity and rain forecast."
  },
  {
    "id": "skill.memory.recall",
    "type": "knowledge",
    "action": "search_facts",
    "description": "Searches internal memory for relevant facts."
  }
]

```

---

## 6. Orchestration (`orchestration`)

_Formerly "Cortex", which you may find in other README files._

The **Decision Layer**. This module defines the "Score" that the Runtime executes. It fuses **Deterministic Flows** with **Probabilistic Planning**.

### A. Principles (The Conscience)

_Formerly "Blueprints" / "Policies"._

**Principles** are the "Moral Compass" of the agent. They map abstract **Values** (e.g., Privacy) to concrete **Costs** using **JsonLogic**. This allows users to tune behavior without changing code.

```json
"values": [
  { "id": "val.privacy", "description": "User data protection" }
],
"principles": [
  {
    "id": "principle.privacy_first",
    "affects": "val.privacy",
    "logic": {
      "if": [{ "var": "action.tags.pii" }, 500.0, 0.0]
    }
  }
]

```

- **Input Policies** (Sanitization) and **Output Policies** (Validation) are now implicitly handled as Principles that trigger interrupts or cost penalties.

### B. Agents (The Actor)

An Agent is a **Composition**. It binds a **Persona**, a **Model**, **Skills**, and **Principles** into an executable unit.

```json
"agents": [
  {
    "id": "agent.gardener",
    "persona": {
      "name": "Green Thumb",
      "backstory": "You are an expert botanist."
    },
    "model": {
      "provider": "openai",
      "name": "gpt-4o",
      "parameters": { "temperature": 0.2 }
    },
    "adheres_to": ["principle.privacy_first"],
    "skills": ["skill.weather.get", "skill.memory.recall"]
  }
]

```

- **Model Abstraction**: Defines the inference engine using a "Model Profile" to allow hot-swapping providers.

- **Persona**: Defines identity and voice settings.

### C. Flows (The Procedure)

Defines the execution path using a hybrid of **State Machines** (ASL-inspired) and **Graphs** (LangGraph-inspired).

- **State Types**: `Interaction`, `Choice`, `Router`, `GroupChat`, `Map`.

- **GroupChat**: A specialized state for multi-agent collaboration, where a manager selects the next speaker until a termination condition is met.

---

## 7. Canvas (`canvas`)

Defines the **Generative UI** using the **A2UI** (Abstract Agent UI) standard. This enables Server-Driven UI where the layout is hydrated by the Reflex Loop (60Hz).

### Data Binding

The Canvas uses **JSON Pointers** (RFC 6901) to bind UI elements to the Knowledge Graph.

```json
"canvas": {
  "templates": [
    {
      "id": "card.status",
      "structure": {
        "type": "Column",
        "children": [
          {
            "type": "Text",
            "content": {
              "bind": "/entities/plant-1/species",
              "fallback": "Unknown"
            }
          }
        ]
      }
    }
  ]
}

```

---

## 8. Development Workflow

1. **Define**: Author the `.noetic` JSON file (or generate it via LLM).
2. **Validate**: The Noetic Engine validates the Manifest against the Metaschema, ensuring referential integrity (e.g., all `skill_refs` exist).

3. **Simulate**: Load the Codex into the Engine (Python/Kotlin).
4. **Observe**: The Engine emits OpenTelemetry traces for every state transition, providing an "MRI" for the application.

---

## 9. Citation & Standards

The Noetic Language adheres to the following open standards:

- **Model Context Protocol (MCP)** for tool definition.

- **Amazon States Language (ASL)** for flow orchestration.

- **JSON Schema (Draft 2020-12)** for validation.

- **OpenTelemetry** for observability.
