from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class Item:
    """Represents an inventory item."""
    id: str
    name: str
    description: str
    type: str  # consumable, food, tool, treasure, equipment
    value: int
    effect: str
    amount: int = 1  # quantity
    power: int = 0   # magnitude of effect (e.g. healing amount)
    slot: Optional[str] = None # e.g. weapon, chest
    stats: Dict[str, int] = field(default_factory=dict)
    element: str = "physical"  # physical, fire, ice, etc.
