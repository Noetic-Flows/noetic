# Noetic v2 Architecture Reference

**Status:** Technical Specification
**Paradigm:** Software 3.0 (Intent-Driven Flows)

This document details the technical implementation of the Noetic v2 Vision. It describes the component stack, data flow, and interfaces required to support "Sovereign Agentic Software."

---

## 1. System Topology

Noetic follows a **Sidecar Architecture** where the intelligence engine runs as a headless local daemon (`noetic-engine`), accessed by various clients ("Hubs") via the **Agent Server Protocol (ASP)**.

### The Stack

| Layer             | Component             | Function                                                              | Status          |
| :---------------- | :-------------------- | :-------------------------------------------------------------------- | :-------------- |
| **L4: Interface** | **Noetic Hubs**       | CLI, Mobile App, VS Code Extension. Handles Render, Input, and State. | *Partial (CLI)* |
| **L3: Nexus**     | **Context Assembler** | "The CPU." Manages Attention, Token Budgeting, and Intent Assembly.   | *Planned*       |
| **L2: Memory**    | **Tri-Store**         | "The Heap." Hybrid Storage (Semantic + Episodic + Procedural).        | *Implemented*   |
| **L1: Kernel**    | **Core Engine**       | "The OS." Inference Loop, Tool Execution, Safety Guard.               | *Implemented*   |

---

## 2. Event-Driven Core ("The Spine")

To maintain performance and traceability, the system separates blocking logic from non-blocking side effects.

### A. The Event Schema
All system events must implement the sealed `NoeticEvent` interface.

```kotlin
sealed interface NoeticEvent {
    val id: String
    val timestamp: Instant
    val correlationId: String? // Links disparate events to one User Request
    val causationId: String?   // Links an effect to its cause (e.g., ToolOutput -> ToolCall)
}
```

### B. The Bus (`noetic.sync.bus`)
*   **Publishers:** Agent Kernel, Memory Store, User Input.
*   **Subscribers:**
    *   **Performance Tracker:** Logs metrics (Token/sec, Latency).
    *   **Canvas Renderer:** Updates UI state based on Agent thoughts.
    *   **Sync Service:** Pushes data to the mesh/cloud (Fire-and-forget).

---

## 3. Data Architecture: The Hybrid Graph

We simulate sophisticated Graph Database behavior using a lightweight **Hybrid Store** (SQL + Vector) optimized for local devices.

### A. The Tri-Store (Layer 2)
1.  **Semantic Memory (Facts):**
    *   *Storage:* SQL (`FactModel`) + Vector (`Chroma`).
    *   *Retrieval:* Hybrid Search (Metadata Filter + Cosine Similarity).
2.  **Episodic Memory (History):**
    *   *Storage:* Time-series log of `Episode` objects.
    *   *Function:* "Time Travel" context for the Agent ("What did we do last Tuesday?").
3.  **Procedural Memory (Skills):**
    *   *Storage:* Registry of executable `Skill` objects.
    *   *Definition:* Can be AOT Compiled (System) or Runtime Script (User).

### B. The Codex (`.noetic`)
The "File Format" for a user's brain.
*   **Structure:** Flat file bundle (Zip/Folder).
*   **Contents:**
    *   `codex.yaml`: Principles, User Preferences.
    *   `memory.db`: SQLite dump of facts.
    *   `skills/`: User scripts.

---

## 4. Agent Development Kit (ADK) & Hooks

The ADK provides the extensibility model.

### A. Active Hooks (Middleware)
*   **Pattern:** Interceptor Chain.
*   **Behavior:** Blocking.
*   **Example:** `PII_Sanitizer` (redacts prompt before Kernel execution).

### B. Passive Hooks (Listeners)
*   **Pattern:** Pub/Sub.
*   **Behavior:** Async.
*   **Example:** `Zapier_Trigger` (sends HTTP request on `NoteCreated`).

---

## 5. Security: Recursive Guard

Security is not a filter; it is a recursive validation loop.

1.  **Input:** User Prompt -> **Guard** -> Kernel.
2.  **Output:** Kernel -> **Guard** -> Generative UI.
3.  **Interaction:** User clicks UI Button -> **Guard** -> Kernel -> Action.

    *   **Shadow Actions:** For high-stakes operations (Delete, Pay, Send), the Agent creates a "Draft" request which the Guard presents to the user as a **Shadow Action Card** for explicit verification.

---

## 6. Noetic Network Security (The Sovereign Overlay)

To support "Universal Access" across untrusted networks (coffee shop Wi-Fi -> Home Desktop), we implement a **Defense-in-Depth** strategy. We assume the physical network is hostile.

### Tier 1: Transport Sovereignty (The Tunnel)
We utilize a **Mesh VPN (Overlay Network)** to flatten the topology. All devices appear to be on the same private LAN (e.g., `100.x.y.z`), regardless of their physical location.

*   **Technology:** **WireGuard** (Kernel-level speed, state-of-the-art crypto).
*   **Coordination:** **Headscale** (Self-hosted Tailscale control server).
    *   *Why Headscale?* It allows you to run your own "Control Plane." No reliance on third-party SaaS for device discovery.
    *   *Result:* Your phone connects to your desktop via an encrypted tunnel that punches through NATs automatically.

### Tier 2: Application Zero-Trust (User-Centric PKI)
Even inside the WireGuard tunnel, we do not blindly trust traffic. We use **mTLS** tied to **User Identity**, not the device.

*   **The Root of Trust:** The User's Auth Credentials (e.g., Master Key, Biometrics, or IdP) act as the Root CA.
*   **Portable Identity:**
    *   When you log into *any* Hub (Phone, Web, Laptop), you authorize that session.
    *   The Hub generates a distinct, short-lived key pair signed by your **User Identity**.
    *   The **Engine** verifies that the request comes from a key signed by *You*, regardless of which device it originated from.


