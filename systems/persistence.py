import os
import bcrypt
from typing import Optional
from sqlalchemy import select
from database import AsyncSessionLocal, PlayerState, WorldState
from models import World, Player

class PersistenceSystem:
    """System for handling game saving and loading."""

    def __init__(self, world: World):
        self.world = world

    async def save_game(self, player: Player) -> str:
        """Saves the current game state to the database."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(PlayerState).filter_by(name=player.name))
            player_state = result.scalars().first()
            
            if not player_state:
                hashed_password = bcrypt.hashpw(player.password.encode('utf-8'), bcrypt.gensalt())
                player_state = PlayerState(name=player.name, password_hash=hashed_password)
                db.add(player_state)

            player_state.location_id = player.location_id
            player_state.health = player.health
            player_state.max_health = player.max_health
            player_state.stamina = player.stamina
            player_state.max_stamina = player.max_stamina
            player_state.gold = player.gold
            player_state.strength = player.strength
            player_state.dexterity = player.dexterity
            player_state.intelligence = player.intelligence
            player_state.attack = player.attack
            player_state.defense = player.defense
            player_state.mana = player.mana
            player_state.max_mana = player.max_mana
            player_state.experience = player.experience
            player_state.level = player.level
            player_state.skill_points = player.skill_points
            player_state.attribute_points = player.attribute_points
            player_state.inventory = player.inventory
            player_state.equipment = player.equipment
            player_state.skills = player.skills
            player_state.active_quests = player.active_quests
            player_state.completed_quests = player.completed_quests
            player_state.visited_locations = player.visited_locations
            
            for loc_id, location in self.world.locations.items():
                result = await db.execute(select(WorldState).filter_by(location_id=loc_id))
                world_state = result.scalars().first()
                
                if not world_state:
                    world_state = WorldState(location_id=loc_id)
                    db.add(world_state)
                world_state.looted_treasures = location.treasure
                world_state.ground_items = location.items

            await db.commit()
        return "Game saved."

    async def load_game(self, password: str) -> Optional[Player]:
        """Load a game state from the database."""
        if not os.path.exists("somerpg.db"):
            return None
            
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(PlayerState))
            player_states = result.scalars().all()
            
            for player_state in player_states:
                if bcrypt.checkpw(password.encode('utf-8'), player_state.password_hash):
                    player = Player(
                        name=player_state.name,
                        password=password,
                        location_id=player_state.location_id,
                        health=player_state.health,
                        max_health=player_state.max_health,
                        stamina=player_state.stamina,
                        max_stamina=player_state.max_stamina,
                        gold=player_state.gold,
                        strength=player_state.strength,
                        dexterity=player_state.dexterity,
                        intelligence=player_state.intelligence,
                        attack=player_state.attack,
                        defense=player_state.defense,
                        mana=player_state.mana,
                        max_mana=player_state.max_mana,
                        experience=player_state.experience,
                        level=player_state.level,
                        skill_points=player_state.skill_points,
                        attribute_points=player_state.attribute_points,
                        inventory=player_state.inventory,
                        equipment=player_state.equipment,
                        skills=player_state.skills,
                        active_quests=player_state.active_quests,
                        completed_quests=player_state.completed_quests,
                        visited_locations=player_state.visited_locations
                    )
            
                    result = await db.execute(select(WorldState))
                    world_states = result.scalars().all()
                    for ws in world_states:
                        location = self.world.get_location(ws.location_id)
                        if location:
                            location.treasure = ws.looted_treasures
                            location.items = ws.ground_items if ws.ground_items else []
                    
                    return player

        return None
