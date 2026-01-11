from dataclasses import dataclass
from typing import Dict

@dataclass
class Recipe:
    """Represents a crafting recipe."""
    id: str
    name: str
    description: str
    ingredients: Dict[str, int]  # item_id: quantity
    result: str  # item_id
    result_amount: int = 1
