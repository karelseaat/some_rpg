from dataclasses import dataclass

@dataclass
class Features:
    """Represents game features that can be enabled/disabled."""
    npcs_enabled: bool = True
    enemies_enabled: bool = True
    traders_enabled: bool = True
