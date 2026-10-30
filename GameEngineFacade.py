import logging
from engine import GameEngine

class GameEngineFacade:
    def __init__(self, *args, **kwargs):
        self._legacy = GameEngine(*args, **kwargs)
        self.logger = logging.getLogger('GameEngineFacade')

    def move_to_location(self, *args, **kwargs):
        self.logger.info(f'Calling move_to_location with args: {args} {kwargs}')
        result = self._legacy.move_to_location(*args, **kwargs)
        self.logger.info(f'move_to_location returned: {result}')
        return result

    def get_location_description(self, *args, **kwargs):
        self.logger.info(f'Calling get_location_description with args: {args} {kwargs}')
        result = self._legacy.get_location_description(*args, **kwargs)
        self.logger.info(f'get_location_description returned: {result}')
        return result

    def get_player_status(self, *args, **kwargs):
        self.logger.info(f'Calling get_player_status with args: {args} {kwargs}')
        result = self._legacy.get_player_status(*args, **kwargs)
        self.logger.info(f'get_player_status returned: {result}')
        return result

    def rest(self, *args, **kwargs):
        self.logger.info(f'Calling rest with args: {args} {kwargs}')
        result = self._legacy.rest(*args, **kwargs)
        self.logger.info(f'rest returned: {result}')
        return result

    def use_item(self, *args, **kwargs):
        self.logger.info(f'Calling use_item with args: {args} {kwargs}')
        result = self._legacy.use_item(*args, **kwargs)
        self.logger.info(f'use_item returned: {result}')
        return result

    def investigate_location(self, *args, **kwargs):
        self.logger.info(f'Calling investigate_location with args: {args} {kwargs}')
        result = self._legacy.investigate_location(*args, **kwargs)
        self.logger.info(f'investigate_location returned: {result}')
        return result

    def encounter_enemy(self, *args, **kwargs):
        self.logger.info(f'Calling encounter_enemy with args: {args} {kwargs}')
        result = self._legacy.encounter_enemy(*args, **kwargs)
        self.logger.info(f'encounter_enemy returned: {result}')
        return result

    def resolve_player_attack(self, *args, **kwargs):
        self.logger.info(f'Calling resolve_player_attack with args: {args} {kwargs}')
        result = self._legacy.resolve_player_attack(*args, **kwargs)
        self.logger.info(f'resolve_player_attack returned: {result}')
        return result

    def get_loot(self, *args, **kwargs):
        self.logger.info(f'Calling get_loot with args: {args} {kwargs}')
        result = self._legacy.get_loot(*args, **kwargs)
        self.logger.info(f'get_loot returned: {result}')
        return result

    def trigger_encounter(self, *args, **kwargs):
        self.logger.info(f'Calling trigger_encounter with args: {args} {kwargs}')
        result = self._legacy.trigger_encounter(*args, **kwargs)
        self.logger.info(f'trigger_encounter returned: {result}')
        return result

    def trigger_danger(self, *args, **kwargs):
        self.logger.info(f'Calling trigger_danger with args: {args} {kwargs}')
        result = self._legacy.trigger_danger(*args, **kwargs)
        self.logger.info(f'trigger_danger returned: {result}')
        return result

    def trigger_hidden_dangers(self, *args, **kwargs):
        self.logger.info(f'Calling trigger_hidden_dangers with args: {args} {kwargs}')
        result = self._legacy.trigger_hidden_dangers(*args, **kwargs)
        self.logger.info(f'trigger_hidden_dangers returned: {result}')
        return result

    def disarm_trap(self, *args, **kwargs):
        self.logger.info(f'Calling disarm_trap with args: {args} {kwargs}')
        result = self._legacy.disarm_trap(*args, **kwargs)
        self.logger.info(f'disarm_trap returned: {result}')
        return result

    def talk_to_npc(self, *args, **kwargs):
        self.logger.info(f'Calling talk_to_npc with args: {args} {kwargs}')
        result = self._legacy.talk_to_npc(*args, **kwargs)
        self.logger.info(f'talk_to_npc returned: {result}')
        return result

    def buy_from_npc(self, *args, **kwargs):
        self.logger.info(f'Calling buy_from_npc with args: {args} {kwargs}')
        result = self._legacy.buy_from_npc(*args, **kwargs)
        self.logger.info(f'buy_from_npc returned: {result}')
        return result

    def buy_item_from_npc_by_name(self, *args, **kwargs):
        self.logger.info(f'Calling buy_item_from_npc_by_name with args: {args} {kwargs}')
        result = self._legacy.buy_item_from_npc_by_name(*args, **kwargs)
        self.logger.info(f'buy_item_from_npc_by_name returned: {result}')
        return result

    def get_inventory(self, *args, **kwargs):
        self.logger.info(f'Calling get_inventory with args: {args} {kwargs}')
        result = self._legacy.get_inventory(*args, **kwargs)
        self.logger.info(f'get_inventory returned: {result}')
        return result

    def accept_quest_from_npc(self, *args, **kwargs):
        self.logger.info(f'Calling accept_quest_from_npc with args: {args} {kwargs}')
        result = self._legacy.accept_quest_from_npc(*args, **kwargs)
        self.logger.info(f'accept_quest_from_npc returned: {result}')
        return result

    def get_active_quests_display(self, *args, **kwargs):
        self.logger.info(f'Calling get_active_quests_display with args: {args} {kwargs}')
        result = self._legacy.get_active_quests_display(*args, **kwargs)
        self.logger.info(f'get_active_quests_display returned: {result}')
        return result

    def get_map_display(self, *args, **kwargs):
        self.logger.info(f'Calling get_map_display with args: {args} {kwargs}')
        result = self._legacy.get_map_display(*args, **kwargs)
        self.logger.info(f'get_map_display returned: {result}')
        return result

    def accept_quest(self, *args, **kwargs):
        self.logger.info(f'Calling accept_quest with args: {args} {kwargs}')
        result = self._legacy.accept_quest(*args, **kwargs)
        self.logger.info(f'accept_quest returned: {result}')
        return result

    def complete_quest(self, *args, **kwargs):
        self.logger.info(f'Calling complete_quest with args: {args} {kwargs}')
        result = self._legacy.complete_quest(*args, **kwargs)
        self.logger.info(f'complete_quest returned: {result}')
        return result

    def equip_item(self, *args, **kwargs):
        self.logger.info(f'Calling equip_item with args: {args} {kwargs}')
        result = self._legacy.equip_item(*args, **kwargs)
        self.logger.info(f'equip_item returned: {result}')
        return result

    def unequip_item(self, *args, **kwargs):
        self.logger.info(f'Calling unequip_item with args: {args} {kwargs}')
        result = self._legacy.unequip_item(*args, **kwargs)
        self.logger.info(f'unequip_item returned: {result}')
        return result

    def get_skills_display(self, *args, **kwargs):
        self.logger.info(f'Calling get_skills_display with args: {args} {kwargs}')
        result = self._legacy.get_skills_display(*args, **kwargs)
        self.logger.info(f'get_skills_display returned: {result}')
        return result

    def craft_item(self, *args, **kwargs):
        self.logger.info(f'Calling craft_item with args: {args} {kwargs}')
        result = self._legacy.craft_item(*args, **kwargs)
        self.logger.info(f'craft_item returned: {result}')
        return result

    def get_recipes_display(self, *args, **kwargs):
        self.logger.info(f'Calling get_recipes_display with args: {args} {kwargs}')
        result = self._legacy.get_recipes_display(*args, **kwargs)
        self.logger.info(f'get_recipes_display returned: {result}')
        return result

    def drop_item(self, *args, **kwargs):
        self.logger.info(f'Calling drop_item with args: {args} {kwargs}')
        result = self._legacy.drop_item(*args, **kwargs)
        self.logger.info(f'drop_item returned: {result}')
        return result

    def pickup_item(self, *args, **kwargs):
        self.logger.info(f'Calling pickup_item with args: {args} {kwargs}')
        result = self._legacy.pickup_item(*args, **kwargs)
        self.logger.info(f'pickup_item returned: {result}')
        return result

    def add_experience(self, *args, **kwargs):
        self.logger.info(f'Calling add_experience with args: {args} {kwargs}')
        result = self._legacy.add_experience(*args, **kwargs)
        self.logger.info(f'add_experience returned: {result}')
        return result

    def save_game(self, *args, **kwargs):
        self.logger.info(f'Calling save_game with args: {args} {kwargs}')
        result = self._legacy.save_game(*args, **kwargs)
        self.logger.info(f'save_game returned: {result}')
        return result
