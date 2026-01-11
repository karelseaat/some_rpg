from dataclasses import dataclass, field
from typing import List

@dataclass
class Encounter:
    """Represents an encounter."""
    id: str
    name: str
    description: str
    type: str  # combat, interaction, obstacle
    difficulty: str  # easy, medium, hard
    reward: int
    weaknesses: List[str] = field(default_factory=list)
    resistances: List[str] = field(default_factory=list)
    loot: List[str] = field(default_factory=list)
    loot_chance: float = 0.5
