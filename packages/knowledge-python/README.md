# Noetic Knowledge (Python Library)

**Layer 4a: The Cognitive Operating System**

The `noetic.knowledge` module is the **Cognitive Operating System** of the Noetic Engine.

Unlike traditional architectures that treat memory as a passive database (RAG), Noetic treats memory as an active **Virtual Machine**. It manages the Agent's attention span using a strict **Stack & Heap** architecture ("AgentProg") and enables multi-agent collaboration via a **Shared Semantic Environment** (SSE).

This module has two primary responsibilities:

1. **State Management (AgentProg):** preventing "Token Bloat" by scoping context to the active task (Stack) vs. long-term storage (Heap).
2. **Swarm Synchronization (SSE):** ensuring multiple agents perceive a shared reality via a federated Knowledge Graph.

## 1. Roadmap (Phase 2: Cognitive Nexus)

- [ ] **Step 1: Scaffolding** (Defining the Ontology & Interfaces)
- [ ] **Step 2: Working Memory** (The Stack & Garbage Collection)
- [ ] **Step 3: The Nexus** (Context Assembly & Budgeting)
- [ ] **Step 4: The Tri-Store** (Zep & Vector DB Integration)
- [ ] **Step 5: Federation** (Shared Semantic Environment)

---

## 2. Architecture: The Tri-Layer Brain

The module is divided into three functional layers, mimicking the hierarchy of biological cognition.

### Layer 1: Working Memory (The Stack)

**Module:** `noetic.knowledge.working`

This layer implements the **AgentProg** architecture. It treats the Context Window like a CPU Call Stack to enforce strict scoping.

- **Memory Frames:** Context is segmented into nested frames.
- **Local Scope:** Logs, scratchpad thoughts, and intermediate tool outputs exist _only_ within the active frame.
- **Garbage Collection:** When a sub-task finishes (Frame Pop), all local "noise" is destroyed. Only the explicit **Return Value** is promoted to the Heap.

### Layer 2: The Tri-Store (The Heap)

**Module:** `noetic.knowledge.store`

The Heap is the "Hard Drive"—infinite, structured, and persistent. It is a **Tri-Store** composed of three specialized memory types:

| Store Type     | Structure         | Backend        | Purpose                                                                                       |
| -------------- | ----------------- | -------------- | --------------------------------------------------------------------------------------------- |
| **Semantic**   | Temporal Graph    | Zep / Graphiti | Stores **Facts** & **Relations** (The "What"). Retrieved via **Community Summaries**.         |
| **Episodic**   | Hierarchical Logs | SQL / Vector   | Stores **Narrative History** (The "When"). Optimized via **AgentFold**.                       |
| **Procedural** | Skill Library     | Vector DB      | Stores **Goal Embeddings** & **Scripts** (The "How"). Solves compounding errors via **Memp**. |

### Layer 3: The Nexus (The Assembler)

**Module:** `noetic.knowledge.nexus`

The Nexus is the CPU. It dynamically assembles the final Prompt Context based on a **Relevance Formula** () and a strict Token Budget.

- **S (Semantic):** Vector similarity.
- **T (Temporal):** Time decay ().
- **G (Graph):** Distance in the Knowledge Graph.
- **I (Salience):** Intrinsic importance score (Safety > Chit-chat).

---

## 2. Shared Semantic Environment (SSE)

To enable Multi-Agent Systems, the Knowledge Engine implements a **Federated Heap**. Agents do not "own" their database; they "mount" a view of the shared reality.

### A. The Ontology (`ontology.py`)

A strict schema definition that all agents must respect. This prevents semantic drift (e.g., Agent A using "Client" vs. Agent B using "Customer"). The Store rejects writes that violate the Ontology.

### B. Graph Scopes (The Mount Protocol)

Agents connect to the Store via a `GraphScope`.

- **GlobalScope:** Full Read/Write access (Root Agent).
- **RestrictedScope:** A "Sandbox" view restricted to specific nodes.

```python
# Parent spawns child with restricted vision
scope = parent.knowledge.create_scope(
    mounts=[
        {"id": "project:123", "access": "RW"},  # Read-Write
        {"id": "global_config", "access": "R"}   # Read-Only
    ]
)

```

### C. The "Blackboard" Sync (Pub/Sub)

We implement **Real-Time State Synchronization**.

1. **Write:** Agent A updates `project:123.status = "DONE"`.
2. **Emit:** The Store emits event `GRAPH_UPDATE:project:123`.
3. **React:** Agent B (subscribed to `project:123`) receives the signal via the Nexus and triggers an immediate **Cognitive Interrupt**.

---

## 3. The "Sleep" Cycle (Offline Maintenance)

To prevent the Tri-Store from becoming a swamp, the engine runs a maintenance cycle during idle periods.

1. **Distillation (Procedural):** Analyzes successful Stack Frames to generate reusable **Skills** (Memp).
2. **Folding (Episodic):** Compresses raw logs into high-level narrative summaries (AgentFold).
3. **Pruning (Semantic):** Merges duplicate nodes and archives low-salience facts using **Leiden Community Detection**.

---

## 4. Implementation Details

### Dependencies

- `getzep` / `graphiti`: For the Temporal Knowledge Graph backend.
- `chromadb` / `qdrant`: For the Vector Store (Procedural/Episodic).
- `networkx`: For in-memory graph traversal and pathfinding.
- `pydantic`: For Ontology enforcement.

### Data Model (`schema.py`)

Implement the **MemoryFrame** for the Stack:

```python
class MemoryFrame(BaseModel):
    id: UUID
    goal: str
    local_vars: List[str]  # The "Noise" to be garbage collected
    return_value: Any      # The "Signal" to be promoted

```

### Logic Requirements

- **Ingestion:** Incoming observations must pass through a **Salience Classifier** (0.0 - 1.0). Only High Salience (>0.5) facts persist to the Heap.
- **Retrieval:** The Nexus must implement the **Relevance Formula**. Do not use simple Cosine Similarity.
- **Garbage Collection:** Ensure that `pop_frame()` creates a "Folded Summary" of the frame before deleting the raw logs.

## 5. Usage

```python
from noetic_knowledge import KnowledgeStore

store = KnowledgeStore(db_url="sqlite:///memory.db")
store.ingest_fact(subject_id=uuid, predicate="likes", object_literal="Pizza")
```

## 6. Directory Structure

```text
noetic_knowledge/
├── __init__.py           # Exports KnowledgeEngine
├── ontology.py           # The Shared Schema Definitions
├── schema.py             # Pydantic Models (MemoryFrame, Fact, Skill)
│
├── working/              # LAYER 1: The Stack
│   ├── stack.py          # MemoryFrame management
│   └── garbage.py        # GC logic
│
├── store/                # LAYER 2: The Heap (Tri-Store)
│   ├── graph.py          # Semantic Store (Zep/Graphiti wrapper)
│   ├── episodic.py       # Event Logs (AgentFold logic)
│   └── procedure.py      # Skill Library (Memp logic)
│
├── nexus/                # LAYER 3: The CPU
│   ├── assembler.py      # Context construction & Relevance weighting
│   └── budget.py         # Token counting & truncation
│
└── sync/                 # SHARED ENVIRONMENT
    ├── scope.py          # GraphScope & Mounting logic
    └── bus.py            # Pub/Sub Event Bus
```