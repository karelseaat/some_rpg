from typing import Dict
from .base import CommandHandler
from .exploration import handle_look, handle_travel, handle_map, handle_investigate, handle_disarm
from .combat import handle_attack, handle_cast, handle_flee
from .inventory import handle_inventory, handle_use, handle_equip, handle_unequip, handle_craft, handle_drop, handle_pickup, handle_give
from .interaction import handle_talk, handle_buy, handle_say, handle_yell
from .character import handle_status, handle_skills, handle_spend, handle_rest, handle_quest
from .admin import handle_cheat_add_item
from .system import handle_quit, handle_toggle_color, handle_help

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
    "toggle_color": handle_toggle_color,
    "say": handle_say,
    "yell": handle_yell,
    "give": handle_give,
    "craft": handle_craft,
    "drop": handle_drop,
    "pickup": handle_pickup,
    "get": handle_pickup,
    "cheat_add_item": handle_cheat_add_item,
}
