from dataclasses import dataclass, field
from typing import Dict

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
    
    # Combat formulas
    base_crit_chance: float = 0.05
    dexterity_crit_bonus: float = 0.005
    crit_multiplier: float = 1.5
    elemental_weakness_multiplier: float = 1.5
    elemental_resistance_multiplier: float = 0.5
    
    # Progression
    base_xp_threshold: int = 100
    xp_multiplier_per_level: float = 1.0
    health_per_level: int = 10
    stamina_per_level: int = 5
    mana_per_level: int = 5
    skill_points_per_level: int = 1
    attribute_points_per_level: int = 3
