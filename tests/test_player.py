import unittest
from models import Player

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player(name="TestPlayer", password="pass")

    def test_initial_stats(self):
        self.assertEqual(self.player.level, 1)
        self.assertEqual(self.player.experience, 0)
        self.assertEqual(self.player.max_health, 100)

    def test_stat_calculations(self):
        self.player.strength = 10
        self.player.attack = 5
        # Total attack = base (5) + strength (10) = 15
        self.assertEqual(self.player.get_total_attack(), 15)
        
        self.player.dexterity = 10
        self.player.defense = 5
        # Total defense = base (5) + dexterity (10) = 15
        self.assertEqual(self.player.get_total_defense(), 15)

if __name__ == '__main__':
    unittest.main()
