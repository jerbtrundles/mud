# crafting.py
from items.item_factory import ItemFactory

class CraftingSystem:
    def __init__(self):
        # Recipe definitions: {result_item: {ingredient1: count1, ingredient2: count2, ...}}
        self.recipes = {
            "strong_healing_potion": {"healing_potion": 2, "gem": 1},
            "torch": {"stick": 1, "cloth": 1},
            "reinforced_leather_armor": {"leather_armor": 1, "gem": 2},
            "enchanted_sword": {"steel_sword": 1, "ruby": 1, "sapphire": 1}
        }
        
        # Define new crafted items
        self._initialize_crafted_items()
    
    def _initialize_crafted_items(self):
        """Add new craftable items to the appropriate item collections"""
        from items.weapon import WEAPONS, Weapon
        from items.armor import ARMORS, Armor
        from items.item import Item
        
        # First, create a dictionary of basic items for crafting
        # We'll store these in a new module-level variable in ItemFactory
        from items.treasure import TOOLS  # We'll add our items to TOOLS collection since they are tool-like
        
        # Add a stick item (needed for torch crafting)
        if "stick" not in TOOLS:
            TOOLS["stick"] = Item(
                "stick", 
                "A simple wooden stick.", 
                value=1, 
                stackable=True, 
                max_stack=10,
                aliases=["branch", "wood"]
            )
        
        # Add cloth item (needed for torch crafting)
        if "cloth" not in TOOLS:
            TOOLS["cloth"] = Item(
                "cloth", 
                "A piece of cloth.", 
                value=1, 
                stackable=True, 
                max_stack=10,
                aliases=["fabric", "rag"]
            )
        
        # Add reinforced leather armor
        if "reinforced_leather_armor" not in ARMORS:
            ARMORS["reinforced_leather_armor"] = Armor(
                "reinforced_leather_armor", 
                "Leather armor reinforced with gemstones, offering improved protection.",
                defense_bonus=5,
                value=25,
                aliases=["reinforced leather", "gem leather", "reinforced armor"]
            )
        
        # Add enchanted sword
        if "enchanted_sword" not in WEAPONS:
            WEAPONS["enchanted_sword"] = Weapon(
                "enchanted_sword", 
                "A sword infused with magical gems, glowing with arcane energy.",
                attack_bonus=18,
                value=75,
                requirements={"level": 3},
                aliases=["enchanted blade", "magic sword", "glowing sword"]
            )
    
    def get_available_recipes(self, player):
        """Get recipes that the player can currently craft with their inventory"""
        available_recipes = {}
        
        for result, ingredients in self.recipes.items():
            can_craft = True
            
            # Check if player has all required ingredients
            for ingredient, count in ingredients.items():
                if not player.has_item(ingredient, count):
                    can_craft = False
                    break
            
            if can_craft:
                available_recipes[result] = ingredients
        
        return available_recipes
    
    def craft_item(self, game_state, recipe_name):
        """Attempt to craft an item from a recipe"""
        player = game_state.player
        
        # Find best matching recipe name
        best_match = None
        for result in self.recipes.keys():
            if result.replace('_', ' ') == recipe_name.lower():
                best_match = result
                break
            elif recipe_name.lower() in result.replace('_', ' '):
                best_match = result
                break
        
        if not best_match:
            # Try checking crafted item display names
            for result in self.recipes.keys():
                item = ItemFactory.get_item(result)
                if item and recipe_name.lower() in item.display_name().lower():
                    best_match = result
                    break
        
        if not best_match:
            return False, f"You don't know how to craft '{recipe_name}'."
        
        recipe_result = best_match
        recipe = self.recipes[recipe_result]
        
        # Check if player has all ingredients
        for ingredient, count in recipe.items():
            if not player.has_item(ingredient, count):
                item_obj = ItemFactory.get_item(ingredient)
                item_name = item_obj.display_name() if item_obj else ingredient.replace('_', ' ')
                return False, f"You need {count}x {item_name} to craft this."
        
        # Remove ingredients from inventory
        for ingredient, count in recipe.items():
            player.remove_from_inventory(ingredient, count)
        
        # Add crafted item to inventory
        player.add_to_inventory(recipe_result)
        
        # Get display names for a better message
        result_item = ItemFactory.get_item(recipe_result)
        
        if result_item:
            return True, f"You successfully crafted {result_item.display_name()}!"
        else:
            return True, f"You successfully crafted {recipe_result.replace('_', ' ')}!"
    
    def display_recipes(self, game_state):
        """Display available crafting recipes to the player"""
        player = game_state.player
        available = self.get_available_recipes(player)
        
        if not available:
            game_state.add_to_history("You don't have the ingredients to craft anything right now.")
            return
        
        game_state.add_to_history("Available Crafting Recipes:", (255, 255, 100))  # TITLE_COLOR
        
        for result, ingredients in available.items():
            result_item = ItemFactory.get_item(result)
            if not result_item:
                continue
                
            # Format ingredient list
            ingredient_text = []
            for ing_name, ing_count in ingredients.items():
                ing_item = ItemFactory.get_item(ing_name)
                if ing_item:
                    ingredient_text.append(f"{ing_count}x {ing_item.display_name()}")
                else:
                    ingredient_text.append(f"{ing_count}x {ing_name.replace('_', ' ')}")
            
            # Show special properties of the crafted item
            properties = ""
            if result_item.type == "weapon":
                properties = f" (+{result_item.attack_bonus} ATK)"
            elif result_item.type == "armor":
                properties = f" (+{result_item.defense_bonus} DEF)"
            
            game_state.add_to_history(f"• {result_item.display_name()}{properties}: {', '.join(ingredient_text)}")
        
        game_state.add_to_history("\nUse 'craft [item name]' to create an item.")
    
    def debug_items(self, game_state):
        """Debug function to check if items are properly registered"""
        game_state.add_to_history("Checking crafting materials in ItemFactory:", (255, 255, 100))
        
        # Test if items can be retrieved
        stick = ItemFactory.get_item("stick")
        cloth = ItemFactory.get_item("cloth")
        
        if stick:
            game_state.add_to_history(f"✓ Stick found: {stick.display_name()}")
        else:
            game_state.add_to_history("✗ Stick NOT found in ItemFactory!")
            
        if cloth:
            game_state.add_to_history(f"✓ Cloth found: {cloth.display_name()}")
        else:
            game_state.add_to_history("✗ Cloth NOT found in ItemFactory!")
            
        # Check if these items can be found via partial matching too
        stick_match = ItemFactory.find_item_by_name("stick")
        cloth_match = ItemFactory.find_item_by_name("cloth")
        branch_match = ItemFactory.find_item_by_name("branch")  # alias for stick
        
        game_state.add_to_history(f"Finding by name - stick: {stick_match}, cloth: {cloth_match}, branch: {branch_match}")