import asyncio
import os
import sys

# Add packages to path so we can import them without installing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../packages/lang-python")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../packages/knowledge-python")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../packages/engine-python")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../packages/conscience-python")))

from noetic_lang.core.stanza import StanzaDefinition, Step
from noetic_knowledge.working.stack import MemoryStack
from noetic_engine.cognition.planner import Planner
from noetic_engine.runtime.interpreter import Interpreter
from noetic_engine.skills.registry import SkillRegistry
from noetic_engine.skills.interfaces import Skill

# Mock Executor for CLI
class CLIExecutor:
    async def execute_step(self, step, stack):
        print(f"\n[EXEC] Executing Step: {step.instruction}")
        print(f"       (Skill: {step.skill_id})")
        # Simulate work
        await asyncio.sleep(0.5)
        print("       -> Done.")
        return "OK"

async def main():
    print("--- Noetic CLI Agent ---")
    
    # 1. Initialize Runtime
    stack = MemoryStack()
    registry = SkillRegistry()
    planner = Planner(skill_registry=registry)
    executor = CLIExecutor()
    interpreter = Interpreter(stack, planner, executor)
    
    # 2. Load Stanza (Loading from standard library)
    import json
    stanza_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../packages/stdlib/stanzas/research.noetic"))
    if not os.path.exists(stanza_path):
        print(f"Error: Stanza file not found at {stanza_path}")
        return

    with open(stanza_path, 'r') as f:
        stanza_data = json.load(f)
    
    stanza = StanzaDefinition(**stanza_data)
    
    # 3. Execute
    print(f"Starting Stanza: {stanza.id}")
    await interpreter.execute_stanza(stanza)
    print("\n--- Execution Complete ---")

if __name__ == "__main__":
    asyncio.run(main())