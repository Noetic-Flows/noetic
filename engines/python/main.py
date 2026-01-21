import argparse
import asyncio
import sys
import logging
from noetic_engine.runtime import NoeticEngine
from noetic_engine.loader import NoeticLoader

logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="Noetic Engine Reference Implementation")
    parser.add_argument("--codex", type=str, required=True, help="Path to the .noetic Codex file")
    args = parser.parse_args()

    print(f"Loading Codex from: {args.codex}")
    
    # Initialize Engine
    engine = NoeticEngine()
    
    # Load Codex
    loader = NoeticLoader()
    loader.load(engine, args.codex)
    
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        asyncio.run(engine.stop())
        sys.exit(0)

if __name__ == "__main__":
    main()