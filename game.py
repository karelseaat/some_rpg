"""
Represents the game state for a single player session.
"""
from typing import Optional
from models import Player, World, Enemy
from GameEngineFacade import GameEngineFacade as GameEngine

class Game:
    """
    Manages the game state for a single player, including the player object
    and the game engine.
    """
    def __init__(self, world: World, player_name: str, password: str):
        self.world = world
        self.in_combat = False
        self.current_enemy: Optional[Enemy] = None
        
        self.player = Player(
            name=player_name,
            password=password,
            location_id=world.start_location,
            gold=100, # Starting gold
        )
        self.player.visited_locations.add(world.start_location)
        self.engine = GameEngine(self.world, self.player)

        # Add starting items from world config
        for item_id, quantity in self.world.start_inventory.items():
            item = self.world.get_item(item_id)
            if item:
                for _ in range(quantity):
                    self.player.add_item(item)

