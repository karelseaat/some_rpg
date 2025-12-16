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
  inventory    - Check your inventory
  use <item>   - Use an item from your inventory
  rest <type>  - Rest (short/long)
  talk <npc>   - Talk to an NPC
  buy <npc> <item> - Buy an item from an NPC
  quest        - Manage quests (list, accept)
  map          - Show a map of traveled areas
  investigate  - Search location for treasure
  encounter    - Try to encounter something (if available)
  danger       - Trigger a danger check
  status       - Show character status
  !            - Show command history
  !N           - Recall command N to the prompt
  help         - Show this message
  quit         - Exit the game
"""
    return info(help_text)

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
    err = game.engine.move_to_location(direction)
    if err:
        return error(err)

    new_location = game.world.get_location(game.player.location_id)
    response = success(f"You travel {direction} to {new_location.name}")
    response += "\n" + info(game.engine.get_location_description())

    # Random danger chance
    import random
    if random.random() < 0.15:  # 15% chance
        msg = game.engine.trigger_danger()
        response += "\n" + warning(msg)
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
    msg, gold = game.engine.encounter_enemy()
    return success(msg) if "defeated" in msg or "peacefully" in msg else warning(msg)

async def handle_danger(game: Game, args: List[str]) -> str:
    """Handles the 'danger' command."""
    return warning(game.engine.trigger_danger())

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
    return "QUIT"

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
    "encounter": handle_encounter,
    "danger": handle_danger,
    "quest": handle_quest,
    "map": handle_map,
    "quit": handle_quit,
}
