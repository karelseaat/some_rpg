"""Game engine logic."""

import random
import os
from typing import Optional, List, Tuple, Dict, Any
import bcrypt
from models import Player, World, Item, Encounter, Danger, Quest, NPC, Enemy, Skill, GameSettings
from color import color_text, Colors, title
from database import AsyncSessionLocal, PlayerState, WorldState
from systems.combat import CombatSystem
from systems.exploration import ExplorationSystem
from systems.inventory import InventorySystem
from systems.quest import QuestSystem
from systems.persistence import PersistenceSystem
from systems.crafting import CraftingSystem
from systems.achievements import AchievementSystem
from systems.progression import ProgressionSystem


class GameEngine:
    """Main game engine."""

    def __init__(self, world: World, player: Player):
        self.world = world
        self.player = player
        self.combat_system = CombatSystem(world, player)
        self.exploration_system = ExplorationSystem(world, player)
        self.inventory_system = InventorySystem(world, player)
        self.quest_system = QuestSystem(world, player)
        self.persistence_system = PersistenceSystem(world)
        self.crafting_system = CraftingSystem(world, player)
        self.achievement_system = AchievementSystem()
        self.progression_system = ProgressionSystem(world)

    @staticmethod
    def generate_password() -> str:
        """Generate a new three-word password."""
        with open("words.txt", "r") as f:
            words = [line.strip() for line in f.readlines()]
        
        password_words = [random.choice(words).capitalize() for _ in range(3)]
        return "".join(password_words)

    def move_to_location(self, direction: str) -> Tuple[Optional[str], Optional[str], Optional[Enemy]]:
        """Move player to a location based on direction. Returns (error, encounter_msg, enemy)."""
        err, success = self.exploration_system.move_to_location(direction)
        if not success:
            return err, None, None
        
        # Trigger encounter
        msg, enemy = self.trigger_encounter()
        return None, msg, enemy

    def get_location_description(self, game: "Game") -> str:
        """Get detailed description of current location."""
        return self.exploration_system.get_location_description(game)

    def get_player_status(self, game: "Game") -> str:
        """Get player status display."""
        status = f"\n{color_text(self.player.name, Colors.YELLOW, game=game)}\n"
        status += f"Level {self.player.level} | Health: {self.player.health}/{self.player.max_health} | "
        status += f"Stamina: {self.player.stamina}/{self.player.max_stamina} | Mana: {self.player.mana}/{self.player.max_mana} | Gold: {self.player.gold}\n"
        status += f"Strength: {self.player.strength} | Dexterity: {self.player.dexterity} | Intelligence: {self.player.intelligence}\n"
        status += f"Attack: {self.player.get_total_attack()} | Defense: {self.player.get_total_defense()}\n"
        status += f"Experience: {self.player.experience}\n"
        status += f"Skill Points: {self.player.skill_points}\n"
        status += f"Attribute Points: {self.player.attribute_points}\n"
        
        if self.player.equipment:
            status += "\nEquipment:\n"
            for slot, item in self.player.equipment.items():
                status += f"  - {slot.capitalize()}: {item.name}\n"
        
        return status

    def rest(self, duration: str = "short") -> Tuple[str, Optional[Enemy]]:
        """Rest to restore health and stamina. Returns (message, enemy)."""
        location = self.world.get_location(self.player.location_id)
        
        # Safe resting in inns/settlements
        if location.type in ["inn", "settlement"]:
            if duration == "short":
                self.player.heal(self.world.settings.rest_short_health_gain)
                self.player.restore_stamina(self.world.settings.rest_short_stamina_gain)
                return "You rest briefly and feel somewhat refreshed", None
            elif duration == "long":
                self.player.health = self.player.max_health
                self.player.stamina = self.player.max_stamina
                return "You rest well and fully recover", None
        
        # Dangerous resting in wilderness
        else:
            # 30% chance of ambush
            if random.random() < 0.3:
                msg, enemy = self.encounter_enemy()
                if enemy:
                    return f"You try to rest, but... {msg}", enemy
            
            # If safe, recover half amount
            if duration == "short":
                self.player.heal(self.world.settings.rest_short_health_gain // 2)
                self.player.restore_stamina(self.world.settings.rest_short_stamina_gain // 2)
                return "You rest uneasily on the hard ground. (50% recovery)", None
            elif duration == "long":
                self.player.heal(self.player.max_health // 2)
                self.player.restore_stamina(self.player.max_stamina // 2)
                return "You sleep fitfully, keeping one eye open. (50% recovery)", None
        
        return "Invalid rest duration", None

    def use_item(self, item_identifier: str) -> Tuple[bool, str]:
        """Use an item from inventory by ID or name."""
        return self.inventory_system.use_item(item_identifier)

    def investigate_location(self) -> str:
        """Investigate current location for secrets/items."""
        return self.exploration_system.investigate_location()

    def encounter_enemy(self) -> Tuple[str, Optional[Enemy]]:
        """Handle a random encounter. Returns (message, enemy object)."""
        return self.combat_system.encounter_enemy()

    def resolve_player_attack(self, enemy: Enemy) -> Dict[str, Any]:
        """Calculate and apply player attack damage to enemy."""
        return self.combat_system.resolve_player_attack(enemy)

    def get_loot(self, enemy: Enemy) -> List[Item]:
        """Generate loot from a defeated enemy."""
        return self.combat_system.get_loot(enemy)

    def trigger_encounter(self) -> Tuple[Optional[str], Optional[Enemy]]:
        """Trigger a random encounter. Returns (message, enemy object)."""
        return self.combat_system.trigger_encounter()

    def trigger_danger(self) -> Optional[str]:
        """Trigger a known danger in the current location."""
        return self.exploration_system.trigger_danger()

    def trigger_hidden_dangers(self) -> Optional[str]:
        """Trigger a hidden danger in the current location."""
        return self.exploration_system.trigger_hidden_dangers()

    def disarm_trap(self) -> str:
        """Attempt to disarm a revealed trap in the current location."""
        return self.exploration_system.disarm_trap()

    def talk_to_npc(self, game: "Game", npc_id: str) -> str:
        """Talk to an NPC by ID or name."""
        return self.quest_system.talk_to_npc(game, npc_id)

    def buy_from_npc(self, npc_identifier: str, item_identifier: str) -> Tuple[bool, str]:
        """Buy an item from an NPC by ID or name."""
        return self.inventory_system.buy_from_npc(npc_identifier, item_identifier)

    def buy_item_from_npc_by_name(self, name_parts: List[str]) -> Tuple[bool, str]:
        """Buy an item from an NPC, parsing multi-word names."""
        return self.inventory_system.buy_item_from_npc_by_name(name_parts)

    def get_inventory(self) -> str:
        """Get player inventory display."""
        return self.inventory_system.get_inventory_display()

    def accept_quest_from_npc(self, npc_identifier: str) -> str:
        """Accept a quest from an NPC by ID or name."""
        return self.quest_system.accept_quest_from_npc(npc_identifier)

    def get_active_quests_display(self) -> str:
        """Get a formatted string of active quests."""
        return self.quest_system.get_active_quests_display()

    def get_map_display(self) -> str:
        """Get a grid-based ASCII art map of visited locations."""
        if not self.player.visited_locations:
            return "You haven't explored anywhere yet."

        visited_locs = [self.world.get_location(loc_id) for loc_id in self.player.visited_locations]
        
        min_x = min(loc.x for loc in visited_locs)
        max_x = max(loc.x for loc in visited_locs)
        min_y = min(loc.y for loc in visited_locs)
        max_y = max(loc.y for loc in visited_locs)

        cell_width = 13
        cell_height = 3

        map_width = (max_x - min_x + 1) * cell_width
        map_height = (max_y - min_y + 1) * cell_height
        
        grid = [[' ' for _ in range(map_width)] for _ in range(map_height)]
        
        visited_coords = { (loc.x, loc.y): loc for loc in visited_locs }

        for loc in visited_locs:
            grid_x = (loc.x - min_x) * cell_width
            grid_y = (loc.y - min_y) * cell_height
            
            is_current = loc.id == self.player.location_id
            
            room_name = loc.name[:9].center(9)
            
            if is_current:
                room_display = f"<{room_name}>"
            else:
                room_display = f"[{room_name}]"

            for i, char in enumerate(room_display):
                # Draw room centered in the cell
                grid[grid_y + 2][grid_x + 2 + i] = char

            # Draw connections
            # South
            if (loc.x, loc.y + 1) in visited_coords:
                grid[grid_y + 3][grid_x + 7] = '|'
                grid[grid_y + 4][grid_x + 7] = '|'
            # East
            if (loc.x + 1, loc.y) in visited_coords:
                grid[grid_y + 2][grid_x + 13] = '-'
                grid[grid_y + 2][grid_x + 14] = '-'
        
        return "Your Explored Map:\n" + "\n".join("".join(row) for row in grid)

    def accept_quest(self, quest_id: str) -> str:
        """Accept a quest."""
        return self.quest_system.accept_quest(quest_id)

    def complete_quest(self, quest_identifier: str) -> str:
        """Complete a quest."""
        return self.quest_system.complete_quest(quest_identifier)

    def equip_item(self, item_name: str) -> Tuple[bool, str]:
        """Equip an item from inventory."""
        return self.inventory_system.equip_item(item_name)

    def unequip_item(self, slot: str) -> Tuple[bool, str]:
        """Unequip an item from a slot."""
        return self.inventory_system.unequip_item(slot)

    def get_skills_display(self) -> str:
        """Get player's skills display."""
        if not self.player.skills:
            return "You have no skills."

        skills_text = "Skills:\n"
        for skill in self.player.skills:
            skills_text += f"  - {skill.name}: {skill.description}\n"
        return skills_text

    def craft_item(self, recipe_name: str) -> Tuple[bool, str]:
        """Craft an item."""
        return self.crafting_system.craft_item(recipe_name)

    def get_recipes_display(self) -> str:
        """Get available recipes."""
        return self.crafting_system.get_available_recipes()

    def drop_item(self, item_identifier: str, amount: int = 1) -> Tuple[bool, str]:
        """Drop an item."""
        return self.inventory_system.drop_item(item_identifier, amount)

    def pickup_item(self, item_identifier: str) -> Tuple[bool, str]:
        """Pick up an item."""
        return self.inventory_system.pickup_item(item_identifier)

    def add_experience(self, amount: int):
        """Add experience to player."""
        self.progression_system.add_experience(self.player, amount)

    async def save_game(self) -> str:
        """Saves the current game state to the database."""
        return await self.persistence_system.save_game(self.player)

    @staticmethod
    async def load_game(world: World, password: str) -> Optional[Player]:
        return await PersistenceSystem(world).load_game(password)
    
