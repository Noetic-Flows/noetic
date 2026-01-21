import sys
import os
import pytest

# Add the engine source to the path
engine_path = os.path.abspath("engines/python")
sys.path.insert(0, engine_path)

print(f"Running tests with path: {sys.path[0]}")

# Run pytest programmatically
# We look for tests in engines/python/tests
exit_code = pytest.main(["engines/python/tests", "-v"])
sys.exit(exit_code)
