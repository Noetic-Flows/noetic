# North Star Scenario: "The Habit App Idea"

**Goal:** Simulate the execution flow of a complex user intent in the ideal "Software 3.0" Noetic system.

**Input Prompt:**
> "Create a new note for an idea to build an app for helping with users' habits, building better ones and tracking along the way. Scaffold out sections of the note that would be helpful for me to fill in later as I dive into this project."
> *(Sent from **Mobile Hub** on the train; processed by **Desktop Workhorse** at home)*

---

## 1. Sensory Ingestion (ASP & The Gateway)
The User Interface (Web Hub) sends a WebSocket packet via the **Agent Server Protocol (ASP)**.

- **Packet:** `INTENT`
- **Payload:** `{ "content": "Create a new note...", "user_id": "u123" }`
- **Routing:** The Engine recognizes this as a generic `Work Request` and forwards it to the **Cognitive Nexus**.

## 2. The Nexus (Context Assembly)
The **Context Assembler** (The "CPU") wakes up. It needs to construct a prompt for the Agent, but it doesn't just pass the raw user text. It "hydrates" the context using the **Tri-Store**.

### A. Intent Analysis
First, the Nexus extracts the core intent topics:
- **Action:** `Create Note`, `Scaffold Sections`
- **Topic:** `Habit App`, `Habit Tracking`

### B. Accessing the Tri-Store (The Heap)

#### 1. Semantic Query (Facts & Concepts)
*Query:* `hybrid_search("Habit Tracking App requirements features")`
*Retrievals:*
- **Fact:** `(Concept:Gamification, RELATED_TO, Concept:Habit_Tracking)` (Salience: 0.8)
- **Fact:** `(Concept:Atomic_Habits, RELATED_TO, Concept:Habit_Formation)` (Salience: 0.9)
- **Fact:** `(User, HAS_INTEREST, "Clean UI Design")` (Inferred from previous interactions).

#### 2. Episodic Query (Past Experiences)
*Query:* `search_episodes("app idea scaffolding")`
*Retrievals:*
- **Episode 42:** "Last week, we scaffolded a 'To-Do List' app. The user liked the 'Technical Stack' and 'User Personas' sections." (Salience: 0.95)
- **Episode 10:** "User rejected the 'Monetization' section in previous ideation." (Constraints).

#### 3. Procedural Query (Skills)
*Query:* `retrieve_skills("scaffold note")`
*Retrievals:*
- **Skill:** `RecursiveIdeation`
    - **Trigger:** "Create a note for an idea..."
    - **Steps:** `["Identify Core Value Prop", "Suggest 5 Standard Sections", "Draft Content", "Ask for Review"]`

## 3. Working Memory (The Stack)
The Nexus initializes a new **MemoryFrame** on the **AgentProg Stack**.

**Frame ID:** `0xff`
**Task:** `Scaffold Habit Note`
**Context (Budgeted < 8k tokens):**
- **User Tone:** Enthusiastic, Builder-focused.
- **Relevant Facts:** User likes 'Clean UI', interested in 'Atomic Habits'.
- **Relevant Episodes:** "Include 'Tech Stack', Exclude 'Monetization'."
- **Active Skill:** `RecursiveIdeation`.

## 4. Execution (The Agent)
The Agent (LLM) receives this highly curated `System Prompt`. It doesn't have to guess what sections to include; the **Episodic Memory** already told it what the user prefers.

**Agent Reasoning (Running on Workhorse):**
1.  *Thinking:* "Okay, I need to scaffold a note. Based on Episode 42, I should include 'Technical Stack'. Based on semantic associations, I should suggest a section for 'Gamification Mechanics'."
2.  *Safety Check (Conscience):* "Proposing to use `RecursiveIdeation` skill. Cost is negligible. Principle `Frugality` passed."
3.  *Action:* Calls tool `create_note(title="Project: Habit Forge", content=...)`.

## 5. Shadow Action Interruption (The "Human-in-the-Loop")
*Scenario Variant:* If the Agent decided to buy a domain name for "Habit Forge":

1.  **Workhorse:** Generates tool call `buy_domain("habitforge.com")`.
2.  **Conscience:** Helper Principle `FinancialSafety` triggers. "Actions spending money require explicit approval."
3.  **Mobile Hub:** Receives a **Shadow Action Card** notification:
    > "Agent wants to purchase `habitforge.com` ($12.00). Approve?"
4.  **User:** Taps "Approve" (Biometric auth).
5.  **Workhorse:** Executes the purchase.

## 6. Output & Feedback Loop (Optimistic UI)
The Note is created locally on the Workhorse and synced instantly to the Mobile Hub via ASP.

**Content Preview:**
> # Project: Habit Forge
> ## 1. Core Philosophy
> *Scaffolded based on interest in 'Atomic Habits'*
>
> ## 2. Feature Set
> - **Gamification Engine** (Progress bars, streaks)
> - **Analytics Dashboard**
>
> ## 3. Technical Stack
> *To be filled...*

## 6. Memory Consolidation (The Aftermath)
Once the task is done, the system performs **Sleep Cycle** operations:

1.  **Episodic:** `ingest_episode_summary("Created scaffolding for 'Habit Forge' app. User accepted the 'Gamification' section.")`
2.  **Semantic:** New Fact `(Project:Habit_Forge, IS_A, App_Idea)`.
3.  **Procedural:** The `RecursiveIdeation` skill success rate is incremented because the user didn't ask for a rewrite.

---

## Summary of Data Flow
| Component     | Function     | Data In                      | Data Out                  |
| :------------ | :----------- | :--------------------------- | :------------------------ |
| **ASP**       | **Ingest**   | Raw User Text                | Intent Object             |
| **Nexus**     | **Assemble** | Intent                       | Context Window (Hydrated) |
| **Tri-Store** | **Recall**   | Topics ("Habit", "Scaffold") | Facts, Episodes, Skills   |
| **Stack**     | **Focus**    | Context                      | Active Frame              |
| **Agent**     | **Act**      | Active Frame                 | Artifact (Note)           |
| **Store**     | **Learn**    | Outcome                      | New Facts/Episodes        |
