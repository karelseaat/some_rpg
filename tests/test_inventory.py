import unittest
from systems.inventory import InventorySystem
from models import World, Player, Item, GameSettings

class TestInventorySystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.world.settings = GameSettings()
        self.player = Player(name="TestPlayer", password="pass")
        self.inventory_system = InventorySystem(self.world, self.player)
        
        # Create some test items
        self.potion = Item(
            id="potion", name="Health Potion", description="Heals 20",
            type="consumable", value=10, effect="heal", amount=1, power=20
        )
        self.sword = Item(
            id="sword", name="Iron Sword", description="Sharp",
            type="equipment", value=50, effect="none", slot="weapon",
            stats={"attack": 10}
        )
        self.world.items["potion"] = self.potion
        self.world.items["sword"] = self.sword

    def test_add_item(self):
        self.player.add_item(self.potion)
        self.assertEqual(len(self.player.inventory), 1)
        self.assertEqual(self.player.inventory[0].id, "potion")
        
        # Test stacking
        self.player.add_item(self.potion)
        self.assertEqual(len(self.player.inventory), 1)
        self.assertEqual(self.player.inventory[0].amount, 2)

    def test_use_consumable(self):
        self.player.health = 50
        self.player.add_item(self.potion)
        
        success, msg = self.inventory_system.use_item("Health Potion")
        
        self.assertTrue(success)
        self.assertEqual(self.player.health, 70) # 50 + 20
        self.assertEqual(len(self.player.inventory), 0) # Should be consumed

    def test_equip_item(self):
        self.player.add_item(self.sword)
        
        success, msg = self.inventory_system.equip_item("Iron Sword")
        
        self.assertTrue(success)
        self.assertIn("weapon", self.player.equipment)
        self.assertEqual(self.player.equipment["weapon"].id, "sword")
        self.assertEqual(len(self.player.inventory), 0) # Moved from inventory to equipment
        
        # Check stats update
        # Base attack (5) + Strength (10) + Sword (10) = 25
        self.assertEqual(self.player.get_total_attack(), 25)

    def test_unequip_item(self):
        self.player.equipment["weapon"] = self.sword
        
        success, msg = self.inventory_system.unequip_item("weapon")
        
        self.assertTrue(success)
        self.assertNotIn("weapon", self.player.equipment)
        self.assertEqual(len(self.player.inventory), 1)
        self.assertEqual(self.player.inventory[0].id, "sword")

if __name__ == '__main__':
    unittest.main()
