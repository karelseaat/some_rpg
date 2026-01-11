from typing import Tuple, Optional, List
from models import World, Player, Item, NPC

class InventorySystem:
    """System for handling items, inventory, and trading."""

    def __init__(self, world: World, player: Player):
        self.world = world
        self.player = player

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

    def use_item(self, item_identifier: str) -> Tuple[bool, str]:
        """Use an item from inventory by ID or name. Returns (success, message)."""
        item_to_use = self._find_item_by_name_or_id(item_identifier)

        if not item_to_use:
            return False, "You can't find an item like that."

        # Check if the player has this item
        player_item = None
        for inv_item in self.player.inventory:
            if inv_item.id == item_to_use.id:
                player_item = inv_item
                break

        if not player_item:
            return False, "You don't have that item."
        
        if player_item.type == "consumable":
            amount_to_restore = item_to_use.power if item_to_use.power > 0 else item_to_use.amount
            if player_item.effect == "heal":
                self.player.heal(amount_to_restore)
                response = f"You drink the {player_item.name} and feel {amount_to_restore} health restored"
                player_item.amount -= 1
                if player_item.amount <= 0:
                    self.player.remove_item(player_item.id)
                return True, response
            elif player_item.effect == "stamina":
                self.player.restore_stamina(amount_to_restore)
                response = f"You consume the {player_item.name} and regain {amount_to_restore} stamina"
                player_item.amount -= 1
                if player_item.amount <= 0:
                    self.player.remove_item(player_item.id)
                return True, response
        
        elif player_item.type == "food":
            amount_to_restore = item_to_use.power if item_to_use.power > 0 else item_to_use.amount
            if player_item.effect == "heal":
                self.player.heal(amount_to_restore)
                response = f"You eat the {player_item.name} and feel {amount_to_restore} health restored"
                player_item.amount -= 1
                if player_item.amount <= 0:
                    self.player.remove_item(player_item.id)
                return True, response
        
        return False, f"You cannot use {player_item.name}"

    def equip_item(self, item_name: str) -> Tuple[bool, str]:
        """Equip an item from inventory. Returns (success, message)."""
        item_to_equip = None
        for item in self.player.inventory:
            if item.name.lower() == item_name.lower():
                item_to_equip = item
                break
        
        if not item_to_equip:
            return False, f"You don't have a {item_name}."
            
        if not item_to_equip.slot:
            return False, f"You can't equip {item_to_equip.name}."
            
        # Check if there is already an item in that slot
        if item_to_equip.slot in self.player.equipment:
            # Unequip the old item first
            self.unequip_item(item_to_equip.slot)
            
        # Equip the new item
        self.player.inventory.remove(item_to_equip)
        self.player.equipment[item_to_equip.slot] = item_to_equip
        
        return True, f"You equipped the {item_to_equip.name}."

    def unequip_item(self, slot: str) -> Tuple[bool, str]:
        """Unequip an item from a slot. Returns (success, message)."""
        if slot not in self.player.equipment:
            return False, f"You have nothing equipped in the {slot} slot."
            
        item_to_unequip = self.player.equipment.pop(slot)
        self.player.add_item(item_to_unequip)
        
        return True, f"You unequipped the {item_to_unequip.name}."

    def buy_from_npc(self, npc_identifier: str, item_identifier: str) -> Tuple[bool, str]:
        """Buy an item from an NPC by ID or name. Returns (success, message)."""
        if not self.world.features.traders_enabled:
            return False, "Trading is disabled in this world."

        npc = self._find_npc_by_name(npc_identifier)
        if not npc or not npc.shop:
            return False, "This NPC doesn't sell items"

        # Night-time restriction: Shops in settlements close at night
        location = self.world.get_location(self.player.location_id)
        if not self.world.is_day and location and location.type == "settlement":
            return False, f"{npc.name} is closed for the night. Come back in the morning."

        item = self._find_item_by_name_or_id(item_identifier)
        if not item:
            return False, "That item doesn't exist."

        if item.id not in npc.inventory:
            return False, "They don't have that item"
        
        if not self.player.spend_gold(item.value):
            return False, f"You don't have enough gold (costs {item.value})"
        
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
        return True, f"You bought {item.name} for {item.value} gold"

    def buy_item_from_npc_by_name(self, name_parts: List[str]) -> Tuple[bool, str]:
        """Buy an item from an NPC, parsing multi-word names. Returns (success, message)."""
        if not name_parts or len(name_parts) < 2:
            return False, "Usage: buy <npc name> <item name>"

        # Iterate through all possible split points
        for i in range(1, len(name_parts)):
            npc_name_guess = " ".join(name_parts[:i])
            item_name_guess = " ".join(name_parts[i:])

            npc = self._find_npc_by_name(npc_name_guess)
            item = self._find_item_by_name_or_id(item_name_guess)

            if npc and item and npc.shop and item.id in npc.inventory:
                # Found a valid combination, proceed with purchase
                return self.buy_from_npc(npc.id, item.id)

        return False, "Could not find a valid NPC and item combination to buy."

    def get_inventory_display(self) -> str:
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
            inv += f"  - {slot.capitalize()}: {item.name}\n"
            
        return inv

    def drop_item(self, item_identifier: str, amount: int = 1) -> Tuple[bool, str]:
        """Drop an item from inventory to the ground."""
        # Find item in inventory
        player_item = None
        for inv_item in self.player.inventory:
            if inv_item.id == item_identifier or inv_item.name.lower() == item_identifier.lower():
                player_item = inv_item
                break
        
        if not player_item:
            return False, "You don't have that item."
            
        if player_item.amount < amount:
            return False, f"You don't have enough {player_item.name}."
            
        # Create item to drop
        dropped_item = Item(
            id=player_item.id,
            name=player_item.name,
            description=player_item.description,
            type=player_item.type,
            value=player_item.value,
            effect=player_item.effect,
            amount=amount,
            slot=player_item.slot,
            stats=player_item.stats.copy() if player_item.stats else {},
            element=player_item.element
        )
        
        # Remove from inventory
        player_item.amount -= amount
        if player_item.amount <= 0:
            self.player.inventory.remove(player_item)
            
        # Add to location
        location = self.world.get_location(self.player.location_id)
        if location:
            # Check if item already on ground to merge
            merged = False
            for ground_item in location.items:
                if ground_item.id == dropped_item.id:
                    ground_item.amount += amount
                    merged = True
                    break
            
            if not merged:
                location.items.append(dropped_item)
                
        return True, f"You dropped {amount}x {dropped_item.name}."

    def pickup_item(self, item_identifier: str) -> Tuple[bool, str]:
        """Pick up an item from the ground."""
        location = self.world.get_location(self.player.location_id)
        if not location:
            return False, "You are nowhere."
            
        # Find item on ground
        ground_item = None
        for item in location.items:
            if item.id == item_identifier or item.name.lower() == item_identifier.lower():
                ground_item = item
                break
                
        if not ground_item:
            return False, "You don't see that here."
            
        # Add to inventory
        self.player.add_item(ground_item)
        
        # Remove from ground
        location.items.remove(ground_item)
        
        return True, f"You picked up {ground_item.name}."
