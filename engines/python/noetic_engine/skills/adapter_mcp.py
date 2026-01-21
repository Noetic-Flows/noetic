import asyncio
import logging
from typing import Dict, Any, Optional
from .interfaces import Skill, SkillResult, SkillContext

logger = logging.getLogger(__name__)

# Try importing httpx for async HTTP
try:
    import httpx
except ImportError:
    httpx = None

class McpSkillAdapter(Skill):
    """
    Adapts a remote MCP Tool to the Noetic Skill interface.
    """
    def __init__(self, server_url: str, tool_name: str, tool_description: str, input_schema: Dict[str, Any]):
        self.server_url = server_url
        self._tool_name = tool_name
        self._description = tool_description
        self._schema = input_schema

    @property
    def id(self) -> str:
        return f"mcp.{self._tool_name}"

    @property
    def description(self) -> str:
        return self._description

    @property
    def schema(self) -> Dict[str, Any]:
        return self._schema

    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """
        Forwards the execution request to the MCP server via JSON-RPC.
        """
        if httpx is None:
            return SkillResult(
                success=False, 
                error="MCP Adapter requires 'httpx' library.",
                cost=0.0
            )

        # JSON-RPC 2.0 Request
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": self._tool_name,
                "arguments": kwargs
            },
            "id": 1
        }

        try:
            async with httpx.AsyncClient() as client:
                # We assume the MCP server accepts POST requests for RPC at the root or /jsonrpc
                # The MCP spec uses SSE for transport usually, but simple HTTP POST is common for simple servers.
                # If SSE is required, this needs a much more complex implementation (sse_client).
                # For this adapter, we assume a simple HTTP endpoint for now.
                
                resp = await client.post(self.server_url, json=payload, timeout=30.0)
                resp.raise_for_status()
                
                rpc_response = resp.json()
                
                if "error" in rpc_response:
                    return SkillResult(
                        success=False,
                        error=f"MCP Error: {rpc_response['error'].get('message')}",
                        cost=0.0
                    )
                
                result_content = rpc_response.get("result", {})
                
                # Extract text/content from result
                # MCP 'tools/call' result structure: { "content": [ { "type": "text", "text": "..." } ] }
                content = result_content.get("content", [])
                text_output = ""
                for item in content:
                    if item.get("type") == "text":
                        text_output += item.get("text", "")
                
                return SkillResult(
                    success=True,
                    data=text_output if text_output else result_content,
                    cost=1.0 # Default cost
                )

        except Exception as e:
            logger.error(f"MCP Call Failed: {e}")
            return SkillResult(success=False, error=str(e), cost=0.0)
