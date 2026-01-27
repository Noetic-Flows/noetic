import sys
import asyncio
from noetic_engine.runtime.mesh import MeshOrchestrator
from noetic_engine.cognition.adk_adapter import ADKAdapter
from noetic_stdlib.agents import N8nAgent, LocalAgent, ADKAgent, AgentDefinition
from noetic_conscience.contracts import AgenticIntentContract

def test_imports():
    print("✅ Imported MeshOrchestrator")
    print("✅ Imported ADKAdapter")
    print("✅ Imported Agents: N8nAgent, LocalAgent, ADKAgent")
    print("✅ Imported AgenticIntentContract")

async def test_instantiation():
    try:
        mesh = MeshOrchestrator()
        print("✅ Instantiated MeshOrchestrator")
        
        definition = AgentDefinition(
            id="test-agent",
            name="Test Agent",
            description="A test agent",
            allowed_tools=["run_command"]
        )
        local_agent = LocalAgent(definition)
        print("✅ Instantiated LocalAgent")
        
        n8n_agent = N8nAgent(definition, webhook_url="http://localhost:5678/webhook/test")
        print("✅ Instantiated N8nAgent")
        
    except Exception as e:
        print(f"❌ Instantiation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_imports()
    asyncio.run(test_instantiation())
