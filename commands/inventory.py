from typing import List, TYPE_CHECKING
from color import info, error, success, warning
from session_manager import session_manager
from .base import CommandHandler

if TYPE_CHECKING:
    from game import Game

async def handle_inventory(game: 'Game', args: List[str]) -> str:
    """Handles the 'inventory' command."""
    return info(game.engine.get_inventory(), game=game)

async def handle_use(game: 'Game', args: List[str]) -> str:
    """Handles the 'use' command."""
    if not args:
        return error("Use what?", game=game)
    item_identifier = " ".join(args)
    success_flag, msg = game.engine.use_item(item_identifier)
    return success(msg, game=game) if success_flag else error(msg, game=game)

async def handle_equip(game: 'Game', args: List[str]) -> str:
    """Handles the 'equip' command."""
    if not args:
        return error("Equip what?", game=game)
    item_name = " ".join(args)
    success_flag, msg = game.engine.equip_item(item_name)
    return success(msg, game=game) if success_flag else error(msg, game=game)

async def handle_unequip(game: 'Game', args: List[str]) -> str:
    """Handles the 'unequip' command."""
    if not args:
        return error("Unequip what? (e.g., 'weapon', 'chest')", game=game)
    slot = " ".join(args)
    success_flag, msg = game.engine.unequip_item(slot)
    return success(msg, game=game) if success_flag else error(msg, game=game)

async def handle_craft(game: 'Game', args: List[str]) -> str:
    """Handles the 'craft' command."""
    if not args:
        return info(game.engine.get_recipes_display(), game=game)
    
    recipe_name = " ".join(args)
    success_flag, msg = game.engine.craft_item(recipe_name)
    return success(msg, game=game) if success_flag else error(msg, game=game)

async def handle_drop(game: 'Game', args: List[str]) -> str:
    """Handles the 'drop' command."""
    if not args:
        return error("Drop what?", game=game)
    
    # Parse amount if present (e.g., "drop 5 potion")
    amount = 1
    item_name = args[0]
    
    if args[0].isdigit() and len(args) > 1:
        try:
            amount = int(args[0])
            item_name = " ".join(args[1:])
        except ValueError:
            pass
    else:
        item_name = " ".join(args)
        
    success_flag, msg = game.engine.drop_item(item_name, amount)
    return success(msg, game=game) if success_flag else error(msg, game=game)

async def handle_pickup(game: 'Game', args: List[str]) -> str:
    """Handles the 'pickup' or 'get' command."""
    if not args:
        return error("Pick up what?", game=game)
    
    item_name = " ".join(args)
    success_flag, msg = game.engine.pickup_item(item_name)
    return success(msg, game=game) if success_flag else error(msg, game=game)

async def handle_give(game: 'Game', args: List[str]) -> str:
    """Handles the 'give' command."""
    if len(args) < 2:
        return error("Usage: give <player> <item>", game=game)
    
    target_name = args[0]
    item_name = " ".join(args[1:])
    
    target_session = session_manager.get_session_by_name(target_name)
    if not target_session:
        return error(f"Player {target_name} not found.", game=game)
    
    target_game = target_session.game
    
    # Check location
    if target_game.player.location_id != game.player.location_id:
        return error(f"{target_name} is not here.", game=game)
    
    item_to_give = None
    for item in game.player.inventory:
        if item.name.lower() == item_name.lower() or item.id == item_name.lower():
            item_to_give = item
            break
            
    if not item_to_give:
        return error(f"You don't have '{item_name}'.", game=game)
    
    # Transfer
    game.player.remove_item(item_to_give.id)
    target_game.player.add_item(item_to_give)
    
    # Notify target
    await target_session.sender.send(
        success(f"{game.player.name} gave you {item_to_give.name}.", game=target_game)
    )
    
    return success(f"You gave {item_to_give.name} to {target_name}.", game=game)
