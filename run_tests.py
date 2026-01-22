import sys
import os
import subprocess

# Add the engine source to the path
engine_path = os.path.abspath("packages/engine-python")
sys.path.insert(0, engine_path)

print(f"Running tests with engine path: {engine_path}")

# Run pytest using the virtual environment's python
venv_python = os.path.abspath(".venv311/bin/python")
if not os.path.exists(venv_python):
    venv_python = "python3" # Fallback

cmd = [venv_python, "-m", "pytest", "packages/engine-python/tests", "-v"]
exit_code = subprocess.call(cmd)
sys.exit(exit_code)
