from typing import Dict, Any
import asyncio
from noetic_conscience.contracts import AgenticIntentContract
from .base import Agent, AgentDefinition

class LocalAgent(Agent):
    """
    An Agent that executes intents on the local machine (CLI/Shell).
    """
    async def execute(self, tool: str, params: Dict[str, Any], contract: AgenticIntentContract) -> Dict[str, Any]:
        """
        Executes a local tool.
        Currently supports:
        - run_command: params { "command": str }
        """
        if tool == "run_command":
            command = params.get("command")
            if not command:
                return {"error": "Missing 'command' parameter", "status": "failed"}

            try:
                # Use asyncio.create_subprocess_shell for async execution
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                return {
                    "status": "success" if process.returncode == 0 else "failed",
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode(),
                    "returncode": process.returncode
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "status": "failed"
                }
        else:
            return {"error": f"Tool '{tool}' not supported by LocalAgent", "status": "failed"}
