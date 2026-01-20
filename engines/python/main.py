import argparse
import asyncio
import sys
from noetic-engine.runtime import NoeticEngine

def main():
    parser = argparse.ArgumentParser(description="Noetic Engine Reference Implementation")
    parser.add_argument("--codex", type=str, required=True, help="Path to the .noetic Codex file")
    args = parser.parse_args()

    print(f"Loading Codex from: {args.codex}")
    
    # Initialize Engine
    engine = NoeticEngine()
    
    # TODO: Load Codex into Engine
    # engine.load_codex(args.codex)
    
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        asyncio.run(engine.stop())
        sys.exit(0)

if __name__ == "__main__":
    main()
