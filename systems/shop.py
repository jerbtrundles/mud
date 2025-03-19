# shop.py
import random
from items.item_factory import ItemFactory

# Colors for text
TEXT_COLOR = (200, 200, 200)
TITLE_COLOR = (255, 255, 100)
COMBAT_COLOR = (255, 165, 0)
HEALTH_COLOR = (100, 255, 100)

class ShopSystem:
    def __init__(self):
        # Shop dialogues
        self.shop_dialogues = [
            "The dwarf nods at you. 'See anything you like?'",
            "'Best prices in the dungeon, that's my guarantee!'",
            "'Need something to fight off those monsters? I've got just the thing.'",
            "'That armor you're looking at? Made it myself. Quality craftsmanship!'",
            "'I also buy adventurer's gear, if you've got extras to sell.'",
            "'Be careful in those caves. Not everyone comes back, y'know.'"
        ]
    
    def get_random_dialogue(self):
        """Return a random shop dialogue."""
        return random.choice(self.shop_dialogues)
    
    def process_buy(self, game_state, item_name):
        """Process a buy request with partial string matching."""
        # Convert to lowercase for case-insensitive matching
        item_text = item_name.lower()
        
        room = game_state.world.get_room(game_state.current_room)
        if not room or not room.get("is_shop", False):
            game_state.add_to_history("There's no shop here to buy from.")
            return
        
        # Check if item is in shop inventory using partial matching
        shop_inventory = room.get("shop_inventory", {})
        
        # Try to find the best matching item in the shop
        best_match = None
        best_score = float('inf')  # Lower is better
        
        for shop_item in shop_inventory:
            # Get the item object if possible
            item_obj = ItemFactory.get_item(shop_item)
            
            # Check exact match on name
            if shop_item.replace('_', ' ') == item_text:
                best_match = shop_item
                break
                
            # Check partial match on name
            if item_text in shop_item.replace('_', ' '):
                score = len(shop_item) - len(item_text)
                if score < best_score:
                    best_match = shop_item
                    best_score = score
                    
            # If we have an item object, check aliases
            if item_obj:
                # Check exact matches on aliases
                if any(alias.lower() == item_text for alias in item_obj.aliases):
                    best_match = shop_item
                    break
                    
                # Check partial matches on aliases
                for alias in item_obj.aliases:
                    if item_text in alias.lower():
                        score = len(alias) - len(item_text)
                        if score < best_score:
                            best_match = shop_item
                            best_score = score
        
        # If no match found
        if not best_match:
            game_state.add_to_history(f"The shop doesn't sell any '{item_text}'.")
            return
            
        # Get the item details
        item_price = shop_inventory[best_match]["price"]
        
        # Check if player has enough coins
        if game_state.coins < item_price:
            game_state.add_to_history(f"You don't have enough coins. {best_match.replace('_', ' ')} costs {item_price} coins, but you only have {game_state.coins}.")
            return
        
        # Purchase the item
        game_state.coins -= item_price
        game_state.player.add_to_inventory(best_match)
        
        # Get the item object for better display
        item_obj = ItemFactory.get_item(best_match)
        if item_obj:
            game_state.add_to_history(f"You purchased {item_obj.display_name()} for {item_price} coins. You have {game_state.coins} coins left.")
        else:
            game_state.add_to_history(f"You purchased {best_match.replace('_', ' ')} for {item_price} coins. You have {game_state.coins} coins left.")
        
        # If it's a healing potion, let them know they can use it
        if best_match == "healing_potion":
            game_state.add_to_history("Use 'use healing potion' when you need to heal.")

    def process_sell(self, game_state, item_name):
        """Process a sell request with partial string matching."""
        # Convert to lowercase for case-insensitive matching
        item_text = item_name.lower()
        
        room = game_state.world.get_room(game_state.current_room)
        if not room or not room.get("is_shop", False):
            game_state.add_to_history("There's no shop here to sell to.")
            return
        
        # Search through player's inventory for closest match
        best_match = None
        best_score = float('inf')  # Lower is better
        
        for inv_item in game_state.player.inventory:
            item = ItemFactory.get_item(inv_item)
            if not item:
                continue
                
            # Check exact name match
            if item.name.replace('_', ' ') == item_text:
                best_match = item.name
                break
                
            # Check alias matches
            if any(alias.lower() == item_text for alias in item.aliases):
                best_match = item.name
                break
                
            # Check partial name match
            if item_text in item.name.replace('_', ' '):
                score = len(item.name) - len(item_text)
                if score < best_score:
                    best_match = item.name
                    best_score = score
                    
            # Check partial alias matches
            for alias in item.aliases:
                if item_text in alias.lower():
                    score = len(alias) - len(item_text)
                    if score < best_score:
                        best_match = item.name
                        best_score = score
        
        actual_item_name = best_match
        
        # Check if player has the item
        if not actual_item_name or not game_state.player.has_item(actual_item_name):
            game_state.add_to_history(f"You don't have a {item_text} to sell.")
            return
        
        # Get the item object
        item = ItemFactory.get_item(actual_item_name)
        if not item:
            game_state.add_to_history(f"You can't sell the {item_text}.")
            return
        
        # Check if the item can be sold
        if not item.can_sell():
            game_state.add_to_history(f"The shopkeeper examines your {item.display_name()}.")
            game_state.add_to_history("'I can't buy that from you. Feel free to use it yourself.'")
            return
        
        # Get the sell price
        sell_price = item.get_sell_price()
            
        # Remove from inventory and add coins
        game_state.player.remove_from_inventory(actual_item_name)
        game_state.coins += sell_price
        
        game_state.add_to_history(f"You sold {item.display_name()} for {sell_price} coins. You now have {game_state.coins} coins.")
    
    def display_shop(self, game_state):
        """Display basic shop info without listing items."""
        room = game_state.world.get_room(game_state.current_room)
        
        # Add a shopkeeper dialogue
        if self.shop_dialogues:
            game_state.add_to_history(self.get_random_dialogue())
        
        game_state.add_to_history("You're in a shop. The shopkeeper watches you expectantly.", TITLE_COLOR)
        game_state.add_to_history(f"You have {game_state.coins} coins.")
        game_state.add_to_history("Type 'list' to see available items, 'buy [item]' to purchase, or 'sell [item]' to sell.")

    def display_shop_inventory(self, game_state):
        """Display the shop inventory as a separate command."""
        room = game_state.world.get_room(game_state.current_room)
        
        if not room or not room.get("is_shop", False):
            game_state.add_to_history("There's no shop here.")
            return
        
        game_state.add_to_history("Shop Inventory:", TITLE_COLOR)
        shop_inventory = room.get("shop_inventory", {})
        
        # Sort items by type and price for a more organized display
        weapons = []
        armors = []
        consumables = []
        other_items = []
        
        for item_name, details in shop_inventory.items():
            item_obj = ItemFactory.get_item(item_name)
            price = details["price"]
            
            if not item_obj:
                other_items.append((item_name.replace('_', ' '), price))
                continue
                
            if item_obj.type == "weapon":
                weapons.append((item_obj.display_name(), price, f"+{item_obj.attack_bonus} ATK"))
            elif item_obj.type == "armor":
                armors.append((item_obj.display_name(), price, f"+{item_obj.defense_bonus} DEF"))
            elif item_obj.type == "consumable" or item_obj.type in ["food", "drink"]:
                effect = ""
                if hasattr(item_obj, "health_restore") and item_obj.health_restore > 0:
                    effect = f"+{item_obj.health_restore} HP"
                consumables.append((item_obj.display_name(), price, effect))
            else:
                other_items.append((item_obj.display_name(), price))
        
        # Display weapons
        if weapons:
            game_state.add_to_history("Weapons:", COMBAT_COLOR)
            for name, price, bonus in weapons:
                game_state.add_to_history(f"  {name} ({bonus}) - {price} coins")
        
        # Display armors
        if armors:
            game_state.add_to_history("Armor:", COMBAT_COLOR)
            for name, price, bonus in armors:
                game_state.add_to_history(f"  {name} ({bonus}) - {price} coins")
        
        # Display consumables
        if consumables:
            game_state.add_to_history("Consumables:", HEALTH_COLOR)
            for name, price, effect in consumables:
                if effect:
                    game_state.add_to_history(f"  {name} ({effect}) - {price} coins")
                else:
                    game_state.add_to_history(f"  {name} - {price} coins")
        
        # Display other items
        if other_items:
            game_state.add_to_history("Other Items:", TEXT_COLOR)
            for name, price in other_items:
                game_state.add_to_history(f"  {name} - {price} coins")
        
        game_state.add_to_history(f"Your coins: {game_state.coins}")