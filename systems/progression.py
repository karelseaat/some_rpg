from models import Player, World
from events import event_bus, Event

class ProgressionSystem:
    """System for handling player progression (XP, leveling)."""

    def __init__(self, world: World):
        self.world = world
        self.setup_listeners()

    def setup_listeners(self):
        """Subscribe to events."""
        event_bus.subscribe("quest_completed", self.on_quest_completed)
        # We can also listen to enemy_killed if we want to decouple combat XP
        # But server.py currently handles it. Let's leave server.py for now or refactor it too?
        # The user asked for data-driven loot/gameplay.
        # Let's stick to quest for now as I just did it.

    def on_quest_completed(self, event: Event):
        """Handle quest completion XP."""
        player = event.data.get("player")
        xp = event.data.get("xp_reward", 0)
        if player and xp > 0:
            self.add_experience(player, xp)

    def add_experience(self, player: Player, amount: int):
        """Add experience to player and handle leveling."""
        player.experience += amount
        
        while True:
            threshold = self.get_xp_threshold(player.level)
            if player.experience >= threshold:
                self.level_up(player)
            else:
                break

    def get_xp_threshold(self, level: int) -> int:
        """Calculate XP needed for next level."""
        settings = self.world.settings
        # Linear: base * level * multiplier
        # The original was level * 100.
        # Let's use: base_xp_threshold * level * xp_multiplier_per_level
        return int(settings.base_xp_threshold * level * settings.xp_multiplier_per_level)

    def level_up(self, player: Player):
        """Level up the player using settings."""
        settings = self.world.settings
        
        player.level += 1
        player.max_health += settings.health_per_level
        player.health = player.max_health
        player.max_stamina += settings.stamina_per_level
        player.stamina = player.max_stamina
        player.max_mana += settings.mana_per_level
        player.mana = player.max_mana
        player.skill_points += settings.skill_points_per_level
        player.attribute_points += settings.attribute_points_per_level
        
        event_bus.publish(Event("level_up", {"player": player, "level": player.level}))
