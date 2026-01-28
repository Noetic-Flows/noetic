# Master Task List

## Vision
To build **Noetic**, a "Software 3.0" operating system where users define intents ("Flows") and AI Agents orchestrate the execution using a rigorous architecture of Stanzas, Memory (Stack/Heap), and Safety (Conscience).

## Phase 1: The Core Engine (Current Focus)
- [/] **Federated Monorepo Setup**
    - [x] Structure (`packages/`, `apps/`)
    - [x] Core dependencies (`engine-python`, `lang-python`)
- [/] **Noetic Engine (`packages/engine-python`)**
    - [x] Runtime Loop
    - [x] FastUI Integration
    - [/] **Agent Server Protocol (ASP)**
        - [x] WebSocket Endpoint (`/ws/asp`)
        - [ ] Message Validation & Error Handling
        - [ ] Connection Heartbeats
- [/] **The Clients**
    - [x] Python CLI (`apps/python-cli`)
    - [/] **Web Hub (`apps/web-hub`)**
        - [x] Next.js Scaffold
        - [ ] ASP Client Implementation
        - [ ] Reflex/FastUI Rendering Component

## Phase 2: Cognition & Memory (Cognitive Nexus)
- [ ] **Layer 1: Working Memory (The Stack)**
    - [ ] `packages/knowledge-python`: Implement `MemoryFrame`
    - [ ] `packages/knowledge-python`: Implement Garbage Collection (Frame Pop)
- [ ] Implement Layer 2: Tri-Store (Heap) <!-- id: 16 -->
    - [ ] Unify Schema (`noetic_knowledge/schema.py`) <!-- id: 17 -->
    - [ ] Update DB Models (`store/models.py`) <!-- id: 18 -->
    - [ ] Refactor `store/store.py` to use unified Schema <!-- id: 19 -->
    - [ ] Implement Procedural Memory (Skills) <!-- id: 20 -->
    - [ ] Verify Tri-Store Operations <!-- id: 21 -->
- [ ] **Layer 3: The Nexus (The Assembler)**
    - [ ] Implement Relevance Formula ($R = S \cdot T \cdot G \cdot I$)
    - [ ] Implement Token Budgeting
- [ ] **Shared Semantic Environment (SSE)**
    - [ ] Define Ontology (`ontology.py`)
    - [ ] Implement Graph Scopes (`GraphScope`)
    - [ ] Implement Pub/Sub Bus

## Phase 3: Safety & Interface
- [ ] **Conscience Module**
    - [ ] Principle Evaluation Engine
    - [ ] Cost Simulation
- [ ] **Noetic Stage**
    - [ ] Generative UI Protocol
    - [ ] Voice/Avatar Integration

## Phase 4: Ecosystem
- [ ] **Standard Library (`stdlib`)**
    - [ ] Research Stanza
    - [ ] Coding Stanza
- [ ] **Marketplace**
    - [ ] `.noetic` Codex Export/Import
