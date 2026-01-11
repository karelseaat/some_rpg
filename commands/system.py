from typing import List, TYPE_CHECKING
from color import info, error, success, warning
from .base import CommandHandler

if TYPE_CHECKING:
    from game import Game

async def handle_quit(game: 'Game', args: List[str]) -> str:
    """Handles the 'quit' command."""
    save_msg = await game.engine.save_game()
    return f"{save_msg}\nQUIT"

async def handle_toggle_color(game: 'Game', args: List[str]) -> str:
    """Handle the toggle_color command."""
    game.player.use_color = not game.player.use_color
    if game.player.use_color:
        return "Color output enabled."
    else:
        return "Color output disabled."

async def handle_help(game: 'Game', args: List[str]) -> str:
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
  say <msg>    - Say something to people in the room
  yell <msg>   - Yell something to everyone on the server
  give <p> <i> - Give an item to another player
  craft <item> - Craft an item (or list recipes)
  drop <item>  - Drop an item on the ground
  pickup <item> - Pick up an item from the ground (alias: get)
  help         - Show this message
  quit         - Exit the game
  toggle_color - Toggle color output on/off
"""
    return info(help_text, game=game)
