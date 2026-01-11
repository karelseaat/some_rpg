from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from .item import Item
from .skill import Skill
from events import event_bus, Event

@dataclass
class Player:
    """Represents the player."""
    name: str
    password: str
    location_id: str = "tavern"
    health: int = 100
    max_health: int = 100
    stamina: int = 100
    max_stamina: int = 100
    gold: int = 10
    strength: int = 10
    dexterity: int = 10
    intelligence: int = 10
    attack: int = 5
    defense: int = 5
    mana: int = 20
    max_mana: int = 20
    experience: int = 0
    level: int = 1
    skill_points: int = 0
    attribute_points: int = 0
    inventory: List[Item] = field(default_factory=list)
    equipment: Dict[str, Item] = field(default_factory=dict)
    skills: List[Skill] = field(default_factory=list)
    active_quests: List[str] = field(default_factory=list)
    completed_quests: List[str] = field(default_factory=list)
    visited_locations: Set[str] = field(default_factory=lambda: {"tavern"})
    kill_counts: Dict[str, int] = field(default_factory=dict)
    use_color: bool = True

    def get_total_attack(self) -> int:
        """Calculate total attack from base stats and equipment."""
        total = self.attack + self.strength
        for item in self.equipment.values():
            if item.stats and "attack" in item.stats:
                total += item.stats["attack"]
        return total

    def get_total_defense(self) -> int:
        """Calculate total defense from base stats and equipment."""
        total = self.defense + self.dexterity
        for item in self.equipment.values():
            if item.stats and "defense" in item.stats:
                total += item.stats["defense"]
        return total

    def take_damage(self, damage: int):
        """Take damage."""
        damage_taken = max(0, damage - self.get_total_defense())
        self.health = max(0, self.health - damage_taken)

    def heal(self, amount: int):
        """Heal health."""
        self.health = min(self.max_health, self.health + amount)

    def use_stamina(self, amount: int) -> bool:
        """Use stamina, return True if successful."""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False

    def restore_stamina(self, amount: int):
        """Restore stamina."""
        self.stamina = min(self.max_stamina, self.stamina + amount)

    def add_gold(self, amount: int):
        """Add gold."""
        self.gold += amount

    def spend_gold(self, amount: int) -> bool:
        """Spend gold, return True if successful."""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def add_item(self, item: Item):
        """Add item to inventory."""
        # Check if item already in inventory
        for inv_item in self.inventory:
            if inv_item.id == item.id:
                inv_item.amount += item.amount
                return
        
        # Add new item as a copy
        new_item = Item(
            id=item.id,
            name=item.name,
            description=item.description,
            type=item.type,
            value=item.value,
            effect=item.effect,
            amount=item.amount,
            slot=item.slot,
            stats=item.stats.copy() if item.stats else {}
        )
        self.inventory.append(new_item)

    def remove_item(self, item_id: str) -> Optional[Item]:
        """Remove item from inventory."""
        for i, item in enumerate(self.inventory):
            if item.id == item_id:
                removed = self.inventory.pop(i)
                return removed
        return None

    def has_item(self, item_id: str) -> bool:
        """Check if player has item."""
        return any(item.id == item_id for item in self.inventory)

    def use_mana(self, amount: int) -> bool:
        """Use mana, return True if successful."""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False

    def restore_mana(self, amount: int):
        """Restore mana."""
        self.mana = min(self.max_mana, self.mana + amount)
