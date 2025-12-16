#!/usr/bin/env python3
"""Main entry point for SomeRPG."""

import sys
import argparse
from config import load_world_config
from server import run_server, save_all_games
from database import create_db_and_tables


def main():
    """Main entry point."""
    
    print("Initializing database...")
    create_db_and_tables()
    
    parser = argparse.ArgumentParser(
        description="SomeRPG - Text-based multiplayer RPG"
    )
    parser.add_argument(
        "--config",
        default="world.toml",
        help="Path to world config file (default: world.toml)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=2300,
        help="Port to run server on (default: 2300)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )

    args = parser.parse_args()

    print("Loading world configuration...")
    world = load_world_config(args.config)
    print(f"Loaded world: {world.name}")
    print(f"Locations: {len(world.locations)}")
    print(f"NPCs: {len(world.npcs)}")
    print(f"Items: {len(world.items)}")
    print(f"Quests: {len(world.quests)}")

    try:
        run_server(world, port=args.port)
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        save_all_games()
        sys.exit(0)


if __name__ == "__main__":
    main()
