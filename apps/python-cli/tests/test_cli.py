import sys
import os
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# Ensure paths are set up similar to main.py for imports to work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../packages/lang-python")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../packages/knowledge-python")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../packages/engine-python")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../packages/conscience-python")))

# Now we can import main
# We need to mock the StanzaDefinition and Interpreter BEFORE importing main if main uses them at top level?
# No, main imports them.

@pytest.mark.asyncio
async def test_cli_main_execution():
    # Mocking dependencies
    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        # Mock file content
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        # JSON data
        import json
        mock_file.read.return_value = json.dumps({
            "id": "test_stanza",
            "description": "Test",
            "steps": [],
            "context_keys": []
        })
        # Handle json.load reading from the mock
        mock_open.return_value = mock_file
        
        # We also need to patch json.load because it might not work well with MagicMock file object depending on implementation
        # But let's try patching json.load directly or just open.
        
        with patch('json.load') as mock_json_load:
            mock_json_load.return_value = {
                "id": "test_stanza",
                "description": "Test",
                "steps": [],
                "context_keys": []
            }
            
            with patch('noetic_engine.runtime.interpreter.Interpreter') as MockInterpreter:
                instance = MockInterpreter.return_value
                instance.execute_stanza = AsyncMock()
                
                # Import main dynamically to avoid top-level execution issues if any
                import importlib.util
                spec = importlib.util.spec_from_file_location("main", os.path.abspath(os.path.join(os.path.dirname(__file__), "../main.py")))
                main_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main_module)
                
                # Run main
                await main_module.main()
                
                # Assertions
                instance.execute_stanza.assert_called_once()
                mock_json_load.assert_called()
