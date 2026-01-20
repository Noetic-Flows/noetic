import asyncio
import time
from typing import Any
from ...interfaces import Skill, SkillResult, SkillContext

class WaitSkill(Skill):
    id = "skill.system.wait"
    description = "Pauses execution for a specified number of seconds."
    schema = {
        "type": "object",
        "properties": {
            "seconds": {"type": "number", "minimum": 0}
        },
        "required": ["seconds"]
    }

    async def execute(self, context: SkillContext, seconds: float = 1.0, **kwargs) -> SkillResult:
        start = time.monotonic()
        await asyncio.sleep(seconds)
        elapsed = (time.monotonic() - start) * 1000
        return SkillResult(
            success=True,
            data={"waited": seconds},
            cost=0.0,
            latency_ms=int(elapsed)
        )

class LogSkill(Skill):
    id = "skill.debug.log"
    description = "Logs a message to the system console."
    schema = {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
            "level": {"type": "string", "enum": ["info", "warning", "error"]}
        },
        "required": ["message"]
    }

    async def execute(self, context: SkillContext, message: str, level: str = "info", **kwargs) -> SkillResult:
        start = time.monotonic()
        print(f"[{level.upper()}] Agent {context.agent_id}: {message}")
        elapsed = (time.monotonic() - start) * 1000
        return SkillResult(
            success=True,
            data=None,
            cost=0.0,
            latency_ms=int(elapsed)
        )
