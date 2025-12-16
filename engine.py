"""Game engine logic."""

import random
import os
from typing import Optional, List, Tuple
from models import Player, World, Item, Encounter, Danger, Quest, NPC, Enemy, Skill
from color import color_text, Colors, title
from database import SessionLocal, PlayerState, WorldState


class GameEngine:
    """Main game engine."""

    def __init__(self, world: World, player: Player):
        self.world = world
        self.player = player

    def move_to_location(self, direction: str) -> Optional[str]:
        """Move player to a location based on direction. Returns error message if invalid."""
        current_location = self.world.get_location(self.player.location_id)
        if not current_location:
            return "Error: Current location not found"

        target_x, target_y = current_location.x, current_location.y
        if direction == "north":
            target_y -= 1
        elif direction == "south":
            target_y += 1
        elif direction == "east":
            target_x += 1
        elif direction == "west":
            target_x -= 1
        else:
            return f"Unknown direction: {direction}"

        new_location = self.world.get_location_by_coords(target_x, target_y)
        if not new_location:
            return "You can't go that way."

        # Cost stamina to travel
        if not self.player.use_stamina(10):
            return "You're too tired to travel. Rest first."

        self.player.location_id = new_location.id
        self.player.visited_locations.add(new_location.id)
        return None

    def get_location_description(self) -> str:
        """Get detailed description of current location."""
        location = self.world.get_location(self.player.location_id)
        if not location:
            return "Unknown location"
        
        desc = f"\n{title(location.name)}\n"
        desc += "-" * len(location.name) + "\n"
        desc += location.description + "\n\n"
        
        # Find available exits dynamically
        available_exits = []
        x, y = location.x, location.y
        if self.world.get_location_by_coords(x, y - 1):
            available_exits.append("north")
        if self.world.get_location_by_coords(x, y + 1):
            available_exits.append("south")
        if self.world.get_location_by_coords(x + 1, y):
            available_exits.append("east")
        if self.world.get_location_by_coords(x - 1, y):
            available_exits.append("west")

        if available_exits:
            desc += "Exits: " + color_text(", ".join(available_exits), Colors.YELLOW) + "\n"
        
        # List NPCs
        if location.npcs:
            desc += f"\nPeople here:\n"
            for npc_id in location.npcs:
                npc = self.world.get_npc(npc_id)
                if npc:
                    desc += f"  - {color_text(npc.name, Colors.BRIGHT_MAGENTA)}\n"        
        return desc

    def get_player_status(self) -> str:
        """Get player status display."""
        status = f"\n{color_text(self.player.name, Colors.YELLOW)}\n"
        status += f"Level {self.player.level} | Health: {self.player.health}/{self.player.max_health} | "
        status += f"Stamina: {self.player.stamina}/{self.player.max_stamina} | Mana: {self.player.mana}/{self.player.max_mana} | Gold: {self.player.gold}\n"
        status += f"Attack: {self.player.get_total_attack()} | Defense: {self.player.get_total_defense()}\n"
        status += f"Experience: {self.player.experience}\n"
        status += f"Skill Points: {self.player.skill_points}\n"
        
        if self.player.equipment:
            status += "\nEquipment:\n"
            for slot, item in self.player.equipment.items():
                status += f"  - {slot.capitalize()}: {item.name}\n"
        
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

    def _find_item_by_name_or_id(self, item_identifier: str) -> Optional[Item]:
        """Find an item by ID or name in the world."""
        # First, try by ID
        item = self.world.get_item(item_identifier)
        if item:
            return item
        
        # If not found, try by name (case-insensitive)
        item_identifier_lower = item_identifier.lower()
        for item_obj in self.world.items.values():
            if item_obj.name.lower() == item_identifier_lower:
                return item_obj
        return None

    def use_item(self, item_identifier: str) -> str:
        """Use an item from inventory by ID or name."""
        item_to_use = self._find_item_by_name_or_id(item_identifier)

        if not item_to_use:
            return "You can't find an item like that."

        # Check if the player has this item
        player_item = None
        for inv_item in self.player.inventory:
            if inv_item.id == item_to_use.id:
                player_item = inv_item
                break

        if not player_item:
            return "You don't have that item."
        
        if player_item.type == "consumable":
            if player_item.effect == "heal":
                self.player.heal(player_item.amount)
                response = f"You drink the {player_item.name} and feel {player_item.amount} health restored"
                player_item.amount -= 1
                if player_item.amount <= 0:
                    self.player.remove_item(player_item.id)
                return response
            elif player_item.effect == "stamina":
                self.player.restore_stamina(player_item.amount)
                response = f"You consume the {player_item.name} and regain {player_item.amount} stamina"
                player_item.amount -= 1
                if player_item.amount <= 0:
                    self.player.remove_item(player_item.id)
                return response
        
        elif player_item.type == "food":
            if player_item.effect == "heal":
                self.player.heal(player_item.amount)
                response = f"You eat the {player_item.name} and feel {player_item.amount} health restored"
                player_item.amount -= 1
                if player_item.amount <= 0:
                    self.player.remove_item(player_item.id)
                return response
        
        return f"You cannot use {player_item.name}"

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
            difficulty_score = {"easy": 1, "medium": 2, "hard": 3}.get(encounter.difficulty, 1)
            
            enemy = Enemy(
                id=encounter.id,
                name=encounter.name,
                description=encounter.description,
                health=difficulty_score * 20,
                max_health=difficulty_score * 20,
                attack=difficulty_score * 5,
                defense=difficulty_score * 2,
                reward_gold=encounter.reward,
                reward_exp=encounter.reward,
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

    def _find_npc_by_name(self, npc_id: str) -> Optional[NPC]:
        """Find an NPC by ID or name."""
        npc = self.world.get_npc(npc_id)
        if not npc:
            npc_id_lower = npc_id.lower()
            for npc_obj in self.world.npcs.values():
                if npc_obj.name.lower() == npc_id_lower:
                    npc = npc_obj
                    break
        return npc

    def talk_to_npc(self, npc_id: str) -> str:
        """Talk to an NPC by ID or name."""
        npc = self._find_npc_by_name(npc_id)

        if not npc:
            return "NPC not found"
        
        response = f"\n{color_text(npc.name, Colors.BRIGHT_MAGENTA)}\n"
        response += f"{npc.description}\n\n"
        response += f'"{npc.dialogue}"\n'
        
        if npc.shop:
            response += "\nThey sell: " + ", ".join(npc.inventory) + "\n"
        
        if npc.offers_quest:
            response += "\n[They have a quest for you]"
        
        return response

    def buy_from_npc(self, npc_identifier: str, item_identifier: str) -> str:
        """Buy an item from an NPC by ID or name."""
        npc = self._find_npc_by_name(npc_identifier)
        if not npc or not npc.shop:
            return "This NPC doesn't sell items"

        item = self._find_item_by_name_or_id(item_identifier)
        if not item:
            return "That item doesn't exist."

        if item.id not in npc.inventory:
            return "They don't have that item"
        
        if not self.player.spend_gold(item.value):
            return f"You don't have enough gold (costs {item.value})"
        
        new_item = Item(
            id=item.id,
            name=item.name,
            description=item.description,
            type=item.type,
            value=item.value,
            effect=item.effect,
            amount=1 if item.type != 'consumable' else item.amount
        )
        self.player.add_item(new_item)
        return f"You bought {item.name} for {item.value} gold"

    def buy_item_from_npc_by_name(self, name_parts: List[str]) -> str:
        """Buy an item from an NPC, parsing multi-word names."""
        if not name_parts or len(name_parts) < 2:
            return "Usage: buy <npc name> <item name>"

        # Iterate through all possible split points
        for i in range(1, len(name_parts)):
            npc_name_guess = " ".join(name_parts[:i])
            item_name_guess = " ".join(name_parts[i:])

            npc = self._find_npc_by_name(npc_name_guess)
            item = self._find_item_by_name_or_id(item_name_guess)

            if npc and item and npc.shop and item.id in npc.inventory:
                # Found a valid combination, proceed with purchase
                return self.buy_from_npc(npc.id, item.id)

        return "Could not find a valid NPC and item combination to buy."

    def get_inventory(self) -> str:
        """Get player inventory display."""
        if not self.player.inventory and not self.player.equipment:
            return "Your inventory and equipment are empty"
            
        inv = "Inventory:\n"
        if not self.player.inventory:
            inv += "  - (empty)\n"
        for item in self.player.inventory:
            inv += f"  - {item.name} (x{item.amount}) - {item.description}\n"
            
        inv += "\nEquipment:\n"
        if not self.player.equipment:
            inv += "  - (none)\n"
        for slot, item in self.player.equipment.items():
            inv += f"  - {slot.capitalize()}: {item.name} (equipped)\n"
            
        return inv

    def accept_quest_from_npc(self, npc_identifier: str) -> str:
        """Accept a quest from an NPC by ID or name."""
        npc = self._find_npc_by_name(npc_identifier)

        if not npc:
            return "NPC not found."

        if not npc.offers_quest:
            return f"{npc.name} has no quest to offer."

        # Find the quest associated with this NPC
        quest_to_accept = None
        for quest in self.world.quests.values():
            if quest.giver == npc.id:
                quest_to_accept = quest
                break
        
        if not quest_to_accept:
            return f"Could not find a quest from {npc.name}."
            
        return self.accept_quest(quest_to_accept.id)

    def get_active_quests_display(self) -> str:
        """Get a formatted string of active quests."""
        if not self.player.active_quests:
            return "You have no active quests"
        
        quests_text = "Active Quests:\n"
        for quest_id in self.player.active_quests:
            quest = self.world.get_quest(quest_id)
            if quest:
                quests_text += f"\n{quest.name}\n{quest.description}\n"
        return quests_text

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
        quest = self.world.get_quest(quest_id)
        if not quest:
            return "Quest not found"
        
        if quest_id in self.player.active_quests:
            return "You already have this quest"
        
        if quest_id in self.player.completed_quests:
            return "You've already completed this quest"
        
        self.player.active_quests.append(quest_id)
        return f"Quest accepted: {quest.name}\n{quest.description}"

    def equip_item(self, item_name: str) -> str:
        """Equip an item from inventory."""
        item_to_equip = None
        for item in self.player.inventory:
            if item.name.lower() == item_name.lower():
                item_to_equip = item
                break
        
        if not item_to_equip:
            return f"You don't have a {item_name}."
            
        if not item_to_equip.slot:
            return f"You can't equip {item_to_equip.name}."
            
        # Check if there is already an item in that slot
        if item_to_equip.slot in self.player.equipment:
            # Unequip the old item first
            self.unequip_item(item_to_equip.slot)
            
        # Equip the new item
        self.player.inventory.remove(item_to_equip)
        self.player.equipment[item_to_equip.slot] = item_to_equip
        
        return f"You equipped the {item_to_equip.name}."

    def unequip_item(self, slot: str) -> str:
        """Unequip an item from a slot."""
        if slot not in self.player.equipment:
            return f"You have nothing equipped in the {slot} slot."
            
        item_to_unequip = self.player.equipment.pop(slot)
        self.player.add_item(item_to_unequip)
        
        return f"You unequipped the {item_to_unequip.name}."

    def get_skills_display(self) -> str:
        """Get player's skills display."""
        if not self.player.skills:
            return "You have not learned any skills."
        
        display = "Your Skills:\n"
        for skill in self.player.skills:
            display += f"  - {skill.name}: {skill.description}\n"
        
        display += f"\nSkill points available: {self.player.skill_points}"
        return display

    def learn_skill(self, skill_name: str) -> str:
        """Learn a new skill."""
        if self.player.skill_points <= 0:
            return "You have no skill points to spend."
            
        skill_to_learn = None
        for skill in self.world.skills.values():
            if skill.name.lower() == skill_name.lower():
                skill_to_learn = skill
                break

        if not skill_to_learn:
            return f"There is no skill named '{skill_name}'."
            
        if skill_to_learn in self.player.skills:
            return f"You already know the {skill_to_learn.name} skill."
            
        self.player.skill_points -= 1
        self.player.skills.append(skill_to_learn)
        
        return f"You have learned the {skill_to_learn.name} skill!"

    def save_game(self):
        db = SessionLocal()
        
        # Player state
        player_state = db.query(PlayerState).filter_by(id=1).first()
        if not player_state:
            player_state = PlayerState(id=1)
            db.add(player_state)

        player_state.name = self.player.name
        player_state.location_id = self.player.location_id
        player_state.health = self.player.health
        player_state.max_health = self.player.max_health
        player_state.stamina = self.player.stamina
        player_state.max_stamina = self.player.max_stamina
        player_state.gold = self.player.gold
        player_state.attack = self.player.attack
        player_state.defense = self.player.defense
        player_state.mana = self.player.mana
        player_state.max_mana = self.player.max_mana
        player_state.experience = self.player.experience
        player_state.level = self.player.level
        player_state.skill_points = self.player.skill_points
        player_state.inventory = self.player.inventory
        player_state.equipment = self.player.equipment
        player_state.skills = self.player.skills
        player_state.active_quests = self.player.active_quests
        player_state.completed_quests = self.player.completed_quests
        player_state.visited_locations = self.player.visited_locations
        
        # World state
        for loc_id, location in self.world.locations.items():
            world_state = db.query(WorldState).filter_by(location_id=loc_id).first()
            if not world_state:
                world_state = WorldState(location_id=loc_id)
                db.add(world_state)
            world_state.looted_treasures = location.treasure

        db.commit()
        db.close()
        return "Game saved."

    @staticmethod
    def load_game(world: World) -> Optional[Player]:
        if not os.path.exists("somerpg.db"):
            return None
            
        db = SessionLocal()
        
        player_state = db.query(PlayerState).filter_by(id=1).first()
        if not player_state:
            db.close()
            return None
            
        player = Player(
            name=player_state.name,
            location_id=player_state.location_id,
            health=player_state.health,
            max_health=player_state.max_health,
            stamina=player_state.stamina,
            max_stamina=player_state.max_stamina,
            gold=player_state.gold,
            attack=player_state.attack,
            defense=player_state.defense,
            mana=player_state.mana,
            max_mana=player_state.max_mana,
            experience=player_state.experience,
            level=player_state.level,
            skill_points=player_state.skill_points,
            inventory=player_state.inventory,
            equipment=player_state.equipment,
            skills=player_state.skills,
            active_quests=player_state.active_quests,
            completed_quests=player_state.completed_quests,
            visited_locations=player_state.visited_locations
        )
        
        world_states = db.query(WorldState).all()
        for ws in world_states:
            location = world.get_location(ws.location_id)
            if location:
                location.treasure = ws.looted_treasures
        
        db.close()
        return player
    
