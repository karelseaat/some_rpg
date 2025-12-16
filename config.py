"""Configuration loader for the game."""

import os
import sys
from pathlib import Path
from typing import Dict, Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib

from models import Location, NPC, Item, Quest, Encounter, Danger, World


def load_world_config(config_path: str = "world.toml") -> World:
    """Load world configuration from TOML file."""
    
    if not os.path.exists(config_path):
        print(f"Error: Config file '{config_path}' not found")
        sys.exit(1)

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    world = World()
    
    # Load world metadata
    if "world" in config:
        world.name = config["world"].get("name", "Unknown World")
        world.start_location = config["world"].get("start_location", "")

    # Load items
    if "items" in config:
        for item_data in config["items"]:
            item = Item(
                id=item_data["id"],
                name=item_data["name"],
                description=item_data["description"],
                type=item_data["type"],
                value=item_data["value"],
                effect=item_data["effect"],
                amount=item_data.get("amount", 1),
            )
            world.items[item.id] = item

    # Load NPCs
    if "npcs" in config:
        for npc_data in config["npcs"]:
            npc = NPC(
                id=npc_data["id"],
                name=npc_data["name"],
                description=npc_data["description"],
                dialogue=npc_data["dialogue"],
                location_id="",  # Will be set from locations
                shop=npc_data.get("shop", False),
                offers_quest=npc_data.get("offers_quest", False),
                inventory=npc_data.get("inventory", []),
            )
            world.npcs[npc.id] = npc

    # Load encounters
    if "encounters" in config:
        for enc_data in config["encounters"]:
            encounter = Encounter(
                id=enc_data["id"],
                name=enc_data["name"],
                description=enc_data["description"],
                type=enc_data["type"],
                difficulty=enc_data["difficulty"],
                reward=enc_data["reward"],
            )
            world.encounters[encounter.id] = encounter

    # Load dangers
    if "dangers" in config:
        for danger_data in config["dangers"]:
            danger = Danger(
                id=danger_data["id"],
                name=danger_data["name"],
                description=danger_data["description"],
                damage=danger_data["damage"],
                escape_difficulty=danger_data["escape_difficulty"],
            )
            world.dangers[danger.id] = danger

    # Load locations
    if "locations" in config:
        for loc_data in config["locations"]:
            location = Location(
                id=loc_data["id"],
                name=loc_data["name"],
                description=loc_data["description"],
                type=loc_data["type"],
                x=loc_data.get("x", 0),
                y=loc_data.get("y", 0),
                npcs=loc_data.get("npcs", []),
                encounters=loc_data.get("encounters", []),
                dangers=loc_data.get("dangers", []),
                treasure=loc_data.get("treasure", []),
            )
            world.locations[location.id] = location
            
            # Update NPC locations
            for npc_id in location.npcs:
                if npc_id in world.npcs:
                    world.npcs[npc_id].location_id = location.id

    # Load quests
    if "quests" in config:
        for quest_data in config["quests"]:
            quest = Quest(
                id=quest_data["id"],
                name=quest_data["name"],
                description=quest_data["description"],
                giver=quest_data["giver"],
                location=quest_data["location"],
                objectives=quest_data["objectives"],
                reward=quest_data["reward"],
                reward_item=quest_data.get("reward_item"),
                completed=False,
            )
            world.quests[quest.id] = quest

    return world
