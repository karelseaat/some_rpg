from typing import List, TYPE_CHECKING
from color import info, error, success, warning
from .base import CommandHandler

if TYPE_CHECKING:
    from game import Game

async def handle_cheat_add_item(game: 'Game', args: List[str]) -> str:
    """Handles the 'cheat_add_item' command."""
    if len(args) < 2:
        return error("Usage: cheat_add_item <item_id> <amount>", game=game)
    
    item_id = args[0]
    try:
        amount = int(args[1])
    except ValueError:
        return error("Amount must be a number.", game=game)
        
    item = game.world.get_item(item_id)
    if not item:
        return error(f"Item {item_id} not found.", game=game)
        
    item.amount = amount
    game.player.add_item(item)
    return success(f"Added {amount}x {item.name} to inventory.", game=game)
