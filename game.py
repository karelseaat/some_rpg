"""
Represents the game state for a single player session.
"""
from models import Player, World
from engine import GameEngine

class Game:
    """
    Manages the game state for a single player, including the player object
    and the game engine.
    """
    def __init__(self, world: World, player_name: str):
        self.world = world
        self.player = Player(
            name=player_name,
            location_id=world.start_location
        )
        self.player.visited_locations.add(world.start_location)
        self.engine = GameEngine(self.world, self.player)
