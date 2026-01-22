# Contributing to the Noetic Ecosystem

Welcome to the **Noetic Monorepo**! We are building the operating system for **Software 3.0**, and we're thrilled you want to help.

Because this is a **Federated Monorepo** with a **Layered SDK Architecture**, it works differently than a standard Python project. This guide will help you navigate the layers and make your first contribution effectively.

---

## 1. Orientation: Where do I fit in?

The repository is organized by **Abstraction Layer**. Depending on your skills and interests, you will work in different folders:

| If you want to...                                                  | You belong in...                                                                  | Layer                         |
| :----------------------------------------------------------------- | :-------------------------------------------------------------------------------- | :---------------------------- |
| **Define the Protocol** (Edit JSON Schemas, change the spec)       | `packages/spec`                                                                   | **Layer 1: The Constitution** |
| **Build Reusable Flows** (Create Stanzas, Agents, Knowledge Packs) | `packages/stdlib`                                                                 | **Layer 2: The Content**      |
| **Update Data Models** (Edit Pydantic classes, Python bindings)    | `packages/lang-python`                                                            | **Layer 3: The SDK**          |
| **Improve Core Logic** (Fix the Planner, optimize Memory, Safety)  | `packages/engine-python` `packages/knowledge-python` `packages/conscience-python` | **Layer 4 & 5: The Runtime**  |
| **Build Tools** (CLI features, VSCode Extension)                   | `apps/`                                                                           | **Consumers**                 |

---

## 2. Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js & NPM** (For Schema validation)
- **VS Code** (Recommended, for Workspace support)

### Installation

1. **Clone the Repository:**

   ```bash
   git clone [https://github.com/noetic-flows/noetic.git](https://github.com/noetic-flows/noetic.git)
   cd noetic
   ```

2. **Set up the Virtual Environment:**
   We recommend using one venv for the whole monorepo to simplify local linking.

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

3. **Install Dependencies (Editable Mode):**
   We install the packages in "Editable Mode" (`-e`) so changes in the library are immediately reflected in the engine.

   ```bash
   # Install the Logic Layers
   pip install -e packages/lang-python
   pip install -e packages/knowledge-python
   pip install -e packages/stage-python
   pip install -e packages/conscience-python
   pip install -e packages/engine-python

   # Install the App Dependencies
   pip install -r apps/python-cli/requirements.txt
   ```

4. **Open the Workspace:**
   Open the file `.vscode/noetic.code-workspace` in VS Code. This is crucial—it configures the IDE to treat each folder in `packages/` as a distinct root, enabling proper IntelliSense and navigation.

---

## 3. How to Contribute

### Scenario A: "I want to add a field to the Stanza definition."

_This touches the Protocol._

1. **Modify the Python Model:** Edit `packages/lang-python/noetic_lang/core/stanza.py`. Add your field to the Pydantic model.
2. **Generate the Spec:** Run the generation script to update the JSON Schemas.

   ```bash
   python packages/lang-python/scripts/generate_schemas.py
   ```

3. **Verify:** Check `packages/spec/schemas/stanza.json` to see your change reflected.
4. **Update the Engine:** Update `packages/engine-python` to handle this new field in the runtime logic.

### Scenario B: "I want to add a new Standard Stanza (e.g., 'Brainstorming')."

_This touches the Standard Library._

1. **Create the File:** Create `packages/stdlib/stanzas/brainstorm.noetic`.
2. **Define the Flow:** Write the JSON definition using existing Skills.
3. **Test it:** Run it using the CLI.

   ```bash
   python apps/python-cli/main.py --codex packages/stdlib/stanzas/brainstorm.noetic
   ```

### Scenario C: "I want to fix a bug in the Planner."

_This touches the Engine Logic._

1. **Locate the Logic:** Go to `packages/engine-python/noetic_engine/cognition/planner.py`.
2. **Write a Failing Test:** Create a test case in `packages/engine-python/tests/test_planner.py` that reproduces the bug.
3. **Fix & Verify:** Edit the code until the test passes.

---

## 4. Development Standards

### Test-Driven Development (TDD)

We follow TDD strictly.

- **Rule:** No logic code is written without a corresponding test.
- **Process:** Write Test (Red) $\rightarrow$ Write Code (Green) $\rightarrow$ Refactor.
- **Running Tests:**

  ```bash
  pytest packages/engine-python/tests
  pytest packages/knowledge-python/tests
  ```

### Coding Style

- **Type Hints:** All function signatures must be typed.
- **Async/Await:** All I/O (Database, LLM, Network) must be async.
- **Pydantic V2:** Use `model_validate`, not `parse_obj`.
- **Docstrings:** Use Google-style docstrings.

### Architecture Rules

- **One-Way Dependencies:** The `engine` can import `knowledge`, but `knowledge` **must never** import `engine`.
- **No Logic in Spec:** `noetic-lang` must remain pure data definitions.

---

## 5. Pull Request Process

1. **Feature Branch:** Create a branch for your work (`feature/new-stanza` or `fix/memory-leak`).
2. **Self-Review:** Ensure you have added tests and updated the relevant READMEs.
3. **Schema Check:** If you changed data models, ensure you ran `generate_schemas.py` and committed the updated JSON spec.
4. **Submit PR:** Link the issue you are solving.

Thank you for building the future of software with us!
