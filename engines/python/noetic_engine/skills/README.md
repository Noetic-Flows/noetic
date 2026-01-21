# Noetic Skills (`noetic.skills`)

## Overview

The `noetic.skills` module represents the **Capabilities** of an Agent. It is the "Body" of the Embodied Mind.

In the Noetic Architecture, the Cortex (Brain) is pure processing. It has **no direct access** to the outside world, nor does it have direct access to its own Memory. To interact with anything—whether sending an email, reading a sensor, or recalling a fact—the Agent must invoke a **Skill**.

This strict mediation allows us to:

1. **Swap Implementations:** Change a "Search" skill from Google to Bing without changing the Agent's logic.
2. **Enforce Permissions:** Prevent a "Guest Agent" from using the "Delete Memory" skill.
3. **Simulate Failures:** Artificially inject noise or forgetfulness into the system for testing.

---

## 1. The Universal Interface

All Skills, regardless of their nature (Network, Database, or System), must implement the unified `Skill` abstract base class.

```python
class Skill(ABC):
    id: str          # e.g., "skill.weather.get"
    description: str # For the Planner to understand when to use it
    schema: Dict     # JSON Schema for arguments

    @abstractmethod
    async def execute(self, context: Context, **kwargs) -> SkillResult:
        """
        The uniform entry point.
        Context: Contains the AgentID and permissions.
        kwargs: The parameters provided by the Planner.
        """
        pass

```

### The `SkillResult`

Skills never return raw data. They return a standardized artifact:

```python
class SkillResult(BaseModel):
    success: bool
    data: Any           # The payload (if success)
    error: str          # Error message (if failure)
    cost: float         # Resource/Time cost incurred
    latency_ms: int

```

---

## 2. Skill Taxonomy

We categorize skills into three distinct domains. The `SkillLoader` handles instantiation based on the `type` field in the Codex.

### A. I/O Skills (`type: "io"`)

Connects the Agent to the External World.

- **Native Adapters:** Python code wrapping local hardware (e.g., `BluetoothSkill`, `CameraSkill`).
- **MCP Adapters:** Connects to **Model Context Protocol** servers. The Skill acts as an MCP Client, translating Noetic intents into JSON-RPC calls over SSE or Stdio.

### B. Knowledge Skills (`type: "knowledge"`)

Connects the Agent to the Internal World.

- **The Paradigm Shift:** The Cortex cannot `import noetic.knowledge`. It must use `skill.recall` or `skill.memorize`.
- **Implementation:** These skills wrap the `KnowledgeStore` methods (`hybrid_search`, `ingest_fact`).
- **Examples:**
- `skill.memory.recall`: Searches the Graph/Vector store.
- `skill.memory.forget`: Marks facts as expired (sets `valid_until`).
- `skill.memory.reflect`: Summarizes recent events (Ingestion).

### C. System Skills (`type: "system"`)

Connects the Agent to the Runtime Engine.

- **Examples:**
- `skill.system.wait`: Pauses execution for seconds.
- `skill.system.terminate`: Ends the current Flow.
- `skill.debug.log`: Writes to the developer console.

---

## 3. The MCP Integration

Noetic treats the **Model Context Protocol (MCP)** as a first-class citizen.

The `McpSkillAdapter` class is responsible for:

1. **Connection Management:** establishing the SSE/Stdio transport to the MCP Server defined in the Codex.
2. **Tool Discovery:** On startup, it queries the MCP server for `tools/list` and dynamically registers them as Noetic Skills.
3. **Execution Proxy:** When the Agent calls the skill, the adapter forwards the arguments via `tools/call`.

---

## 4. Implementation Directives (For AI Assistant)

### The Permission Gate

Before `execute()` is run, the `SkillRegistry` must perform a **Capability Check**.

1. Look at the `context.agent_id`.
2. Load that Agent's definition from the Codex.
3. Verify that `skill.id` exists in the Agent's `skills` list.
4. **If not:** Throw a `PermissionDeniedError`. The Agent tried to use a tool it doesn't have "installed."

### Handling Knowledge Access

Create a concrete class `KnowledgeSkill` that accepts the `KnowledgeStore` singleton in its constructor.

- _Note:_ This is the _only_ place in the system where `noetic.knowledge` and `noetic.skills` are allowed to touch.
- Implement "Hallucination Mode" (Optional): If a global config `noise_level > 0` is set, randomly drop results from `skill.memory.recall` to simulate imperfect memory.

### Async First

All skills must be `async`.

- I/O (Network) is naturally async.
- Knowledge (Database) is async (or threaded).
- **Do not** use blocking `time.sleep()` in System skills; use `await asyncio.sleep()`.

### Error Handling

If a Skill crashes (e.g., API timeout), **do not crash the Engine**.

- Catch the Exception.
- Return `SkillResult(success=False, error="Connection timed out")`.
- This allows the **Planner** to see the failure and try a different strategy (e.g., "The API failed, I will try to Google it instead").

---

## 5. Directory Structure

```text
/noetic/skills
├── __init__.py         # Exports Skill, SkillResult, SkillRegistry
├── interfaces.py       # ABC definitions
├── registry.py         # Loads skills from Codex and manages permissions
├── adapter_native.py   # wrappers for Python code
├── adapter_mcp.py      # Client implementation for Model Context Protocol
└── library/            # The Standard Library of Skills
    ├── io/
    │   ├── http.py
    │   └── file_system.py
    ├── knowledge/
    │   ├── recall.py
    │   └── ingest.py
    └── system/
        └── control.py

```
