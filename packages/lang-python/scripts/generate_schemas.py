import json
import os
import shutil
from typing import Type
from pydantic import BaseModel

from noetic_lang.core import (
    AgentDefinition,
    FlowDefinition,
    StanzaDefinition,
    IdentityContext,
    ACL,
    AgenticIntentContract
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../spec")

def clean_output_dir(directory: str):
    """Ensure a clean output directory exists."""
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

def export_schema(model: Type[BaseModel], filename: str):
    """Export Pydantic model to JSON schema file."""
    schema = model.model_json_schema()
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "w") as f:
        json.dump(schema, f, indent=2)
    print(f"Generated: {filepath}")

def main():
    print(f"Generating schemas to {OUTPUT_DIR}...")
    clean_output_dir(OUTPUT_DIR)
    
    # Core Protocol Models
    export_schema(FlowDefinition, "flow_definition.json")
    export_schema(StanzaDefinition, "stanza_definition.json")
    export_schema(AgentDefinition, "agent_definition.json")
    
    # Security Models
    export_schema(IdentityContext, "identity_context.json")
    export_schema(ACL, "acl.json")
    export_schema(AgenticIntentContract, "agentic_intent_contract.json")
    
    print("Schema generation complete.")

if __name__ == "__main__":
    main()
