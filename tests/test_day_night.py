import unittest
from systems.inventory import InventorySystem
from models import World, Player, Item, NPC, Location, GameSettings

class TestDayNightMechanics(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.world.settings = GameSettings()
        self.player = Player(name="TestPlayer", password="pass")
        self.inventory_system = InventorySystem(self.world, self.player)
        
        # Setup Location and NPC
        self.market = Location(id="market", name="Market", description="Market", type="settlement", x=0, y=0)
        self.tavern = Location(id="tavern", name="Tavern", description="Tavern", type="inn", x=1, y=0)
        
        self.merchant = NPC(
            id="merchant", name="Merchant", description="Seller",
            dialogue="Buy stuff", shop=True, inventory=["potion"], location_id="market"
        )
        self.bartender = NPC(
            id="bartender", name="Bartender", description="Pourer",
            dialogue="Drink stuff", shop=True, inventory=["ale"], location_id="tavern"
        )
        
        self.potion = Item(id="potion", name="Potion", description="Heal", type="consumable", value=10, effect="heal")
        self.ale = Item(id="ale", name="Ale", description="Drink", type="consumable", value=5, effect="stamina")
        
        self.world.locations["market"] = self.market
        self.world.locations["tavern"] = self.tavern
        self.world.npcs["merchant"] = self.merchant
        self.world.npcs["bartender"] = self.bartender
        self.world.items["potion"] = self.potion
        self.world.items["ale"] = self.ale

    def test_shop_closed_at_night(self):
        # Set time to Night (12+ ticks)
        self.world.time_tick = 15 
        self.assertFalse(self.world.is_day)
        
        # Player at market
        self.player.location_id = "market"
        self.player.gold = 100
        
        success, msg = self.inventory_system.buy_from_npc("Merchant", "Potion")
        
        self.assertFalse(success)
        self.assertIn("closed for the night", msg)

    def test_shop_open_at_day(self):
        # Set time to Day (0-11 ticks)
        self.world.time_tick = 5
        self.assertTrue(self.world.is_day)
        
        # Player at market
        self.player.location_id = "market"
        self.player.gold = 100
        
        success, msg = self.inventory_system.buy_from_npc("Merchant", "Potion")
        
        self.assertTrue(success)
        self.assertIn("bought Potion", msg)

    def test_inn_open_at_night(self):
        # Set time to Night
        self.world.time_tick = 15
        
        # Player at tavern
        self.player.location_id = "tavern"
        self.player.gold = 100
        
        success, msg = self.inventory_system.buy_from_npc("Bartender", "Ale")
        
        self.assertTrue(success)
        self.assertIn("bought Ale", msg)

if __name__ == '__main__':
    unittest.main()
