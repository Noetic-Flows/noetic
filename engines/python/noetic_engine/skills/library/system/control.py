import asyncio
import time
from typing import Any, Dict
from noetic_engine.skills.interfaces import Skill, SkillResult, SkillContext

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

class TerminateSkill(Skill):
    id = "skill.system.terminate"
    description = "Signals the Noetic Engine to stop."
    schema = {
        "type": "object",
        "properties": {
            "reason": {"type": "string", "default": "Agent requested termination."}
        },
        "required": []
    }

    async def execute(self, context: SkillContext, reason: str = "Agent requested termination.", **kwargs) -> SkillResult:
        start = time.monotonic()
        if context.engine:
            await context.engine.stop()
            print(f"Agent {context.agent_id} requested engine termination: {reason}")
            elapsed = (time.monotonic() - start) * 1000
            return SkillResult(
                success=True,
                data={"reason": reason},
                cost=0.0,
                latency_ms=int(elapsed)
            )
        else:
            elapsed = (time.monotonic() - start) * 1000
            return SkillResult(
                success=False,
                error="Engine context not available to terminate.",
                cost=0.0,
                latency_ms=int(elapsed)
            )


class PlaceholderSkill(Skill):
    id = "skill.placeholder"
    description = "A placeholder for dynamically loaded skills."
    schema = {}

    def __init__(self, id: str, description: str, **kwargs):
        self.id = id
        self.description = description
        self.metadata = kwargs

    @property
    def schema(self) -> Dict[str, Any]:
        # Placeholder skills don't have a fixed schema, return an empty one
        return {}

    async def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        # Just return success for now
        return SkillResult(
            success=True,
            data={"status": "placeholder_executed", "args": kwargs},
            cost=0.0
        )