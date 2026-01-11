import random
from typing import Tuple, Optional, Dict, Any, List
from models import World, Player, Enemy, Encounter, Item

class CombatSystem:
    """System for handling combat and encounters."""

    def __init__(self, world: World, player: Player):
        self.world = world
        self.player = player

    def encounter_enemy(self) -> Tuple[str, Optional[Enemy]]:
        """Handle a random encounter. Returns (message, enemy object)."""
        location = self.world.get_location(self.player.location_id)
        
        if not location or not location.encounters:
            return "No encounter here.", None
        
        encounter_id = random.choice(location.encounters)
        encounter = self.world.get_encounter(encounter_id)
        
        if not encounter:
            return "Encounter failed to load.", None
        
        if encounter.type == "combat":
            difficulty_score = self.world.settings.difficulty_multipliers.get(encounter.difficulty, 1)
            
            enemy = Enemy(
                id=encounter.id,
                name=encounter.name,
                description=encounter.description,
                health=difficulty_score * self.world.settings.enemy_health_multiplier,
                max_health=difficulty_score * self.world.settings.enemy_health_multiplier,
                attack=difficulty_score * self.world.settings.enemy_attack_multiplier,
                defense=difficulty_score * self.world.settings.enemy_defense_multiplier,
                reward_gold=encounter.reward,
                reward_exp=encounter.reward,
                weaknesses=encounter.weaknesses,
                resistances=encounter.resistances,
                loot_table=encounter.loot,
                loot_chance=encounter.loot_chance,
            )
            
            return f"You are attacked by a {enemy.name}!", enemy
        
        elif encounter.type == "interaction":
            msg = f"You encountered a {encounter.name}: {encounter.description}\n"
            msg += f"The encounter is resolved peacefully and you gain {encounter.reward} gold"
            self.player.add_gold(encounter.reward)
            return msg, None
        
        elif encounter.type == "obstacle":
            msg = f"You face an obstacle: {encounter.name}\n"
            msg += f"You overcome it with effort"
            return msg, None
        
        return "Unknown encounter type.", None

    def trigger_encounter(self) -> Tuple[Optional[str], Optional[Enemy]]:
        """Trigger a random encounter. Returns (message, enemy object)."""
        location = self.world.get_location(self.player.location_id)
        
        if not location or not location.encounters:
            return None, None
        
        # Chance to trigger an encounter
        if random.random() > self.world.settings.encounter_chance:
            return None, None
        
        encounter_id = random.choice(location.encounters)
        
        message, enemy = self.encounter_enemy()
        
        if enemy:
            # In a real persistent world, we might remove it, but for random encounters 
            # we often keep them or remove them temporarily. 
            # The original code removed it from the location list.
            if encounter_id in location.encounters:
                location.encounters.remove(encounter_id)
            
        return message, enemy

    def resolve_player_attack(self, enemy: Enemy) -> Dict[str, Any]:
        """Calculate and apply player attack damage to enemy. Returns combat details."""
        base_damage = self.player.get_total_attack()
        settings = self.world.settings
        
        # 1. Critical Hit Calculation
        # Base chance + bonus per point of Dexterity
        crit_chance = settings.base_crit_chance + (self.player.dexterity * settings.dexterity_crit_bonus)
        is_crit = random.random() < crit_chance
        
        damage_multiplier = settings.crit_multiplier if is_crit else 1.0
        
        # 2. Elemental Calculation
        effectiveness = "normal"
        weapon_element = "physical"
        
        # Check equipped weapon element
        if "weapon" in self.player.equipment:
            weapon_element = self.player.equipment["weapon"].element
            
        if weapon_element in enemy.weaknesses:
            damage_multiplier *= settings.elemental_weakness_multiplier
            effectiveness = "super"
        elif weapon_element in enemy.resistances:
            damage_multiplier *= settings.elemental_resistance_multiplier
            effectiveness = "not_very"
            
        final_damage = int(base_damage * damage_multiplier)
        
        # Apply damage
        enemy.health = max(0, enemy.health - final_damage)
        
        return {
            "damage": final_damage,
            "is_crit": is_crit,
            "effectiveness": effectiveness,
            "element": weapon_element
        }

    def resolve_enemy_attack(self, enemy: Enemy) -> int:
        """Calculate and apply enemy attack damage to player."""
        damage = enemy.attack
        self.player.take_damage(damage)
        return damage

    def get_loot(self, enemy: Enemy) -> List[Item]:
        """Generate loot from a defeated enemy."""
        loot = []
        if not enemy.loot_table:
            return loot
            
        for item_id in enemy.loot_table:
            if random.random() < enemy.loot_chance:
                item = self.world.get_item(item_id)
                if item:
                    loot.append(item)
        return loot
