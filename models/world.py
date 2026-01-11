from typing import Dict, Optional
from .location import Location
from .npc import NPC
from .item import Item
from .recipe import Recipe
from .skill import Skill
from .quest import Quest
from .encounter import Encounter
from .danger import Danger
from .features import Features
from .settings import GameSettings

class World:
    """Represents the game world."""

    def __init__(self):
        self.locations: Dict[str, Location] = {}
        self.npcs: Dict[str, NPC] = {}
        self.items: Dict[str, Item] = {}
        self.recipes: Dict[str, Recipe] = {}
        self.skills: Dict[str, Skill] = {}
        self.quests: Dict[str, Quest] = {}
        self.encounters: Dict[str, Encounter] = {}
        self.dangers: Dict[str, Danger] = {}
        self.name: str = ""
        self.start_location: str = ""
        self.start_inventory: Dict[str, int] = {}
        self.features: Features = Features()
        self.settings: GameSettings = GameSettings()
        self.time_tick: int = 0

    @property
    def is_day(self) -> bool:
        """Returns True if it is day, False if night.
        Day is 0-11 ticks, Night is 12-23 ticks (assuming 24 tick cycle).
        """
        return (self.time_tick % 24) < 12

    @property
    def time_display(self) -> str:
        """Returns a string representation of the time."""
        hour = self.time_tick % 24
        if hour < 12:
            return "Day"
        else:
            return "Night"

    def get_location(self, location_id: str) -> Optional[Location]:
        """Get a location by id."""
        return self.locations.get(location_id)

    def get_location_by_coords(self, x: int, y: int) -> Optional[Location]:
        """Get a location by coordinates."""
        for location in self.locations.values():
            if location.x == x and location.y == y:
                return location
        return None

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Get an NPC by id."""
        return self.npcs.get(npc_id)

    def get_item(self, item_id: str) -> Optional[Item]:
        """Get an item by id."""
        return self.items.get(item_id)

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by id."""
        return self.recipes.get(recipe_id)

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get a skill by id."""
        return self.skills.get(skill_id)

    def get_quest(self, quest_id: str) -> Optional[Quest]:
        """Get a quest by id."""
        return self.quests.get(quest_id)

    def get_encounter(self, encounter_id: str) -> Optional[Encounter]:
        """Get an encounter by id."""
        return self.encounters.get(encounter_id)

    def get_danger(self, danger_id: str) -> Optional[Danger]:
        """Get a danger by id."""
        return self.dangers.get(danger_id)
