# Noetic Vision & Alignment

**Date:** 2026-01-27
**Status:** Phase 2 Complete (Libraries Verified)

## 1. The "Noetic" Shift (formerly "Burrito")
The project has evolved from "Burrito" (a code-name for a local-first productivity hub) to **"Noetic"** (a formalized ecosystem for Agentic Flows).

- **Burrito:** Use this term only when referring to historical prototypes or the specific "Hub" client logic (Kotlin/mobile app).
- **Noetic:** The official name of the Engine, Protocol, and Monorepo.

## 2. Core Architectural Pillars (Verified)

### A. Hub vs. Brain Separation
- **The Brain (Implemented):** `noetic-engine`. Stateless, handles inference, memory (Knowledge), and safety (Conscience).
- **The Hub (Mocked/Future):** The Client App (CLI, VSCode, Mobile). Responsible for state, user context, and displaying the UI.
    - *Current State:* `apps/python-cli` and `tests/test_mock_runner.py` act as the Hub.

### B. Malleable Memory (`noetic-knowledge`)
- **Verified:** `KnowledgeStore` implements the Graph + Vector (Chroma) + SQL architecture.
- **Feature:** "AgentProg" Memory Stack (Working Memory) vs. Heap (Long-term) is implemented in `MemoryStack` and `Nexus`.

### C. Safety First (`noetic-conscience`)
- **Verified:** Logic for `Principles`, `Evaluator`, and `Veto` is in place.
- **Goal:** "Employee Handbook" style safety checks before execution.

### D. Generative UI (`noetic-stage`)
- **Verified:** `CanvasRenderer` produces A2UI-compatible JSON.
- **Gap:** "Visage" (Voice/Avatar) is defined in vision but not yet implemented.

## 3. The Agent Server Protocol (ASP)
The `README` describes a "Sidecar" architecture.
- **Current:** `NoeticEngine` runs as a process.
- **Future:** Needs formal WebSocket/IPC layer for true "Sidecar" usage by external apps.

## 4. Next Steps (Phase 3: The Engine)
Focus on cementing the **Runtime Kernel**:
1.  **Flow Manager:** Robust state machine for `Stanza` transitions.
2.  **ASP Layer:** WebSocket/API to allow "The Hub" to connect to "The Brain".
3.  **Cognition Loop:** Finalize the Actor-Critic loop in `noetic_engine.cognition`.
