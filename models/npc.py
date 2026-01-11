from dataclasses import dataclass, field
from typing import List

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
