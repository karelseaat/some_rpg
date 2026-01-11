from dataclasses import dataclass, field
from typing import List, Set
from .item import Item

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
    items: List[Item] = field(default_factory=list)  # Items on the ground
    revealed_dangers: Set[str] = field(default_factory=set)
    known_dangers: Set[str] = field(default_factory=set)
