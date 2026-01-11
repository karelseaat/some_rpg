import unittest
from models import Player
from systems.achievements import AchievementSystem
from events import event_bus, Event

class TestEventSystem(unittest.TestCase):
    def setUp(self):
        self.player = Player(name="TestPlayer", password="pass")
        self.achievement_system = AchievementSystem()
        self.notifications = []
        
        # Mock notification listener
        def on_notification(event):
            self.notifications.append(event.data)
        
        event_bus.subscribe("notification", on_notification)

    def test_level_up_event(self):
        # Trigger level up
        self.player.level = 5
        event_bus.publish(Event("level_up", {"player": self.player, "level": self.player.level}))
        
        # Check if achievement system caught it
        # It should publish a notification
        
        # We need to check if "Rising Star" achievement was unlocked
        # The notification listener should have received it
        
        found_achievement = False
        for note in self.notifications:
            if "Rising Star" in note["message"]:
                found_achievement = True
                break
        
        self.assertTrue(found_achievement, "Achievement notification not received")

    def test_quest_completed_event(self):
        # Simulate quest completion event directly
        event_bus.publish(Event("quest_completed", {
            "player": self.player,
            "quest_id": "q1",
            "quest_name": "Test Quest"
        }))
        
        # Check for quest completion notification
        found_msg = False
        for note in self.notifications:
            if "Quest Completed: Test Quest" in note["message"]:
                found_msg = True
                break
        self.assertTrue(found_msg)

if __name__ == '__main__':
    unittest.main()
