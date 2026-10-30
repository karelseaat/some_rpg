import unittest
from unittest.mock import patch
from models import World, Player, Location, GameSettings, Enemy
from GameEngineFacade import GameEngineFacade as GameEngine

class TestWildernessCamping(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.world.settings = GameSettings()
        self.player = Player(name="TestPlayer", password="pass")
        self.engine = GameEngine(self.world, self.player)
        
        # Setup Locations
        self.forest = Location(id="forest", name="Forest", description="Trees", type="wilderness", x=0, y=0)
        self.forest.encounters = ["wolf"]
        self.world.locations["forest"] = self.forest
        
        # Setup Encounter
        self.world.encounters["wolf"] = type('obj', (object,), {
            "id": "wolf", "name": "Wolf", "description": "A wolf", 
            "type": "combat", "difficulty": "easy", "reward": 10,
            "weaknesses": [], "resistances": [], "loot": [], "loot_chance": 0.5
        })
        
        self.player.location_id = "forest"
        self.player.health = 10
        self.player.stamina = 10

    @patch('random.random')
    @patch('random.choice')
    def test_rest_ambush(self, mock_choice, mock_random):
        # Force ambush (random < 0.3)
        mock_random.return_value = 0.1
        mock_choice.return_value = "wolf"
        
        msg, enemy = self.engine.rest("short")
        
        self.assertIsNotNone(enemy)
        self.assertIn("You try to rest, but...", msg)
        self.assertEqual(enemy.name, "Wolf")
        # Health should NOT have increased
        self.assertEqual(self.player.health, 10)

    @patch('random.random')
    def test_rest_safe_wilderness(self, mock_random):
        # Force safe (random >= 0.3)
        mock_random.return_value = 0.5
        
        msg, enemy = self.engine.rest("short")
        
        self.assertIsNone(enemy)
        self.assertIn("rest uneasily", msg)
        # Health should increase by half of normal (normal is 20, so 10)
        self.assertEqual(self.player.health, 20) # 10 + 10

if __name__ == '__main__':
    unittest.main()
