import unittest
from systems.exploration import ExplorationSystem
from models import World, Player, Location, GameSettings

class TestExplorationSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.world.settings = GameSettings()
        self.player = Player(name="TestPlayer", password="pass")
        self.exploration_system = ExplorationSystem(self.world, self.player)
        
        # Setup a simple map
        # [Loc1 (0,0)] -- East --> [Loc2 (1,0)]
        self.loc1 = Location(id="loc1", name="Start", description="Start here", type="wilderness", x=0, y=0)
        self.loc2 = Location(id="loc2", name="End", description="End here", type="wilderness", x=1, y=0)
        
        self.world.locations["loc1"] = self.loc1
        self.world.locations["loc2"] = self.loc2
        
        self.player.location_id = "loc1"

    def test_move_success(self):
        err, success = self.exploration_system.move_to_location("east")
        
        self.assertTrue(success)
        self.assertIsNone(err)
        self.assertEqual(self.player.location_id, "loc2")
        self.assertEqual(self.player.stamina, 90) # 100 - 10 cost

    def test_move_blocked(self):
        err, success = self.exploration_system.move_to_location("north")
        
        self.assertFalse(success)
        self.assertEqual(err, "You can't go that way.")
        self.assertEqual(self.player.location_id, "loc1")
        self.assertEqual(self.player.stamina, 100) # No cost for failed move

    def test_move_no_stamina(self):
        self.player.stamina = 5
        
        err, success = self.exploration_system.move_to_location("east")
        
        self.assertFalse(success)
        self.assertIn("too tired", err)
        self.assertEqual(self.player.location_id, "loc1")

if __name__ == '__main__':
    unittest.main()
