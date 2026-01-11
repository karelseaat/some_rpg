from typing import Optional
from models import World, Player, NPC, Quest
from color import color_text, Colors
from events import event_bus, Event

class QuestSystem:
    """System for handling NPCs and quests."""

    def __init__(self, world: World, player: Player):
        self.world = world
        self.player = player
        event_bus.subscribe("enemy_killed", self.on_enemy_killed)

    def on_enemy_killed(self, event: Event):
        """Handle enemy killed event."""
        if event.data["player"] != self.player:
            return
            
        enemy_id = event.data["enemy_id"]
        # Update kill counts
        if enemy_id not in self.player.kill_counts:
            self.player.kill_counts[enemy_id] = 0
        self.player.kill_counts[enemy_id] += 1

    def _find_npc_by_name(self, npc_id: str) -> Optional[NPC]:
        """Find an NPC by ID or name."""
        npc = self.world.get_npc(npc_id)
        if not npc:
            npc_id_lower = npc_id.lower()
            for npc_obj in self.world.npcs.values():
                if npc_obj.name.lower() == npc_id_lower:
                    npc = npc_obj
                    break
        return npc

    def talk_to_npc(self, game, npc_id: str) -> str:
        """Talk to an NPC by ID or name."""
        npc = self._find_npc_by_name(npc_id)

        if not npc:
            return "NPC not found"
        
        response = f"\n{color_text(npc.name, Colors.BRIGHT_MAGENTA, game=game)}\n"
        response += f"{npc.description}\n\n"
        response += f'"{npc.dialogue}"\n'
        
        if self.world.features.traders_enabled and npc.shop:
            item_names = [self.world.get_item(item_id).name for item_id in npc.inventory if self.world.get_item(item_id)]
            if item_names:
                response += "\nThey sell: " + ", ".join(item_names) + "\n"
        
        if npc.offers_quest:
            quest = self.world.get_quest(npc.offers_quest)
            if quest:
                response += f"\n[They have a quest for you: '{quest.name}']\n"
                response += f"(To accept, type: accept_quest {npc.name})\n"
        
        return response

    def accept_quest_from_npc(self, npc_identifier: str) -> str:
        """Accept a quest from an NPC by ID or name."""
        npc = self._find_npc_by_name(npc_identifier)

        if not npc:
            return "NPC not found."

        if not npc.offers_quest:
            return f"{npc.name} has no quest to offer."

        # Find the quest associated with this NPC
        quest_to_accept = None
        for quest in self.world.quests.values():
            if quest.giver == npc.id:
                quest_to_accept = quest
                break
        
        if not quest_to_accept:
            return f"Could not find a quest from {npc.name}."
            
        return self.accept_quest(quest_to_accept.id)

    def accept_quest(self, quest_id: str) -> str:
        """Accept a quest."""
        quest = self.world.get_quest(quest_id)
        if not quest:
            return "Quest not found"
        
        if quest_id in self.player.active_quests:
            return "You already have this quest"
        
        if quest_id in self.player.completed_quests:
            return "You've already completed this quest"
        
        self.player.active_quests.append(quest_id)
        return f"Quest accepted: {quest.name}\n{quest.description}"

    def complete_quest(self, quest_identifier: str) -> str:
        """Attempt to complete a quest."""
        # Find quest by ID or name in active quests
        quest_id_to_complete = None
        for q_id in self.player.active_quests:
            if q_id == quest_identifier:
                quest_id_to_complete = q_id
                break
            quest = self.world.get_quest(q_id)
            if quest and quest.name.lower() == quest_identifier.lower():
                quest_id_to_complete = q_id
                break
        
        if not quest_id_to_complete:
            return "You don't have that active quest."

        quest = self.world.get_quest(quest_id_to_complete)
        if not quest:
            return "Quest data not found."

        # Check if player is at the quest giver's location
        giver = self.world.get_npc(quest.giver)
        if not giver:
            return "Quest giver not found."

        if self.player.location_id != giver.location_id:
            return f"You must return to {giver.name} to complete this quest."

        # Check completion requirements
        if quest.required_item:
            item_count = 0
            for item in self.player.inventory:
                if item.id == quest.required_item:
                    item_count += item.amount
            
            if item_count < quest.required_item_amount:
                item_name = self.world.get_item(quest.required_item).name
                return f"You need {quest.required_item_amount}x {item_name} to complete this quest."
            
            # Remove required items
            remaining_to_remove = quest.required_item_amount
            # Iterate backwards to safely remove items
            for i in range(len(self.player.inventory) - 1, -1, -1):
                item = self.player.inventory[i]
                if item.id == quest.required_item:
                    if item.amount <= remaining_to_remove:
                        remaining_to_remove -= item.amount
                        self.player.inventory.pop(i)
                    else:
                        item.amount -= remaining_to_remove
                        remaining_to_remove = 0
                    
                    if remaining_to_remove <= 0:
                        break

        if quest.required_kill:
            kill_count = self.player.kill_counts.get(quest.required_kill, 0)
            if kill_count < quest.required_kill_amount:
                # Try to get enemy name
                enemy_name = quest.required_kill
                # We don't have a direct way to get enemy name from ID unless we look at encounters
                # But for now let's just use the ID or try to find it
                return f"You need to defeat {quest.required_kill_amount}x {enemy_name} to complete this quest. (Current: {kill_count})"

        # Complete the quest
        self.player.active_quests.remove(quest_id_to_complete)
        self.player.completed_quests.append(quest_id_to_complete)
        
        event_bus.publish(Event("quest_completed", {
            "player": self.player,
            "quest_id": quest_id_to_complete,
            "quest_name": quest.name,
            "xp_reward": quest.xp_reward
        }))
        
        # Give rewards
        reward_msg = f"Quest Completed: {quest.name}!\n"
        
        if quest.reward > 0:
            self.player.add_gold(quest.reward)
            reward_msg += f"You gained {quest.reward} gold.\n"
            
        # XP Reward
        if quest.xp_reward > 0:
            # We don't call gain_experience here anymore, the ProgressionSystem listens to the event
            reward_msg += f"You gained {quest.xp_reward} experience.\n"

        if quest.reward_item:
            item = self.world.get_item(quest.reward_item)
            if item:
                self.player.add_item(item)
                reward_msg += f"You received: {item.name}\n"

        return reward_msg

    def get_active_quests_display(self) -> str:
        """Get a formatted string of active quests."""
        if not self.player.active_quests:
            return "You have no active quests"
        
        quests_text = "Active Quests:\n"
        for quest_id in self.player.active_quests:
            quest = self.world.get_quest(quest_id)
            if quest:
                quests_text += f"\n{quest.name}\n{quest.description}\n"
        return quests_text
