from typing import Tuple, List
from models import World, Player, Item

class CraftingSystem:
    """System for crafting items."""

    def __init__(self, world: World, player: Player):
        self.world = world
        self.player = player

    def get_available_recipes(self) -> str:
        """Get a list of recipes the player can see."""
        # For now, all recipes are visible. Later could be unlocked.
        if not self.world.recipes:
            return "No recipes available."
            
        msg = "Crafting Recipes:\n"
        for recipe in self.world.recipes.values():
            ingredients_str = ", ".join([f"{qty}x {self.world.get_item(iid).name}" for iid, qty in recipe.ingredients.items()])
            result_item = self.world.get_item(recipe.result)
            msg += f"  - {recipe.name}: {ingredients_str} -> {recipe.result_amount}x {result_item.name}\n"
        return msg

    def craft_item(self, recipe_name: str) -> Tuple[bool, str]:
        """Craft an item using a recipe."""
        recipe = None
        for r in self.world.recipes.values():
            if r.name.lower() == recipe_name.lower():
                recipe = r
                break
        
        if not recipe:
            return False, "Recipe not found."

        # Check ingredients
        for item_id, qty in recipe.ingredients.items():
            player_has = 0
            for item in self.player.inventory:
                if item.id == item_id:
                    player_has = item.amount
                    break
            
            if player_has < qty:
                item_name = self.world.get_item(item_id).name
                return False, f"Not enough ingredients. Need {qty}x {item_name}."

        # Consume ingredients
        for item_id, qty in recipe.ingredients.items():
            for _ in range(qty):
                self.player.remove_item(item_id)

        # Add result
        result_item = self.world.get_item(recipe.result)
        if result_item:
            # Create new item instance
            crafted_item = Item(
                id=result_item.id,
                name=result_item.name,
                description=result_item.description,
                type=result_item.type,
                value=result_item.value,
                effect=result_item.effect,
                amount=recipe.result_amount,
                slot=result_item.slot,
                stats=result_item.stats.copy() if result_item.stats else {},
                element=result_item.element
            )
            self.player.add_item(crafted_item)
            return True, f"You crafted {recipe.result_amount}x {result_item.name}!"
        
        return False, "Error creating item."
