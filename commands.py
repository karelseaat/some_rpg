"""
Command handlers for the game.
"""
from typing import List, Dict, Callable, Coroutine
from game import Game
from color import info, error, success, warning

# Command handler function signature
CommandHandler = Callable[[Game, List[str]], Coroutine[None, None, str]]

async def handle_help(game: Game, args: List[str]) -> str:
    """Handles the 'help' command."""
    help_text = """
Commands:
  look         - Look around current location
  travel <dir> - Travel in a direction (north, south, east, west)
  inventory    - Check your inventory and equipment
  use <item>   - Use an item from your inventory
  equip <item> - Equip an item from your inventory
  unequip <slot> - Unequip an item from a slot
  skills       - View your skills
  learn <skill> - Learn a new skill using skill points
  attack       - Attack the current enemy in combat
  cast <skill> - Cast a skill in combat
  flee         - Flee from combat
  rest <type>  - Rest (short/long)
  talk <npc>   - Talk to an NPC
  buy <npc> <item> - Buy an item from an NPC
  quest        - Manage quests (list, accept)
  map          - Show a map of traveled areas
  investigate  - Search for treasure and traps
  status       - Show character status
  spend <stat> <points> - Spend attribute points
  disarm       - Try to disarm a trap
  help         - Show this message
  quit         - Exit the game
"""
    return info(help_text)

async def handle_spend(game: Game, args: List[str]) -> str:
    """Handles the 'spend' command."""
    if len(args) != 2:
        return error("Usage: spend <stat> <points>")
    
    stat = args[0].lower()
    try:
        points = int(args[1])
    except ValueError:
        return error("Points must be a number.")

    if points <= 0:
        return error("You must spend a positive number of points.")

    if game.player.attribute_points < points:
        return error("You don't have enough attribute points.")

    if stat not in ["strength", "dexterity", "intelligence"]:
        return error("You can only spend points on strength, dexterity, or intelligence.")

    if stat == "strength":
        game.player.strength += points
    elif stat == "dexterity":
        game.player.dexterity += points
    elif stat == "intelligence":
        game.player.intelligence += points

    game.player.attribute_points -= points
    return success(f"You spent {points} points on {stat}.")

async def handle_disarm(game: Game, args: List[str]) -> str:
    """Handles the 'disarm' command."""
    msg = game.engine.disarm_trap()
    return success(msg) if "disarmed" in msg else error(msg)

async def handle_look(game: Game, args: List[str]) -> str:
    """Handles the 'look' command."""
    return info(game.engine.get_location_description())

async def handle_status(game: Game, args: List[str]) -> str:
    """Handles the 'status' command."""
    return info(game.engine.get_player_status())

async def handle_travel(game: Game, args: List[str]) -> str:
    """Handles the 'travel' command."""
    if not args:
        return error("Travel where? (north, south, east, west)")

    direction = args[0]
    err, enemy = game.engine.move_to_location(direction)
    if err:
        return error(err)

    new_location = game.world.get_location(game.player.location_id)
    response = success(f"You travel {direction} to {new_location.name}")
    response += "\n" + info(game.engine.get_location_description())

    if enemy:
        game.in_combat = True
        game.current_enemy = enemy
        response += "\n" + warning(f"You have encountered a {enemy.name}!")

    return response

async def handle_inventory(game: Game, args: List[str]) -> str:
    """Handles the 'inventory' command."""
    return info(game.engine.get_inventory())

async def handle_use(game: Game, args: List[str]) -> str:
    """Handles the 'use' command."""
    if not args:
        return error("Use what?")
    item_identifier = " ".join(args)
    msg = game.engine.use_item(item_identifier)
    return success(msg) if "restored" in msg or "eat" in msg else info(msg)

async def handle_rest(game: Game, args: List[str]) -> str:
    """Handles the 'rest' command."""
    duration = args[0] if args else "short"
    msg = game.engine.rest(duration)
    status = game.engine.get_player_status()
    return success(msg) + "\n" + info(status)

async def handle_talk(game: Game, args: List[str]) -> str:
    """Handles the 'talk' command."""
    if not args:
        return error("Talk to whom?")
    npc_id = " ".join(args)
    return info(game.engine.talk_to_npc(npc_id))

async def handle_buy(game: Game, args: List[str]) -> str:
    """Handles the 'buy' command."""
    if not args:
        return error("Usage: buy <npc> <item>")
    msg = game.engine.buy_item_from_npc_by_name(args)
    return success(msg) if "bought" in msg else error(msg)

