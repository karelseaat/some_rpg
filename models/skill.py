from dataclasses import dataclass

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
    element: str = "physical"
