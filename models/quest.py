from dataclasses import dataclass
from typing import List, Optional

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
    xp_reward: int = 0
    completed: bool = False
    required_item: Optional[str] = None
    required_item_amount: int = 0
    required_kill: Optional[str] = None
    required_kill_amount: int = 0
