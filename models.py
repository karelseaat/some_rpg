"""Game world and entity models."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Item:
    """Represents an inventory item."""
    id: str
    name: str
    description: str
    type: str  # consumable, food, tool, treasure, equipment
    value: int
    effect: str
    amount: int = 1  # healing amount or quantity


@dataclass
class NPC:
    """Represents a non-player character."""
    id: str
    name: str
    description: str
    dialogue: str
    location_id: str
    shop: bool = False
    offers_quest: bool = False
    inventory: List[str] = field(default_factory=list)


@dataclass
class Quest:
    """Represents a quest."""
    id: str
    name: str
    description: str
    giver: str  # NPC id
    location: str
    objectives: List[str]
    reward: int
    reward_item: Optional[str] = None
    completed: bool = False


@dataclass
class Encounter:
    """Represents an encounter."""
    id: str
    name: str
    description: str
    type: str  # combat, interaction, obstacle
    difficulty: str  # easy, medium, hard
    reward: int


@dataclass
class Danger:
    """Represents a danger/hazard."""
    id: str
    name: str
    description: str
    damage: int
    escape_difficulty: str


@dataclass
class Location:
    """Represents a location in the world."""
    id: str
    name: str
    description: str
    type: str  # inn, wilderness, settlement, landmark
    exits: Dict[str, str]  # direction -> location_id
    npcs: List[str] = field(default_factory=list)  # NPC ids
    encounters: List[str] = field(default_factory=list)  # Encounter ids
    dangers: List[str] = field(default_factory=list)
    treasure: List[str] = field(default_factory=list)  # Item ids


@dataclass
class Player:
    """Represents the player character."""
    name: str
    location_id: str
    health: int = 100
    max_health: int = 100
    stamina: int = 100
    max_stamina: int = 100
    gold: int = 50
    inventory: List[Item] = field(default_factory=list)
    active_quests: List[str] = field(default_factory=list)
    completed_quests: List[str] = field(default_factory=list)
    experience: int = 0
    level: int = 1

    def take_damage(self, damage: int):
        """Take damage."""
        self.health = max(0, self.health - damage)

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
        self.inventory.append(item)

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

    def gain_experience(self, amount: int):
        """Gain experience and potentially level up."""
        self.experience += amount
        level_threshold = self.level * 100
        if self.experience >= level_threshold:
            self.level_up()

    def level_up(self):
        """Level up the player."""
        self.level += 1
        self.max_health += 10
        self.health = self.max_health
        self.max_stamina += 5
        self.stamina = self.max_stamina


class World:
    """Represents the game world."""

    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.npcs: Dict[str, NPC] = {}
        self.items: Dict[str, Item] = {}
        self.quests: Dict[str, Quest] = {}
        self.encounters: Dict[str, Encounter] = {}
        self.dangers: Dict[str, Danger] = {}
        self.name: str = ""
        self.start_location: str = ""

    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by id."""
        return self.locations.get(location_id)

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get an NPC by id."""
        return self.npcs.get(npc_id)

    def get_item(self, item_id: str) -> Optional[Item]:
        """Get an item by id."""
        return self.items.get(item_id)

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by id."""
        return self.quests.get(quest_id)

    def get_encounter(self, encounter_id: str) -> Optional[Encounter]:
        """Get an encounter by id."""
        return self.encounters.get(encounter_id)

    def get_danger(self, danger_id: str) -> Optional[Danger]:
        """Get a danger by id."""
        return self.dangers.get(danger_id)
