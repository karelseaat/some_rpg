import unittest
from unittest.mock import MagicMock, AsyncMock
from session_manager import SessionManager, Session
from commands import handle_say, handle_yell, handle_give
from models import Item

class TestMultiplayer(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Reset singleton
        self.session_manager = SessionManager()
        self.session_manager.sessions = []
        
        # Mock Game 1 (Alice)
        self.game1 = MagicMock()
        self.game1.player.name = "Alice"
        self.game1.player.location_id = "town"
        self.game1.player.inventory = []
        self.game1.player.remove_item = MagicMock()
        self.game1.player.use_color = False
        
        self.sender1 = AsyncMock()
        self.session1 = Session("Alice", self.game1, self.sender1)
        self.session_manager.add_session(self.session1)
        
        # Mock Game 2 (Bob)
        self.game2 = MagicMock()
        self.game2.player.name = "Bob"
        self.game2.player.location_id = "town"
        self.game2.player.inventory = []
        self.game2.player.add_item = MagicMock()
        self.game2.player.use_color = False
        
        self.sender2 = AsyncMock()
        self.session2 = Session("Bob", self.game2, self.sender2)
        self.session_manager.add_session(self.session2)
        
        # Mock Game 3 (Charlie) - Different location
        self.game3 = MagicMock()
        self.game3.player.name = "Charlie"
        self.game3.player.location_id = "forest"
        self.game3.player.use_color = False
        
        self.sender3 = AsyncMock()
        self.session3 = Session("Charlie", self.game3, self.sender3)
        self.session_manager.add_session(self.session3)

    async def test_say(self):
        # Alice says something in town
        await handle_say(self.game1, ["Hello", "world"])
        
        # Bob (in town) should hear it
        self.sender2.send.assert_called_once()
        args, _ = self.sender2.send.call_args
        self.assertIn("Alice says: Hello world", args[0])
        
        # Charlie (in forest) should NOT hear it
        self.sender3.send.assert_not_called()

    async def test_yell(self):
        # Alice yells
        await handle_yell(self.game1, ["Help!"])
        
        # Everyone should hear it
        self.sender2.send.assert_called_once()
        self.assertIn("Alice yells: Help!", self.sender2.send.call_args[0][0])
        
        self.sender3.send.assert_called_once()
        self.assertIn("Alice yells: Help!", self.sender3.send.call_args[0][0])

    async def test_give_success(self):
        # Setup item
        item = Item(id="potion", name="Potion", description="Heal", type="consumable", value=10, effect="heal")
        self.game1.player.inventory = [item]
        
        # Alice gives potion to Bob
        response = await handle_give(self.game1, ["Bob", "Potion"])
        
        self.assertIn("You gave Potion to Bob", response)
        
        # Check transfer
        self.game1.player.remove_item.assert_called_with("potion")
        self.game2.player.add_item.assert_called_with(item)
        
        # Check notification
        self.sender2.send.assert_called_once()
        self.assertIn("Alice gave you Potion", self.sender2.send.call_args[0][0])

    async def test_give_fail_not_found(self):
        response = await handle_give(self.game1, ["Dave", "Potion"])
        self.assertIn("Player Dave not found", response)

    async def test_give_fail_wrong_location(self):
        item = Item(id="potion", name="Potion", description="Heal", type="consumable", value=10, effect="heal")
        self.game1.player.inventory = [item]
        
        response = await handle_give(self.game1, ["Charlie", "Potion"])
        self.assertIn("Charlie is not here", response)

    async def test_give_fail_no_item(self):
        response = await handle_give(self.game1, ["Bob", "Sword"])
        self.assertIn("You don't have 'Sword'", response)

if __name__ == '__main__':
    unittest.main()
