"""Game engine logic."""

import random
from typing import Optional, List, Tuple
from models import Player, World, Item, Encounter, Danger, Quest


class GameEngine:
    """Main game engine."""

    def __init__(self, world: World, player: Player):
        self.world = world
        self.player = player

    def move_to_location(self, location_id: str) -> Optional[str]:
        """Move player to a location. Returns error message if invalid."""
        current_location = self.world.get_location(self.player.location_id)
        
        if not current_location:
            return "Error: Current location not found"
        
        if location_id not in current_location.exits.values():
            return "You cannot go that way"
        
        new_location = self.world.get_location(location_id)
        if not new_location:
            return f"Location {location_id} not found"
        
        # Cost stamina to travel
        if not self.player.use_stamina(10):
            return "You're too tired to travel. Rest first."
        
        self.player.location_id = location_id
        return None

    def get_location_description(self) -> str:
        """Get detailed description of current location."""
        location = self.world.get_location(self.player.location_id)
        if not location:
            return "Unknown location"
        
        desc = f"\n{location.name}\n"
        desc += "-" * len(location.name) + "\n"
        desc += location.description + "\n\n"
        
        # List exits
        if location.exits:
            desc += "Exits: " + ", ".join(location.exits.keys()) + "\n"
        
        # List NPCs
        if location.npcs:
            desc += f"\nPeople here:\n"
            for npc_id in location.npcs:
                npc = self.world.get_npc(npc_id)
                if npc:
                    desc += f"  - {npc.name}\n"
        
        return desc

    def get_player_status(self) -> str:
        """Get player status display."""
        status = f"\n{self.player.name}\n"
        status += f"Level {self.player.level} | Health: {self.player.health}/{self.player.max_health} | "
        status += f"Stamina: {self.player.stamina}/{self.player.max_stamina} | Gold: {self.player.gold}\n"
        status += f"Experience: {self.player.experience}\n"
        return status

    def rest(self, duration: str = "short") -> str:
        """Rest to restore health and stamina."""
        location = self.world.get_location(self.player.location_id)
        
        if location.type not in ["inn", "settlement"]:
            return "You can only rest safely in settlements or inns"
        
        if duration == "short":
            self.player.heal(20)
            self.player.restore_stamina(30)
            return "You rest briefly and feel somewhat refreshed"
        elif duration == "long":
            self.player.health = self.player.max_health
            self.player.stamina = self.player.max_stamina
            return "You rest well and fully recover"
        
        return "Invalid rest duration"

    def use_item(self, item_id: str) -> str:
        """Use an item from inventory."""
        item = None
        for inv_item in self.player.inventory:
            if inv_item.id == item_id:
                item = inv_item
                break
        
        if not item:
            return "You don't have that item"
        
        if item.type == "consumable":
            if item.effect == "heal":
                self.player.heal(item.amount)
                response = f"You drink the {item.name} and feel {item.amount} health restored"
                item.amount -= 1
                if item.amount <= 0:
                    self.player.remove_item(item_id)
                return response
            elif item.effect == "stamina":
                self.player.restore_stamina(item.amount)
                response = f"You consume the {item.name} and regain {item.amount} stamina"
                item.amount -= 1
                if item.amount <= 0:
                    self.player.remove_item(item_id)
                return response
        
        elif item.type == "food":
            if item.effect == "heal":
                self.player.heal(item.amount)
                response = f"You eat the {item.name} and feel {item.amount} health restored"
                item.amount -= 1
                if item.amount <= 0:
                    self.player.remove_item(item_id)
                return response
        
        return f"You cannot use {item.name}"

    def investigate_location(self) -> str:
        """Investigate current location for secrets/items."""
        location = self.world.get_location(self.player.location_id)
        if not location:
            return "There's nothing to investigate here"
        
        if not location.treasure:
            return "You search but find nothing of value"
        
        found_items = []
        for treasure_id in location.treasure:
            item = self.world.get_item(treasure_id)
            if item and random.random() > 0.3:  # 70% chance to find
                found_items.append(item)
                location.treasure.remove(treasure_id)
        
        if found_items:
            response = "Your investigation reveals treasure!\n"
            for item in found_items:
                self.player.add_item(Item(
                    id=item.id,
                    name=item.name,
                    description=item.description,
                    type=item.type,
                    value=item.value,
                    effect=item.effect,
                    amount=1
                ))
                response += f"  Found: {item.name}\n"
            return response
        
        return "You search but find nothing"

    def encounter_enemy(self) -> Tuple[str, int]:
        """Handle a random encounter. Returns (message, gold_reward)."""
        location = self.world.get_location(self.player.location_id)
        
        if not location or not location.encounters:
            return "No encounter", 0
        
        encounter_id = random.choice(location.encounters)
        encounter = self.world.get_encounter(encounter_id)
        
        if not encounter:
            return "Encounter failed to load", 0
        
        if encounter.type == "combat":
            # Simple combat: player wins if they defeat the difficulty
            difficulty_score = {"easy": 1, "medium": 2, "hard": 3}.get(encounter.difficulty, 1)
            player_power = self.player.level + random.randint(1, 10)
            enemy_power = difficulty_score * 5 + random.randint(1, 8)
            
            if player_power > enemy_power:
                gold = encounter.reward * difficulty_score
                exp = encounter.reward
                self.player.add_gold(gold)
                self.player.gain_experience(exp)
                return f"You defeated the {encounter.name} and gained {gold} gold and {exp} exp!", gold
            else:
                damage = 5 * difficulty_score
                self.player.take_damage(damage)
                return f"The {encounter.name} defeated you! You took {damage} damage", 0
        
        elif encounter.type == "interaction":
            msg = f"You encountered a {encounter.name}: {encounter.description}\n"
            msg += f"The encounter is resolved peacefully and you gain {encounter.reward} gold"
            self.player.add_gold(encounter.reward)
            return msg, encounter.reward
        
        elif encounter.type == "obstacle":
            msg = f"You face an obstacle: {encounter.name}\n"
            msg += f"You overcome it with effort"
            return msg, 0
        
        return "Unknown encounter type", 0

    def trigger_danger(self) -> str:
        """Trigger a random danger. Returns damage and message."""
        location = self.world.get_location(self.player.location_id)
        
        if not location or not location.dangers:
            return "No danger"
        
        danger_id = random.choice(location.dangers)
        danger = self.world.get_danger(danger_id)
        
        if not danger:
            return "Danger failed to load"
        
        escape_scores = {"easy": 0.8, "medium": 0.5, "hard": 0.2}
        escape_chance = escape_scores.get(danger.escape_difficulty, 0.5)
        
        if random.random() < escape_chance:
            return f"You narrowly escape the {danger.name}!"
        else:
            self.player.take_damage(danger.damage)
            return f"You couldn't escape the {danger.name} and took {danger.damage} damage!"

    def talk_to_npc(self, npc_id: str) -> str:
        """Talk to an NPC by ID or name."""
        npc = self.world.get_npc(npc_id)
        
        # If not found by ID, try to find by name (case-insensitive)
        if not npc:
            npc_id_lower = npc_id.lower()
            for npc_obj in self.world.npcs.values():
                if npc_obj.name.lower() == npc_id_lower:
                    npc = npc_obj
                    break
        
        if not npc:
            return "NPC not found"
        
        response = f"\n{npc.name}\n"
        response += f"{npc.description}\n\n"
        response += f'"{npc.dialogue}"\n'
        
        if npc.shop:
            response += "\nThey sell: " + ", ".join(npc.inventory) + "\n"
        
        if npc.offers_quest:
            response += "\n[They have a quest for you]"
        
        return response

    def buy_from_npc(self, npc_id: str, item_id: str) -> str:
        """Buy an item from an NPC."""
        npc = self.world.get_npc(npc_id)
        if not npc or not npc.shop:
            return "This NPC doesn't sell items"
        
        if item_id not in npc.inventory:
            return "They don't have that item"
        
        item = self.world.get_item(item_id)
        if not item:
            return "Item not found"
        
        if not self.player.spend_gold(item.value):
            return f"You don't have enough gold (costs {item.value})"
        
        new_item = Item(
            id=item.id,
            name=item.name,
            description=item.description,
            type=item.type,
            value=item.value,
            effect=item.effect,
            amount=item.amount
        )
        self.player.add_item(new_item)
        return f"You bought {item.name} for {item.value} gold"

    def get_inventory(self) -> str:
        """Get player inventory display."""
        if not self.player.inventory:
            return "Your inventory is empty"
        
        inv = "Inventory:\n"
        for item in self.player.inventory:
            inv += f"  - {item.name} (x{item.amount}) - {item.description}\n"
        return inv

    def accept_quest(self, quest_id: str) -> str:
        """Accept a quest."""
        quest = self.world.get_quest(quest_id)
        if not quest:
            return "Quest not found"
        
        if quest_id in self.player.active_quests:
            return "You already have this quest"
        
        if quest_id in self.player.completed_quests:
            return "You've already completed this quest"
        
        self.player.active_quests.append(quest_id)
        return f"Quest accepted: {quest.name}\n{quest.description}"
