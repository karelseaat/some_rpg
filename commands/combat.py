from typing import List, TYPE_CHECKING
from color import info, error, success, warning
from .base import CommandHandler

if TYPE_CHECKING:
    from game import Game

async def handle_attack(game: 'Game', args: List[str]) -> str:
    """Handles the 'attack' command."""
    if not game.in_combat:
        return error("You are not in combat.", game=game)
    
    enemy = game.current_enemy
    result = game.engine.resolve_player_attack(enemy)
    
    damage = result["damage"]
    msg = f"You attack {enemy.name} for {damage} damage."
    
    if result["is_crit"]:
        msg += " " + warning("CRITICAL HIT!", game=game)
        
    if result["effectiveness"] == "super":
        msg += " " + success("It's super effective!", game=game)
    elif result["effectiveness"] == "not_very":
        msg += " " + info("It's not very effective...", game=game)
    
    return success(msg, game=game)

async def handle_cast(game: 'Game', args: List[str]) -> str:
    """Handles the 'cast' command for using skills."""
    if not game.in_combat:
        return error("You can only cast spells in combat.", game=game)
        
    if not args:
        return error("Cast what skill?", game=game)
        
    skill_name = " ".join(args)
    skill_to_use = None
    for skill in game.player.skills:
        if skill.name.lower() == skill_name.lower():
            skill_to_use = skill
            break
            
    if not skill_to_use:
        return error(f"You don't know the {skill_name} skill.", game=game)
        
    if not game.player.use_mana(skill_to_use.cost):
        return error("Not enough mana.", game=game)
        
    if skill_to_use.effect == "damage":
        enemy = game.current_enemy
        enemy.health = max(0, enemy.health - skill_to_use.value)
        return success(f"You cast {skill_to_use.name} on {enemy.name} for {skill_to_use.value} damage.", game=game)
    elif skill_to_use.effect == "heal":
        game.player.heal(skill_to_use.value)
        return success(f"You cast {skill_to_use.name} and heal for {skill_to_use.value} health.", game=game)
    
    return error("That skill has no effect in this situation.", game=game)

async def handle_flee(game: 'Game', args: List[str]) -> str:
    """Handles the 'flee' command."""
    if not game.in_combat:
        return error("You are not in combat.", game=game)
        
    game.in_combat = False
    game.current_enemy = None
    return info("You have fled from combat.", game=game)
