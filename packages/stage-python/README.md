# Noetic Stage (Python Library)

**Layer 4b: The Interface Library**

The `noetic.stage` module is the **Face** of the Noetic Engine. It is responsible for rendering the application's user interface.

Unlike traditional UI frameworks (View-Model) or simple Server-Driven UI (JSON View), the Noetic Stage implements a **Generative, Reflex-Reactive Architecture**.

1. **Generative:** The UI structure is not hardcoded in templates; it is dynamically assembled by the **Reflex System** based on the current `WorldState` and the `stage.json` Codex definition.
2. **Reflex-Reactive:** The UI runs on the "Reflex Loop" (60Hz). It updates immediately in response to user input (Client-Side Prediction) while asynchronously synchronizing with the "Brain" (Cognitive Loop).
3. **A2UI Standard:** It utilizes the **Abstract Agent UI (A2UI)** schema, a JSON-based protocol for defining semantic, adaptive interfaces that can be rendered natively on any platform (Web, Mobile, VR).

**Crucial:** The Agents must use a Skill (MCP) for I/O with the Stage.

---

## 1. Architecture: The Reflex Renderer

The Stage is **not** just a passive display. It is an active system that mediates between the User and the Memory.

### The Data Flow

1. **Read:** The Renderer subscribes to `noetic.memory.world_state`.
2. **Bind:** It parses the Stage JSON templates (from the Codex), resolving **Binding Objects** against the current World State.
3. **Hydrate:** It injects active values into the A2UI Tree.
4. **Render:** It pushes the hydrated tree to the frontend (FastUI / React).
5. **Act:** It captures user events, updates the local UI state _instantly_ (Optimistic UI), and flushes the event to the Cognitive Event Queue.

---

## 2. The A2UI Schema (`schema.py`)

This module must strictly enforce the A2UI specification defined in the Noetic Protocol.

### Core Component Types

- **Containers:** `Column`, `Row`, `Stack`, `Card`.
- **Primitives:** `Text`, `Button`, `Image`, `Icon`.
- **Inputs:** `TextField`, `Slider`, `Toggle`.
- **Generative:** `ForEach` (iterates over Entity lists), `Conditional` (renders based on Logic).

### Data Binding Strategy: JSON Pointers

Because Noetic Apps are defined purely in JSON (without compiled code), we cannot use standard binding frameworks like React State or compiled Swift/Kotlin bindings. Text templating engines (like Mustache/Jinja) are also unsuitable because they operate on strings, not live object trees, and would destroy the performance of our 60Hz Reflex Loop.

Instead, we use **Binding Objects** powered by standard **JSON Pointers (RFC 6901)**.

**The Schema:**

```json
{
  "type": "Text",
  "content": {
    "bind": "/entities/plant-1/species", // JSON Pointer
    "fallback": "Unknown"
  }
}
```

**How it works:**
The Renderer treats the `WorldState` as a single JSON document. When it encounters an object with the `"bind"` key, it uses a standard JSON Pointer library to traverse the Memory path (e.g., look inside `entities`, find `plant-1`, get `species`) and returns the value.

---

## 3. Implementation Strategy (Python Reference)

For this Python reference implementation, we use **FastUI** (by Pydantic) as the rendering target. This proves that Noetic A2UI can drive a modern, reactive web interface.

### `StageRenderer` (`renderer.py`)

The main class responsible for the translation layer.

**Logic:**

1. **Load Templates:** Parse `stage.json` into Pydantic models.
2. **Resolve Context:** Create a `RenderContext` containing the current Entities and Facts.
3. **Tree Traversal:** Walk the A2UI JSON tree recursively.
    - **Detection:** Check if a property value is a dictionary containing the key `"bind"`.
    - **Resolution:** If yes, use the `jsonpointer` library to resolve the value from the `RenderContext`.
4. **Target Translation:** Convert the fully hydrated A2UI Node into a **FastUI Component**.
    - `A2UI.Column` -> `FastUI.Div`
    - `A2UI.Button` -> `FastUI.Button(on_click=...)`

### `ReflexManager` (`reflex.py`)

Manages the "Game Loop" aspect of the UI.

**Logic:**

- Maintains a `local_state` dictionary for transient UI data (e.g., text being typed into a field) that hasn't reached the Brain yet.
- Merges `local_state` over `world_state` during rendering to ensure the UI feels responsive (Zero-Latency Typing).

---

## 4. Implementation Details

### Data Binding Resolution

- **Library:** Use `jsonpointer` (standard Python lib).
- **Robustness:** If a pointer path does not exist (e.g., `entities/plant-999`), the resolver **must not crash**. It should return the `fallback` value or `null`.
- **Type Safety:** Ensure that if a boolean property (like `visible`) binds to a string value, it is cast appropriately or handled safely.

### FastUI Integration

- Map A2UI `action_id` strings to FastUI `BackEvent`.
- When a FastUI event fires, the handler must:
    1. Look up the action in the Stage JSON (from the Codex).
    2. If it's a local action (e.g., "Toggle Details"), update `local_state`.
    3. If it's an agent action (e.g., "Water Plant"), create a `noetic.senses.Event` and push it to `memory.event_queue`.

### Generative Lists (`ForEach`)

Support the `iterator` pattern in JSON:

```json
{
  "type": "ForEach",
  "source": { "bind": "/queries/active_plants" },
  "as": "item",
  "child": {
    "type": "Text",
    "content": { "bind": "/item/species" } // Scoped resolution
  }
}
```

The renderer must iterate over the list found at `source` and generate a list of components, temporarily injecting `item` into the resolution scope.

### Theme Support

Respect the `theme` field in Stage JSON (in the Codex). If `theme="noetic.themes.dark"`, inject the appropriate CSS classes or FastUI style props into the components.

## 5. Usage

```python
from noetic_stage import CanvasRenderer, Component

# Render a component with live data binding
ui = CanvasRenderer().render(
    root=Component(...), 
    context=world_state
)
```

## 6. Directory Structure

```text
noetic_stage/
├── __init__.py         # Exports StageRenderer
├── schema.py           # Pydantic Models for A2UI (The Language)
├── renderer.py         # Main Logic (A2UI -> FastUI Translator)
├── reflex.py           # State merging and Event handling
├── bindings.py         # The JSON Pointer resolution logic
└── components/         # Individual component mappers
    ├── containers.py
    ├── primitives.py
    └── inputs.py
```