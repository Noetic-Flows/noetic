# Noetic Lang (Python Bindings)

**Layer 3: The Data Protocol**

This package contains the **Pure Data Models** for the Noetic Ecosystem. It defines the "Shape" of the universe—Agents, Stanzas, Flows, and Actions—using Pydantic.

## 🚫 Constraints

- **No Logic:** This package must never contain business logic, execution code, or side effects.
- **No Heavy Dependencies:** It should only depend on `pydantic`.
- **Source of Truth:** These models are used to generate the JSON Schemas in `packages/spec`.

## 📂 Structure

- `noetic_lang.core`: The primary definitions (`AgentDefinition`, `StanzaDefinition`, `Plan`, `Goal`).
- `noetic_lang.utils`: Lightweight validators and ID generators.

## 🛠️ Usage

```python
from noetic_lang.core import AgentDefinition

agent = AgentDefinition(
    id="agent.architect",
    persona={"role": "System Architect"}
)
```
