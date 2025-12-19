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
        default="default.toml",
        help="Name of the world config file in the 'worlds' directory (default: default.toml)"
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
    parser.add_argument(
        "--list-features",
        action="store_true",
        help="List all available features and their status"
    )
    parser.add_argument(
        "--list-worlds",
        action="store_true",
        help="List all available worlds"
    )

    args = parser.parse_args()

    if args.list_worlds:
        print("\nAvailable Worlds:")
        import os
        for world_file in os.listdir("worlds"):
            if world_file.endswith(".toml"):
                print(f"  - {world_file}")
        sys.exit(0)

    config_path = f"worlds/{args.config}"

    print(f"Loading world configuration from {config_path}...")
    world = load_world_config(config_path)
    
    if args.list_features:
        print("\nAvailable Features:")
        for feature, enabled in world.features.__dict__.items():
            status = "enabled" if enabled else "disabled"
            print(f"  - {feature}: {status}")
        sys.exit(0)

    print(f"Loaded world: {world.name}")
    print(f"Locations: {len(world.locations)}")
    
    npcs_status = f"{len(world.npcs)}" if world.features.npcs_enabled else "0 (disabled)"
    enemies_status = f"{len(world.encounters)} (enabled)" if world.features.enemies_enabled else "0 (disabled)"
    traders_status = "enabled" if world.features.traders_enabled else "disabled"
    
    print(f"NPCs: {npcs_status}")
    print(f"Enemies: {enemies_status}")
    print(f"Traders: {traders_status}")
    
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