async def handle_investigate(game: Game, args: List[str]) -> str:
    """Handles the 'investigate' command."""
    msg = game.engine.investigate_location()
    return success(msg) if "treasure" in msg else info(msg)

async def handle_encounter(game: Game, args: List[str]) -> str:
    """Handles the 'encounter' command."""
    msg, enemy = game.engine.encounter_enemy()
    if enemy:
        game.in_combat = True
        game.current_enemy = enemy
        return warning(msg)
    return info(msg)

async def handle_quest(game: Game, args: List[str]) -> str:
    """Handles the 'quest' command."""
    subcommand = args[0] if args else "list"
    if subcommand == "list":
        return info(game.engine.get_active_quests_display())
    elif subcommand == "accept":
        if len(args) < 2:
            return error("Accept quest from which NPC?")
        npc_identifier = " ".join(args[1:])
        return info(game.engine.accept_quest_from_npc(npc_identifier))
    else:
        return error(f"Unknown quest command: {subcommand}")

async def handle_map(game: Game, args: List[str]) -> str:
    """Handles the 'map' command."""
    return info(game.engine.get_map_display())

async def handle_quit(game: Game, args: List[str]) -> str:
    """Handles the 'quit' command."""
    save_msg = game.engine.save_game()
    return f"{save_msg}\nQUIT"

async def handle_equip(game: Game, args: List[str]) -> str:
    """Handles the 'equip' command."""
    if not args:
        return error("Equip what?")
    item_name = " ".join(args)
    return info(game.engine.equip_item(item_name))

async def handle_unequip(game: Game, args: List[str]) -> str:
    """Handles the 'unequip' command."""
    if not args:
        return error("Unequip what? (e.g., 'weapon', 'chest')")
    slot = " ".join(args)
    return info(game.engine.unequip_item(slot))

async def handle_skills(game: Game, args: List[str]) -> str:
    """Handles the 'skills' command."""
    return info(game.engine.get_skills_display())


async def handle_attack(game: Game, args: List[str]) -> str:
    """Handles the 'attack' command."""
    if not game.in_combat:
        return error("You are not in combat.")
    
    player_attack = game.player.get_total_attack()
    enemy = game.current_enemy
    
    enemy.health = max(0, enemy.health - player_attack)
    
    return success(f"You attack {enemy.name} for {player_attack} damage.")

async def handle_cast(game: Game, args: List[str]) -> str:
    """Handles the 'cast' command for using skills."""
    if not game.in_combat:
        return error("You can only cast spells in combat.")
        
    if not args:
        return error("Cast what skill?")
        
    skill_name = " ".join(args)
    skill_to_use = None
    for skill in game.player.skills:
        if skill.name.lower() == skill_name.lower():
            skill_to_use = skill
            break
            
    if not skill_to_use:
        return error(f"You don't know the {skill_name} skill.")
        
    if not game.player.use_mana(skill_to_use.cost):
        return error("Not enough mana.")
        
    if skill_to_use.effect == "damage":
        enemy = game.current_enemy
        enemy.health = max(0, enemy.health - skill_to_use.value)
        return success(f"You cast {skill_to_use.name} on {enemy.name} for {skill_to_use.value} damage.")
    elif skill_to_use.effect == "heal":
        game.player.heal(skill_to_use.value)
        return success(f"You cast {skill_to_use.name} and heal for {skill_to_use.value} health.")
    
    return error("That skill has no effect in this situation.")

async def handle_flee(game: Game, args: List[str]) -> str:
    """Handles the 'flee' command."""
    if not game.in_combat:
        return error("You are not in combat.")
        
    game.in_combat = False
    game.current_enemy = None
    return info("You have fled from combat.")

COMMANDS: Dict[str, CommandHandler] = {
    "help": handle_help,
    "look": handle_look,
    "status": handle_status,
    "travel": handle_travel,
    "inventory": handle_inventory,
    "use": handle_use,
    "rest": handle_rest,
    "talk": handle_talk,
    "buy": handle_buy,
    "investigate": handle_investigate,
    "quest": handle_quest,
    "map": handle_map,
    "equip": handle_equip,
    "unequip": handle_unequip,
    "skills": handle_skills,
    "attack": handle_attack,
    "cast": handle_cast,
    "flee": handle_flee,
    "quit": handle_quit,
    "disarm": handle_disarm,
    "spend": handle_spend,
}
