from dataclasses import dataclass, field
from typing import List

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
    weaknesses: List[str] = field(default_factory=list)
    resistances: List[str] = field(default_factory=list)
    loot_table: List[str] = field(default_factory=list)
    loot_chance: float = 0.5
