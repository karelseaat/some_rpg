from typing import List, TYPE_CHECKING
from color import info, error, success, warning, color_text, Colors
from session_manager import session_manager
from .base import CommandHandler

if TYPE_CHECKING:
    from game import Game

async def handle_talk(game: 'Game', args: List[str]) -> str:
    """Handles the 'talk' command."""
    if not args:
        return error("Talk to whom?", game=game)
    npc_id = " ".join(args)
    return info(game.engine.talk_to_npc(game=game, npc_id=npc_id), game=game)

async def handle_buy(game: 'Game', args: List[str]) -> str:
    """Handles the 'buy' command."""
    if not args:
        return error("Usage: buy <npc> <item>", game=game)
    success_flag, msg = game.engine.buy_item_from_npc_by_name(args)
    return success(msg, game=game) if success_flag else error(msg, game=game)

async def handle_say(game: 'Game', args: List[str]) -> str:
    """Handles the 'say' command."""
    if not args:
        return error("Say what?", game=game)
    
    message = " ".join(args)
    formatted_msg = f"{color_text(game.player.name, Colors.YELLOW, game=game)} says: {message}"
    
    await session_manager.broadcast_to_location(
        game.player.location_id, 
        formatted_msg, 
        exclude_player=game.player.name
    )
    return f"You say: {message}"

async def handle_yell(game: 'Game', args: List[str]) -> str:
    """Handles the 'yell' command."""
    if not args:
        return error("Yell what?", game=game)
    
    message = " ".join(args)
    formatted_msg = f"{color_text(game.player.name, Colors.RED, game=game)} yells: {message}"
    
    await session_manager.broadcast(
        formatted_msg, 
        exclude_player=game.player.name
    )
    return f"You yell: {message}"
