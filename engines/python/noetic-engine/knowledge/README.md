# Noetic Memory (`noetic.knowledge`)

TODO: Update this design to implement a Shared Semantic Environment.

## Overview

The `noetic.knowledge` module is the **Single Source of Truth** (The Blackboard) for the Noetic Engine.

In the Noetic architecture, the Engine (Core) is transient and stateless, while the Memory is persistent and stateful. If the Engine crashes or restarts, it should be able to resume execution exactly where it left off by hydrating from `noetic.knowledge`.

This module implements a **Temporal Knowledge Graph** inspired by [Zep](https://getzep.com/). It combines the structured precision of a graph database (NetworkX) with the semantic flexibility of a vector store, all underpinned by a rigorous timeline. This temporal knowledge graph enables properly intelligent agentic systems to utilize a "living document" of facts, or a "world model", and are also auditable (with time travel capabilities).

Crucial: The Agents must use a Skill (MCP) for I/O with Knowledge.

---

## 1. The "Blackboard" Philosophy

The **Blackboard Pattern** dictates that modules do not talk to each other directly; they talk to the Blackboard.

- **Reflex System:** Writes raw `Events` to the Blackboard (e.g., "User clicked button").
- **Cognitive System:** Reads the `WorldState` from the Blackboard to make plans.
- **Surface (UI):** Observes the Blackboard to render the current state.

### The `WorldState` Snapshot

This Knowledge module provides a "Hot" in-memory object representing the exact state of the simulation at the current tick.

```python
class WorldState(BaseModel):
    tick: int                      # Current frame count
    entities: Dict[UUID, Entity]   # Active objects (Plants, User, etc.)
    facts: List[Fact]              # Current true relations
    event_queue: List[Event]       # Unprocessed inputs
    active_goals: List[Goal]       # What the agents are trying to do

```

---

## 2. The Zep-Inspired Temporal Graph

Standard Knowledge Graphs are static: `(User) -[LOCATED_AT]-> (Home)`.
A **Temporal Knowledge Graph** (like Zep) adds the dimension of time: `(User) -[LOCATED_AT]-> (Home) [Valid: 09:00 - 17:00]`.

This allows the Agent to understand **Context Change** and **Episodic Memory**.

### A. The Graph Structure (`(Subject, Predicate, Object)`)

We use a directed graph where:

- **Nodes** are `Entities` (The Noun).
- **Edges** are `Facts` (The Relation).

### B. The Temporal Dimension

Every Fact (Edge) has a lifecycle.

- `created_at`: When the system learned this.
- `valid_from`: When this fact became true in the "simulation".
- `valid_until`: When this fact ceased to be true (making it "History").

**Why this matters:**
If the user asks "Where was I yesterday?", the system queries the graph with a time filter `t = now - 24h`. A standard graph would only know where the user is _now_.

### C. The Semantic Layer (Vectors)

Every Node and Edge is embedded into a Vector Store.

- **Fact:** "The plant is wilting." `[0.12, -0.98, ...]`
- **Query:** "Is the garden healthy?"
- **Search:** The vector search finds "The plant is wilting" because "wilting" is semantically opposite to "healthy," even if the keywords don't match.

---

## 3. Architecture: The "Hybrid Store"

To achieve the Zep-inspired Temporal Graph functionality, we use a hybrid backend strategy:

| Component            | Technology                           | Responsibility                                                                                                |
| -------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| **Relational Store** | **SQLAlchemy** (SQLite / PostgreSQL) | Stores the Graph Topology (Nodes/Edges), Transactions, and Time Ranges. Ensures strict consistency.           |
| **Vector Store**     | **ChromaDB** (Persistent Mode)       | Stores the Semantic Embeddings of Entities and Facts. Enables "fuzzy" retrieval.                              |
| **Graph Cache**      | **NetworkX** (In-Memory)             | A lightweight graph loaded on startup for fast "Shortest Path" and "Neighborhood" algorithms during planning. |

### The Data Flow

1. **Write:** `ingest()` writes to SQL (Relation) AND ChromaDB (Vector) in a single atomic-like operation.
2. **Read (State):** `get_world_state()` queries SQL to hydrate the current snapshot.
3. **Read (Search):** `search()` queries ChromaDB for candidates, then hydrates details from SQL.

---

## 4. Data Model (`schema.py`)

We map our Pydantic models to SQL tables using SQLAlchemy ORM.

### A. Tables (Relational)

**1. `entities**`

- `id` (UUID, PK)
- `type` (String) - e.g., "Plant", "User"
- `attributes` (JSONB) - e.g., `{"species": "Fern"}`
- `created_at` (DateTime)
- `updated_at` (DateTime)

**2. `facts` (The Edges)**

- `id` (UUID, PK)
- `subject_id` (UUID, FK -> entities.id)
- `predicate` (String) - e.g., "needs_water"
- `object_entity_id` (UUID, FK -> entities.id, Nullable)
- `object_literal` (Text, Nullable)
- `confidence` (Float)
- **Temporal Columns:**
- `valid_from` (DateTime)
- `valid_until` (DateTime, Nullable) - NULL means "Currently True"

**3. `tags` & `entity_tags**`

- Standard Many-to-Many relationship table to link Entities to System Tags (UUIDs).

### B. Vectors (Semantic)

**Collection: `facts**`

- **Embedding:** `sentence-transformers/all-MiniLM-L6-v2`
- **Document:** Natural language representation (e.g., "The User watered the Fern").
- **Metadata:** `{"subject_id": "...", "predicate": "...", "valid_until": "None"}`

---

## 5. Core Logic Requirements

### 1. Ingestion & Temporal Resolution

When `ingest_fact(subject, predicate, object)` is called:

1. **Query SQL:** Is there an _existing, active_ fact with this (Subject, Predicate, Object)?

- **If Yes:** Update `valid_from` or `confidence` if needed. Do not create duplicates.
- **If No:**
- Check for **Contradictions** (e.g., existing fact is `status=dry`, new fact is `status=wet`).
- If contradiction found: Update the _old_ fact's `valid_until` to `NOW()`. (This preserves history).
- Insert the _new_ fact with `valid_from = NOW()` and `valid_until = NULL`.

1. **Update Vector:** Generate embedding for the new fact and upsert to ChromaDB.

### 2. Time Travel Querying

The `get_world_state(snapshot_time: datetime = NOW)` method must respect the timeline.

- **SQL Query:**

```sql
SELECT * FROM facts
WHERE valid_from <= :snapshot_time
AND (valid_until IS NULL OR valid_until > :snapshot_time)

```

- This allows the Engine to "rewind" the world state to debug past decisions.

### 3. Atomic Transactions

Implement a Context Manager for writes to ensure SQL and Vector stores stay in sync.

```python
with knowledge_store.transaction() as tx:
    tx.add_fact(...)
    tx.update_entity(...)
# Commit happens here. If SQL fails, Vector write is skipped.

```

---

## 6. Implementation Directives (For AI Assistant)

### Dependencies

Use the following production-grade libraries:

- `sqlalchemy`: For ORM and SQL management.
- `alembic`: For database migrations (essential for schema evolution).
- `chromadb`: For vector storage.
- `pydantic`: For data validation.

### Initialization (`__init__.py`)

- The module must check for the existence of `noetic.db` (SQLite) and `noetic_chroma/` (Vector Data).
- If missing, it should auto-initialize the schema using Alembic.
- It must pre-seed **System Tags** (defined in the Protocol) to ensure UUID consistency.

### Performance

- **Indexing:** Ensure SQL indices on `subject_id`, `predicate`, and `valid_until` for fast lookups.
- **Lazy Loading:** Do not load the entire history into NetworkX. Only load _active_ facts (`valid_until IS NULL`) into the in-memory graph for planning.

### Search Implementation

Implement `hybrid_search(query)`:

1. **Chroma:** `results = collection.query(query_texts=[query])`
2. **Hydration:** Extract `fact_ids` from Chroma results.
3. **SQL:** `SELECT * FROM facts WHERE id IN (fact_ids) AND valid_until IS NULL`.
4. **Return:** List of Pydantic `Fact` objects.

---

## 7. Directory Structure

```text
../knowledge
├── __init__.py         # Exports KnowledgeStore
├── interfaces.py       # Abstract Base Class
├── schema.py           # Pydantic Models (API Layer)
├── models.py           # SQLAlchemy Models (DB Layer)
├── store.py            # Main Logic (The Controller)
├── graph.py            # NetworkX wrapper for pathfinding
├── vector.py           # ChromaDB wrapper
└── utils/
    └── time.py         # Temporal helpers

```
