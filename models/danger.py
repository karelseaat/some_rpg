from dataclasses import dataclass
from typing import Optional

@dataclass
class Danger:
    """Represents a danger/hazard."""
    id: str
    name: str
    description: str
    type: str  # trap
    damage: Optional[int] = None
    escape_difficulty: Optional[str] = None
