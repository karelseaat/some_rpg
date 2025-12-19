"""Game world and entity models."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set


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
    slot: Optional[str] = None # e.g. weapon, chest
    stats: Dict[str, int] = field(default_factory=dict)


@dataclass
class Skill:
    """Represents a skill."""
    id: str
    name: str
    description: str
    type: str  # combat, utility
    cost: int  # mana cost
    effect: str
    value: int


@dataclass
class Features:
    """Represents game features that can be enabled/disabled."""
    npcs_enabled: bool = True
    enemies_enabled: bool = True
    traders_enabled: bool = True


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
class Enemy:
    """Represents an enemy in combat."""
    id: str
    name: str
    description: str
    health: int
    max_health: int
    attack: int
    defense: int
    reward_gold: int
    reward_exp: int


@dataclass
class Danger:
    """Represents a danger/hazard."""
    id: str
    name: str
    description: str
    type: str  # trap
    damage: Optional[int] = None
    escape_difficulty: Optional[str] = None


@dataclass
class Location:
    """Represents a location in the world."""
    id: str
    name: str
    description: str
    type: str  # inn, wilderness, settlement, landmark
    x: int = 0
    y: int = 0
    npcs: List[str] = field(default_factory=list)  # NPC ids
    encounters: List[str] = field(default_factory=list)  # Encounter ids
    dangers: List[str] = field(default_factory=list)
    treasure: List[str] = field(default_factory=list)  # Item ids
    revealed_dangers: Set[str] = field(default_factory=set)
    known_dangers: Set[str] = field(default_factory=set)


@dataclass
class Player:
    """Represents the player character."""
    name: str
    password: str
    location_id: str
    health: int = 100
    max_health: int = 100
    stamina: int = 100
    max_stamina: int = 100
    mana: int = 50
    max_mana: int = 50
    gold: int = 50
    strength: int = 5
    dexterity: int = 5
    intelligence: int = 5
    attack: int = 1
    defense: int = 0
    inventory: List[Item] = field(default_factory=list)
    equipment: Dict[str, Item] = field(default_factory=dict)
    skills: List[Skill] = field(default_factory=list)
    skill_points: int = 0
    attribute_points: int = 0
    active_quests: List[str] = field(default_factory=list)
    completed_quests: List[str] = field(default_factory=list)
    experience: int = 0
    level: int = 1
    visited_locations: Set[str] = field(default_factory=set)

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
                inv_item.amount += 1
                return
        
        # Add new item as a copy
        new_item = Item(
            id=item.id,
            name=item.name,
            description=item.description,
            type=item.type,
            value=item.value,
            effect=item.effect,
            amount=1,
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

    def gain_experience(self, amount: int):
        """Gain experience and potentially level up."""
        self.experience += amount
        level_threshold = self.level * 100
        if self.experience >= level_threshold:
            self.level_up()

    def use_mana(self, amount: int) -> bool:
        """Use mana, return True if successful."""
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False

    def restore_mana(self, amount: int):
        """Restore mana."""
        self.mana = min(self.max_mana, self.mana + amount)

    def level_up(self):
        """Level up the player."""
        self.level += 1
        self.max_health += 10
        self.health = self.max_health
        self.max_stamina += 5
        self.stamina = self.max_stamina
        self.max_mana += 5
        self.mana = self.max_mana
        self.skill_points += 1
        self.attribute_points += 3


@dataclass
class GameSettings:
    """Represents game settings."""
    travel_stamina_cost: int = 10
    encounter_chance: float = 0.25
    danger_chance: float = 0.15
    investigate_treasure_chance: float = 0.7
    rest_short_health_gain: int = 20
    rest_short_stamina_gain: int = 30
    disarm_trap_dexterity_bonus: float = 0.05
    disarm_trap_base_chance: Dict[str, float] = field(default_factory=lambda: {"easy": 0.8, "medium": 0.5, "hard": 0.2})
    difficulty_multipliers: Dict[str, int] = field(default_factory=lambda: {"easy": 1, "medium": 2, "hard": 3})
    enemy_health_multiplier: int = 20
    enemy_attack_multiplier: int = 5
    enemy_defense_multiplier: int = 2


class World:
    """Represents the game world."""

    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.npcs: Dict[str, NPC] = {}
        self.items: Dict[str, Item] = {}
        self.skills: Dict[str, Skill] = {}
        self.quests: Dict[str, Quest] = {}
        self.encounters: Dict[str, Encounter] = {}
        self.dangers: Dict[str, Danger] = {}
        self.name: str = ""
        self.start_location: str = ""
        self.start_inventory: Dict[str, int] = {}
        self.features: Features = Features()
        self.settings: GameSettings = GameSettings()

    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by id."""
        return self.locations.get(location_id)

    def get_location_by_coords(self, x: int, y: int) -> Optional[Location]:
        """Get a location by coordinates."""
        for location in self.locations.values():
            if location.x == x and location.y == y:
                return location
        return None

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get an NPC by id."""
        return self.npcs.get(npc_id)

    def get_item(self, item_id: str) -> Optional[Item]:
        """Get an item by id."""
        return self.items.get(item_id)

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get a skill by id."""
        return self.skills.get(skill_id)

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by id."""
        return self.quests.get(quest_id)

    def get_encounter(self, encounter_id: str) -> Optional[Encounter]:
        """Get an encounter by id."""
        return self.encounters.get(encounter_id)

    def get_danger(self, danger_id: str) -> Optional[Danger]:
        """Get a danger by id."""
        return self.dangers.get(danger_id)
