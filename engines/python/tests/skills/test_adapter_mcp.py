import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from noetic_engine.skills.adapter_mcp import McpSkillAdapter
from noetic_engine.skills.interfaces import SkillResult, SkillContext

@pytest.mark.asyncio
async def test_mcp_adapter_success():
    # Mock httpx
    with patch("noetic_engine.skills.adapter_mcp.httpx") as mock_httpx:
        # Setup Mock Client
        mock_client = AsyncMock()
        mock_response = MagicMock() # Use MagicMock for response
        mock_response.json.return_value = {
            "result": {
                "content": [{"type": "text", "text": "Hello MCP"}]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_client.post.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        
        mock_httpx.AsyncClient.return_value = mock_client
        
        adapter = McpSkillAdapter(
            server_url="http://localhost:8000",
            tool_name="test_tool",
            tool_description="A test tool",
            input_schema={}
        )
        
        ctx = SkillContext(agent_id="test", store=None)
        result = await adapter.execute(ctx, arg1="value")
        
        assert result.success is True
        assert result.data == "Hello MCP"

@pytest.mark.asyncio
async def test_mcp_adapter_no_httpx():
    # Simulate missing httpx
    with patch("noetic_engine.skills.adapter_mcp.httpx", new=None):
        adapter = McpSkillAdapter("url", "tool", "desc", {})
        ctx = SkillContext(agent_id="test", store=None)
        result = await adapter.execute(ctx)
        
        assert result.success is False
        assert "httpx" in result.error
