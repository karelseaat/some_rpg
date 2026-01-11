import random
from typing import Tuple, Optional, List
from models import World, Player, Enemy, Item
from color import color_text, Colors, title

class ExplorationSystem:
    """System for handling movement, location descriptions, and dangers."""

    def __init__(self, world: World, player: Player):
        self.world = world
        self.player = player

    def move_to_location(self, direction: str) -> Tuple[Optional[str], bool]:
        """
        Move player to a location based on direction. 
        Returns (error_message, success).
        """
        current_location = self.world.get_location(self.player.location_id)
        if not current_location:
            return "Error: Current location not found", False

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
            return f"Unknown direction: {direction}", False

        new_location = self.world.get_location_by_coords(target_x, target_y)
        if not new_location:
            return "You can't go that way.", False

        # Cost stamina to travel
        if not self.player.use_stamina(self.world.settings.travel_stamina_cost):
            return "You're too tired to travel. Rest first.", False

        self.player.location_id = new_location.id
        self.player.visited_locations.add(new_location.id)

        return None, True

    def get_location_description(self, game) -> str:
        """Get detailed description of current location."""
        location = self.world.get_location(self.player.location_id)
        if not location:
            return "Unknown location"
        
        time_str = f"[{self.world.time_display}]"
        desc = f"\n{title(f'{location.name} {time_str}', game=game)}\n"
        desc += "-" * (len(location.name) + len(time_str) + 1) + "\n"
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
            desc += "Exits: " + color_text(", ".join(available_exits), Colors.YELLOW, game=game) + "\n"
        
        # List NPCs
        if self.world.features.npcs_enabled and location.npcs:
            desc += f"\nPeople here:\n"
            for npc_id in location.npcs:
                npc = self.world.get_npc(npc_id)
                if npc:
                    desc += f"  - {color_text(npc.name, Colors.BRIGHT_MAGENTA, game=game)}\n"

        # List Items on Ground
        if location.items:
            desc += f"\nItems on the ground:\n"
            for item in location.items:
                desc += f"  - {color_text(item.name, Colors.CYAN, game=game)} (x{item.amount})\n"

        if location.known_dangers:
            desc += "\nYou sense danger here.\n"
                    
        return desc

    def investigate_location(self) -> str:
        """Investigate current location for secrets/items."""
        location = self.world.get_location(self.player.location_id)
        if not location:
            return "There's nothing to investigate here"
        
        if not location.treasure and not any(d.type == 'trap' for d in (self.world.get_danger(d_id) for d_id in location.dangers)):
            return "You search but find nothing of value"

        response = ""
        found_any = False
        
        # Find treasure
        if location.treasure:
            found_items = []
            for treasure_id in location.treasure[:]:  # Iterate over a copy
                item = self.world.get_item(treasure_id)
                if item and random.random() < self.world.settings.investigate_treasure_chance:
                    found_items.append(item)
                    location.treasure.remove(treasure_id)
            
            if found_items:
                response += "Your investigation reveals treasure!\n"
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
                found_any = True

        # Find traps
        if location.dangers:
            dex_bonus = (self.player.dexterity * self.world.settings.disarm_trap_dexterity_bonus)
            for danger_id in location.dangers:
                danger = self.world.get_danger(danger_id)
                if danger and danger.type == 'trap' and danger.id not in location.revealed_dangers:
                    if random.random() < dex_bonus:
                        location.revealed_dangers.add(danger.id)
                        if response: response += "\n"

                        base_chance = self.world.settings.disarm_trap_base_chance.get(danger.escape_difficulty, 0.5)
                        disarm_chance = min(0.95, base_chance + (self.player.dexterity - 5) * self.world.settings.disarm_trap_dexterity_bonus)

                        response += f"You found a {danger.name} trap! Your chance to disarm it is {disarm_chance:.0%}.\n"
                        found_any = True
        
        if not found_any:
            return "You search but find nothing"
        
        return response

    def trigger_danger(self) -> Optional[str]:
        """Trigger a known danger in the current location."""
        location = self.world.get_location(self.player.location_id)
        if not location or not location.known_dangers:
            return None

        danger_id = random.choice(list(location.known_dangers))
        danger = self.world.get_danger(danger_id)
        if danger:
            self.player.take_damage(danger.damage)
            return f"You were hit by a {danger.name} and took {danger.damage} damage!"
        return None

    def trigger_hidden_dangers(self) -> Optional[str]:
        """Trigger a hidden danger in the current location."""
        location = self.world.get_location(self.player.location_id)
        if not location or not location.dangers:
            return None

        # Logic to discover and trigger hidden dangers
        if random.random() < self.world.settings.investigate_treasure_chance: # reusing setting for now
            danger_id = random.choice(location.dangers)
            danger = self.world.get_danger(danger_id)
            if danger and danger.id not in location.revealed_dangers:
                self.player.take_damage(danger.damage)
                location.revealed_dangers.add(danger.id) # Reveal it after it springs
                return f"You sprung a hidden {danger.name} and took {danger.damage} damage!"
        return None

    def disarm_trap(self) -> str:
        """Attempt to disarm a revealed trap in the current location."""
        location = self.world.get_location(self.player.location_id)
        if not location or not location.revealed_dangers:
            return "There are no revealed traps to disarm here."

        trap = None
        for danger_id in location.revealed_dangers:
            danger = self.world.get_danger(danger_id)
            if danger and danger.type == "trap":
                trap = danger
                break
        
        if not trap:
            return "There are no revealed traps to disarm here."

        base_chance = self.world.settings.disarm_trap_base_chance.get(trap.escape_difficulty, 0.5)
        
        # Add a bonus based on dexterity
        dex_bonus = (self.player.dexterity - 5) * self.world.settings.disarm_trap_dexterity_bonus
        disarm_chance = min(0.95, base_chance + dex_bonus)

        if random.random() < disarm_chance:
            location.dangers.remove(trap.id)
            location.revealed_dangers.remove(trap.id)
            return f"You successfully disarmed the {trap.name}!"
        else:
            self.player.take_damage(trap.damage)
            return f"You failed to disarm the {trap.name} and took {trap.damage} damage!"
