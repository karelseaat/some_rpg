from typing import List, TYPE_CHECKING
from color import info, error, success, warning
from .base import CommandHandler

if TYPE_CHECKING:
    from game import Game

async def handle_status(game: 'Game', args: List[str]) -> str:
    """Handles the 'status' command."""
    return info(game.engine.get_player_status(game=game), game=game)

async def handle_skills(game: 'Game', args: List[str]) -> str:
    """Handles the 'skills' command."""
    return info(game.engine.get_skills_display(), game=game)

async def handle_spend(game: 'Game', args: List[str]) -> str:
    """Handles the 'spend' command."""
    if len(args) != 2:
        return error("Usage: spend <stat> <points>", game=game)
    
    stat = args[0].lower()
    try:
        points = int(args[1])
    except ValueError:
        return error("Points must be a number.", game=game)

    if points <= 0:
        return error("You must spend a positive number of points.", game=game)

    if game.player.attribute_points < points:
        return error("You don't have enough attribute points.", game=game)

    if stat not in ["strength", "dexterity", "intelligence"]:
        return error("You can only spend points on strength, dexterity, or intelligence.", game=game)

    if stat == "strength":
        game.player.strength += points
    elif stat == "dexterity":
        game.player.dexterity += points
    elif stat == "intelligence":
        game.player.intelligence += points

    game.player.attribute_points -= points
    return success(f"You spent {points} points on {stat}.", game=game)

async def handle_rest(game: 'Game', args: List[str]) -> str:
    """Handles the 'rest' command."""
    duration = args[0] if args else "short"
    msg, enemy = game.engine.rest(duration)
    
    if enemy:
        game.in_combat = True
        game.current_enemy = enemy
        return warning(msg, game=game)
        
    status = game.engine.get_player_status(game=game)
    return success(msg, game=game) + "\n" + info(status, game=game)

async def handle_quest(game: 'Game', args: List[str]) -> str:
    """Handles the 'quest' command."""
    subcommand = args[0] if args else "list"
    if subcommand == "list":
        return info(game.engine.get_active_quests_display(), game=game)
    elif subcommand == "accept":
        if len(args) < 2:
            return error("Accept quest from which NPC?", game=game)
        npc_identifier = " ".join(args[1:])
        return info(game.engine.accept_quest_from_npc(npc_identifier), game=game)
    elif subcommand == "complete":
        if len(args) < 2:
            return error("Complete which quest?", game=game)
        quest_identifier = " ".join(args[1:])
        msg = game.engine.complete_quest(quest_identifier)
        return success(msg, game=game) if "Completed" in msg else error(msg, game=game)
    else:
        return error(f"Unknown quest command: {subcommand}", game=game)
