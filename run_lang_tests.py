import sys
import os
import subprocess

# Add the lang-python source to the path
lang_path = os.path.abspath("packages/lang-python")
sys.path.insert(0, lang_path)

print(f"Running tests with lang-python path: {lang_path}")

# Run pytest using the virtual environment's python
venv_python = os.path.abspath(".venv311/bin/python")
if not os.path.exists(venv_python):
    venv_python = "python3" # Fallback

cmd = [venv_python, "-m", "pytest", "packages/lang-python/tests", "-v"]
exit_code = subprocess.call(cmd)
sys.exit(exit_code)
