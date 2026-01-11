from events import event_bus, Event
from models import Player

class AchievementSystem:
    """System for handling achievements and titles."""

    def __init__(self):
        event_bus.subscribe("level_up", self.on_level_up)
        event_bus.subscribe("quest_completed", self.on_quest_completed)
        event_bus.subscribe("enemy_killed", self.on_enemy_killed)
        
        # Simple in-memory achievement tracking (could be persisted in Player)
        self.achievements = {
            "novice_killer": {"name": "Novice Killer", "desc": "Kill 1 enemy", "condition": lambda p: sum(p.kill_counts.values()) >= 1},
            "veteran_killer": {"name": "Veteran Killer", "desc": "Kill 5 enemies", "condition": lambda p: sum(p.kill_counts.values()) >= 5},
            "level_5": {"name": "Rising Star", "desc": "Reach Level 5", "condition": lambda p: p.level >= 5},
            "quest_master": {"name": "Quest Master", "desc": "Complete 3 quests", "condition": lambda p: len(p.completed_quests) >= 3},
        }

    def check_achievements(self, player: Player):
        """Check if player earned any new achievements."""
        # In a real system, we'd store earned achievements in the player model
        # For now, we'll just check and emit a notification if condition is met
        # This is a simplified demo implementation
        
        total_kills = sum(player.kill_counts.values())
        
        if total_kills == 1:
            self.notify(player, "Achievement Unlocked: Novice Killer (First Blood!)")
        elif total_kills == 5:
            self.notify(player, "Achievement Unlocked: Veteran Killer (5 Kills)")
            
        if player.level == 5:
            self.notify(player, "Achievement Unlocked: Rising Star (Level 5)")
            
        if len(player.completed_quests) == 3:
            self.notify(player, "Achievement Unlocked: Quest Master (3 Quests)")

    def on_level_up(self, event: Event):
        player = event.data["player"]
        level = event.data["level"]
        self.notify(player, f"*** LEVEL UP! You are now level {level} ***")
        self.check_achievements(player)

    def on_quest_completed(self, event: Event):
        player = event.data["player"]
        quest_name = event.data["quest_name"]
        self.notify(player, f"*** Quest Completed: {quest_name} ***")
        self.check_achievements(player)

    def on_enemy_killed(self, event: Event):
        player = event.data["player"]
        self.check_achievements(player)

    def notify(self, player: Player, message: str):
        """Publish a notification event."""
        event_bus.publish(Event("notification", {
            "player_name": player.name,
            "message": message
        }))
