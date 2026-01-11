import unittest
from unittest.mock import MagicMock, patch
from systems.combat import CombatSystem
from models import World, Player, Enemy, Encounter, GameSettings

class TestCombatSystem(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.world.settings = GameSettings()
        self.player = Player(name="TestPlayer", password="pass")
        self.combat_system = CombatSystem(self.world, self.player)

    @patch('random.random')
    def test_resolve_player_attack(self, mock_random):
        # Mock random to avoid critical hit (crit chance is low, so 0.5 is safe)
        mock_random.return_value = 0.5
        
        enemy = Enemy(
            id="goblin", name="Goblin", description="A goblin",
            health=50, max_health=50, attack=5, defense=0,
            reward_gold=10, reward_exp=10
        )
        
        # Player base attack is 5 + 10 (strength) = 15
        result = self.combat_system.resolve_player_attack(enemy)
        
        self.assertEqual(result["damage"], 15)
        self.assertEqual(enemy.health, 35)
        self.assertFalse(result["is_crit"])

    def test_resolve_enemy_attack(self):
        enemy = Enemy(
            id="goblin", name="Goblin", description="A goblin",
            health=50, max_health=50, attack=20, defense=0,
            reward_gold=10, reward_exp=10
        )
        
        # Player base defense is 5 + 10 (dexterity) = 15
        # Damage taken = max(0, 20 - 15) = 5
        damage = self.combat_system.resolve_enemy_attack(enemy)
        
        self.assertEqual(damage, 20) # The method returns raw damage, but player takes mitigated damage
        self.assertEqual(self.player.health, 95) # 100 - 5

if __name__ == '__main__':
    unittest.main()
