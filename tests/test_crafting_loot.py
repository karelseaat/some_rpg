import unittest
from unittest.mock import MagicMock, patch
from systems.crafting import CraftingSystem
from systems.combat import CombatSystem
from models import World, Player, Item, Recipe, Enemy

class TestCraftingLoot(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.player = Player(name="TestPlayer", password="pass")
        self.crafting_system = CraftingSystem(self.world, self.player)
        self.combat_system = CombatSystem(self.world, self.player)
        
        # Setup Items
        self.wood = Item(id="wood", name="Wood", description="Wood", type="material", value=1, effect="none")
        self.stone = Item(id="stone", name="Stone", description="Stone", type="material", value=1, effect="none")
        self.axe = Item(id="axe", name="Axe", description="Axe", type="tool", value=10, effect="none")
        
        self.world.items["wood"] = self.wood
        self.world.items["stone"] = self.stone
        self.world.items["axe"] = self.axe
        
        # Setup Recipe
        self.recipe = Recipe(
            id="axe_craft", name="Axe", description="Craft an axe",
            ingredients={"wood": 2, "stone": 1}, result="axe", result_amount=1
        )
        self.world.recipes["axe_craft"] = self.recipe

    def test_craft_success(self):
        # Give ingredients
        self.player.add_item(self.wood)
        self.player.add_item(self.wood)
        self.player.add_item(self.stone)
        
        success, msg = self.crafting_system.craft_item("Axe")
        
        self.assertTrue(success)
        self.assertIn("crafted 1x Axe", msg)
        
        # Check inventory
        self.assertTrue(self.player.has_item("axe"))
        self.assertFalse(self.player.has_item("wood"))
        self.assertFalse(self.player.has_item("stone"))

    def test_craft_fail_missing_ingredients(self):
        # Give partial ingredients
        self.player.add_item(self.wood)
        
        success, msg = self.crafting_system.craft_item("Axe")
        
        self.assertFalse(success)
        self.assertIn("Not enough ingredients", msg)
        
        # Check inventory (should not consume)
        self.assertTrue(self.player.has_item("wood"))

    @patch('random.random')
    def test_get_loot(self, mock_random):
        # Setup Enemy with loot
        enemy = Enemy(
            id="goblin", name="Goblin", description="Goblin",
            health=10, max_health=10, attack=1, defense=1,
            reward_gold=10, reward_exp=10,
            loot_table=["wood"], loot_chance=0.5
        )
        
        # Force drop (random < 0.5)
        mock_random.return_value = 0.1
        
        loot = self.combat_system.get_loot(enemy)
        
        self.assertEqual(len(loot), 1)
        self.assertEqual(loot[0].id, "wood")
        
        # Force no drop (random >= 0.5)
        mock_random.return_value = 0.6
        
        loot = self.combat_system.get_loot(enemy)
        
        self.assertEqual(len(loot), 0)

if __name__ == '__main__':
    unittest.main()
