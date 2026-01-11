import unittest
from systems.quest import QuestSystem
from models import World, Player, NPC, Quest, GameSettings

class TestQuestSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.world.settings = GameSettings()
        self.player = Player(name="TestPlayer", password="pass")
        self.quest_system = QuestSystem(self.world, self.player)
        
        # Setup NPC and Quest
        self.npc = NPC(
            id="mayor", name="Mayor", description="The Mayor",
            dialogue="Hello hero!", location_id="town",
            offers_quest="rat_problem"
        )
        self.quest = Quest(
            id="rat_problem", name="Rat Problem", description="Kill rats",
            giver="mayor", location="sewers", objectives=["Kill 5 rats"],
            reward=100, required_item="rat_tail", required_item_amount=5
        )
        
        self.world.npcs["mayor"] = self.npc
        self.world.quests["rat_problem"] = self.quest
        
        # Add required item to world items so it can be looked up
        from models import Item
        self.world.items["rat_tail"] = Item(id="rat_tail", name="Rat Tail", description="Tail of a rat", type="junk", value=1, effect="none")

    def test_talk_to_npc(self):
        # Mock game object with player.use_color
        class DummyPlayer:
            use_color = False
            
        class DummyGame:
            player = DummyPlayer()
            
        response = self.quest_system.talk_to_npc(DummyGame(), "Mayor")
        
        self.assertIn("Mayor", response)
        self.assertIn("Hello hero!", response)
        self.assertIn("Rat Problem", response)

    def test_accept_quest_success(self):
        response = self.quest_system.accept_quest("rat_problem")
        
        self.assertIn("Quest accepted", response)
        self.assertIn("rat_problem", self.player.active_quests)

    def test_accept_quest_already_active(self):
        self.player.active_quests.append("rat_problem")
        
        response = self.quest_system.accept_quest("rat_problem")
        
        self.assertEqual(response, "You already have this quest")
        self.assertEqual(len(self.player.active_quests), 1)

    def test_accept_quest_from_npc(self):
        response = self.quest_system.accept_quest_from_npc("Mayor")
        
        self.assertIn("Quest accepted", response)
        self.assertIn("rat_problem", self.player.active_quests)

    def test_accept_quest_from_npc_no_quest(self):
        self.npc.offers_quest = False
        
        response = self.quest_system.accept_quest_from_npc("Mayor")
        
        self.assertIn("has no quest", response)
        self.assertEqual(len(self.player.active_quests), 0)

    def test_complete_quest_success(self):
        self.player.active_quests.append("rat_problem")
        # Player is at "tavern" by default. Mayor is at "town".
        # Update player location to match NPC
        self.player.location_id = "town"
        
        # Give player required items
        from models import Item
        self.player.add_item(Item(id="rat_tail", name="Rat Tail", description="Tail", type="junk", value=1, effect="none", amount=5))
        
        response = self.quest_system.complete_quest("rat_problem")
        
        self.assertIn("Quest Completed", response)
        self.assertIn("100 gold", response)
        self.assertNotIn("rat_problem", self.player.active_quests)
        self.assertIn("rat_problem", self.player.completed_quests)
        self.assertEqual(self.player.gold, 110) # 10 start + 100 reward
        
        # Verify items were removed
        self.assertFalse(self.player.has_item("rat_tail"))

    def test_complete_quest_missing_items(self):
        self.player.active_quests.append("rat_problem")
        self.player.location_id = "town"
        
        # Give fewer items than required
        from models import Item
        self.player.add_item(Item(id="rat_tail", name="Rat Tail", description="Tail", type="junk", value=1, effect="none", amount=2))
        
        response = self.quest_system.complete_quest("rat_problem")
        
        self.assertIn("need 5x Rat Tail", response)
        self.assertIn("rat_problem", self.player.active_quests)

    def test_complete_quest_wrong_location(self):
        self.player.active_quests.append("rat_problem")
        self.player.location_id = "tavern" # Mayor is at "town"
        
        response = self.quest_system.complete_quest("rat_problem")
        
        self.assertIn("must return to Mayor", response)
        self.assertIn("rat_problem", self.player.active_quests)

    def test_complete_quest_not_active(self):
        response = self.quest_system.complete_quest("rat_problem")
        self.assertIn("don't have that active quest", response)

if __name__ == '__main__':
    unittest.main()
