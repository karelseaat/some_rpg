"""Configuration loader for the game."""

import os
import sys
from pathlib import Path
from typing import Dict, Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib

from models import Location, NPC, Item, Quest, Encounter, Danger, World, Skill, Features, GameSettings


def load_game_settings(config_path: str = "game.toml") -> GameSettings:
    """Load game settings from TOML file."""
    if not os.path.exists(config_path):
        print(f"Warning: Game settings file '{config_path}' not found. Using default settings.")
        return GameSettings()

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    settings = GameSettings()

    if "player" in config:
        settings.travel_stamina_cost = config["player"].get("travel_stamina_cost", settings.travel_stamina_cost)

    if "world" in config:
        settings.encounter_chance = config["world"].get("encounter_chance", settings.encounter_chance)
        settings.danger_chance = config["world"].get("danger_chance", settings.danger_chance)
        settings.investigate_treasure_chance = config["world"].get("investigate_treasure_chance", settings.investigate_treasure_chance)

    if "mechanics" in config:
        settings.rest_short_health_gain = config["mechanics"].get("rest_short_health_gain", settings.rest_short_health_gain)
        settings.rest_short_stamina_gain = config["mechanics"].get("rest_short_stamina_gain", settings.rest_short_stamina_gain)
        settings.disarm_trap_dexterity_bonus = config["mechanics"].get("disarm_trap_dexterity_bonus", settings.disarm_trap_dexterity_bonus)
        if "disarm_trap_base_chance" in config["mechanics"]:
            settings.disarm_trap_base_chance.update(config["mechanics"]["disarm_trap_base_chance"])

    if "combat" in config:
        if "difficulty_multipliers" in config["combat"]:
            settings.difficulty_multipliers.update(config["combat"]["difficulty_multipliers"])
        settings.enemy_health_multiplier = config["combat"].get("enemy_health_multiplier", settings.enemy_health_multiplier)
        settings.enemy_attack_multiplier = config["combat"].get("enemy_attack_multiplier", settings.enemy_attack_multiplier)
        settings.enemy_defense_multiplier = config["combat"].get("enemy_defense_multiplier", settings.enemy_defense_multiplier)
        
    return settings


def load_world_config(config_path: str = "world.toml") -> World:
    """Load world configuration from TOML file."""
    
    if not os.path.exists(config_path):
        print(f"Error: Config file '{config_path}' not found")
        sys.exit(1)

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    world = World()
    world.settings = load_game_settings()
    
    # Load world metadata
    if "world" in config:
        world.name = config["world"].get("name", "Unknown World")
        world.start_location = config["world"].get("start_location", "")
        if "start_inventory" in config["world"]:
            for item_id, quantity in config["world"]["start_inventory"].items():
                world.start_inventory[item_id] = quantity

    # Load features
    if "features" in config:
        world.features.npcs_enabled = config["features"].get("npcs_enabled", True)
        world.features.enemies_enabled = config["features"].get("enemies_enabled", True)
        world.features.traders_enabled = config["features"].get("traders_enabled", True)

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
                slot=item_data.get("slot"),
                stats=item_data.get("stats", {})
            )
            world.items[item.id] = item

    # Load skills
    if "skills" in config:
        for skill_data in config["skills"]:
            skill = Skill(
                id=skill_data["id"],
                name=skill_data["name"],
                description=skill_data["description"],
                type=skill_data["type"],
                cost=skill_data["cost"],
                effect=skill_data["effect"],
                value=skill_data["value"],
            )
            world.skills[skill.id] = skill

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
                type=danger_data["type"],
                damage=danger_data.get("damage"),
                escape_difficulty=danger_data.get("escape_difficulty"),
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
