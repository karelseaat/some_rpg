from typing import List, TYPE_CHECKING
from color import info, error, success, warning
from .base import CommandHandler

if TYPE_CHECKING:
    from game import Game

async def handle_look(game: 'Game', args: List[str]) -> str:
    """Handles the 'look' command."""
    return info(game.engine.get_location_description(game=game), game=game)

async def handle_travel(game: 'Game', args: List[str]) -> str:
    """Handles the 'travel' command."""
    if not args:
        return error("Travel where? (north, south, east, west)", game=game)

    direction = args[0]
    err, encounter_msg, enemy = game.engine.move_to_location(direction)
    if err:
        return error(err, game=game)

    new_location = game.world.get_location(game.player.location_id)
    response = success(f"You travel {direction} to {new_location.name}", game=game)
    response += "\n" + info(game.engine.get_location_description(game=game), game=game)

    if enemy:
        game.in_combat = True
        game.current_enemy = enemy
        response += "\n" + warning(encounter_msg, game=game)
    elif encounter_msg:
        # Non-combat encounter (interaction/obstacle)
        response += "\n" + info(encounter_msg, game=game)

    return response

async def handle_map(game: 'Game', args: List[str]) -> str:
    """Handles the 'map' command."""
    return info(game.engine.get_map_display(), game=game)

async def handle_investigate(game: 'Game', args: List[str]) -> str:
    """Handles the 'investigate' command."""
    msg = game.engine.investigate_location()
    return success(msg, game=game) if "treasure" in msg else info(msg, game=game)

async def handle_disarm(game: 'Game', args: List[str]) -> str:
    """Handles the 'disarm' command."""
    msg = game.engine.disarm_trap()
    return success(msg, game=game) if "disarmed" in msg else error(msg, game=game)
