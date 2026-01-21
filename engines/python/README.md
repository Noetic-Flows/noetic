# Noetic Engine (Python)

The reference implementation of the Noetic Engine in Python.

## Structure

- `noetic-engine/`: Core package source code.
  - `knowledge/`: Knowledge Graph and World State management (System 1 memory).
  - `orchestration/`: Planning, Agents, and Principles (System 2).
  - `runtime/`: Main loops (Reflex and Cognitive), Engine lifecycle.
  - `skills/`: Tool definitions and registry.
  - `canvas/`: UI component definitions and rendering.
  - `loader.py`: Codex (.noetic) file parser.

## Development

This project follows Test-Driven Development.

### Running Tests

Run the full test suite with:

```bash
python run_tests.py
```

Or using pytest directly:

```bash
pytest engines/python/tests
```