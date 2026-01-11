import unittest
from models import World, Player, GameSettings
from systems.progression import ProgressionSystem
from events import event_bus, Event

class TestProgressionSystem(unittest.TestCase):
    def setUp(self):
        event_bus.clear()
        self.world = World()
        self.world.settings = GameSettings()
        # Set simple progression settings for testing
        self.world.settings.base_xp_threshold = 100
        self.world.settings.xp_multiplier_per_level = 1.0
        self.world.settings.health_per_level = 10
        
        self.player = Player(name="TestPlayer", password="pass")
        self.progression_system = ProgressionSystem(self.world)
        
        self.level_up_events = []
        def on_level_up(event):
            self.level_up_events.append(event.data)
        event_bus.subscribe("level_up", on_level_up)

    def test_xp_threshold(self):
        # Level 1 -> 2 needs 100 * 1 * 1.0 = 100 XP
        self.assertEqual(self.progression_system.get_xp_threshold(1), 100)
        # Level 2 -> 3 needs 100 * 2 * 1.0 = 200 XP
        self.assertEqual(self.progression_system.get_xp_threshold(2), 200)

    def test_add_experience_no_level_up(self):
        self.progression_system.add_experience(self.player, 50)
        self.assertEqual(self.player.experience, 50)
        self.assertEqual(self.player.level, 1)
        self.assertEqual(len(self.level_up_events), 0)

    def test_add_experience_level_up(self):
        # Need 100 XP to level up
        self.progression_system.add_experience(self.player, 100)
        
        self.assertEqual(self.player.experience, 100)
        self.assertEqual(self.player.level, 2)
        self.assertEqual(len(self.level_up_events), 1)
        self.assertEqual(self.level_up_events[0]["level"], 2)
        
        # Check stats increase
        self.assertEqual(self.player.max_health, 110) # 100 + 10
        self.assertEqual(self.player.health, 110)

    def test_multiple_level_ups(self):
        # Level 1->2 needs 100. Level 2->3 needs 200. Total 300.
        # If we give 350 XP, should reach level 4 (350 >= 300).
        self.progression_system.add_experience(self.player, 350)
        
        self.assertEqual(self.player.level, 4)
        # Should trigger level up for 2, 3, 4
        self.assertEqual(len(self.level_up_events), 3)

    def test_quest_xp_event(self):
        # Simulate quest completion event
        event_bus.publish(Event("quest_completed", {
            "player": self.player,
            "quest_id": "q1",
            "quest_name": "Test Quest",
            "xp_reward": 150
        }))
        
        # Should level up (150 > 100)
        self.assertEqual(self.player.level, 2)
        self.assertEqual(self.player.experience, 150)

if __name__ == '__main__':
    unittest.main()
