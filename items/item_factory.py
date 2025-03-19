# item_factory.py
from items.weapon import WEAPONS, get_weapon
from items.armor import ARMORS, get_armor
from items.herbs import HERBS, get_herb
from items.consumable import CONSUMABLES, get_consumable
from items.treasure import (
    GEMS, get_gem,
    QUEST_ITEMS, get_quest_item,
    KEYS, get_key,
    TOOLS, get_tool
)
from items.treasure_box import TREASURE_BOXES, get_treasure_box
from items.box_keys import BOX_KEYS, get_box_key

class ItemFactory:
    """
    Factory class to centralize item creation and management
    """
    
    @staticmethod
    def get_item(item_name):
        """
        Get an item instance by name
        
        Args:
            item_name (str): The internal name of the item
            
        Returns:
            Item: The item instance, or None if not found
        """
        if item_name in WEAPONS:
            return get_weapon(item_name)
        elif item_name in ARMORS:
            return get_armor(item_name)
        elif item_name in CONSUMABLES:
            return get_consumable(item_name)
        elif item_name in GEMS:
            return get_gem(item_name)
        elif item_name in QUEST_ITEMS:
            return get_quest_item(item_name)
        elif item_name in KEYS:
            return get_key(item_name)
        elif item_name in TOOLS:
            return get_tool(item_name)
        elif item_name in TREASURE_BOXES:
            return get_treasure_box(item_name)
        elif item_name in BOX_KEYS:
            return get_box_key(item_name)
        elif item_name in HERBS:  # Add this line
            return get_herb(item_name)  # And this line
        elif item_name == "coin":
            # Special case for coins
            from items.item import Item
            return Item("coin", "A gold coin.", value=1, stackable=True, max_stack=999)
        return None
    
    @staticmethod
    def get_all_items():
        """
        Get all available items as a dictionary
        
        Returns:
            dict: A dictionary of all items where keys are item names
        """
        all_items = {}
        
        # Add weapons
        from items.weapon import WEAPONS
        all_items.update(WEAPONS)
        
        # Add armors
        from items.armor import ARMORS
        all_items.update(ARMORS)
        
        # Add consumables
        from items.consumable import CONSUMABLES
        all_items.update(CONSUMABLES)
        
        # Add treasures
        from items.treasure import GEMS, QUEST_ITEMS, KEYS, TOOLS
        all_items.update(GEMS)
        all_items.update(QUEST_ITEMS)
        all_items.update(KEYS)
        all_items.update(TOOLS)
        
        from items.treasure_box import TREASURE_BOXES
        all_items.update(TREASURE_BOXES)
        
        from items.box_keys import BOX_KEYS
        all_items.update(BOX_KEYS)

        # Add coin as a special case
        from items.item import Item
        all_items["coin"] = Item("coin", "A gold coin.", value=1, stackable=True, max_stack=999)
        
        return all_items

    @staticmethod
    def find_item_by_name(search_string, include_partial=True):
        """
        Find an item by name or alias with partial string matching
        
        Args:
            search_string (str): The name to search for
            include_partial (bool): Whether to include partial matches
            
        Returns:
            str: The internal item name, or None if not found
        """
        search_string = search_string.lower().replace(' ', '_')
        
        # First check for direct match
        all_items = ItemFactory.get_all_items()
        if search_string in all_items:
            return search_string
            
        # Then check for exact alias match
        for item_name, item in all_items.items():
            item_obj = ItemFactory.get_item(item_name)
            if item_obj and search_string in [alias.lower().replace(' ', '_') for alias in item_obj.aliases]:
                return item_name
                
        # Finally, check for partial match if enabled
        if include_partial:
            # First check partial matches on item names
            matches = []
            for item_name in all_items.keys():
                if search_string in item_name:
                    matches.append((item_name, len(item_name) - len(search_string)))  # Score by how close the match is
            
            # Then check partial matches on aliases
            for item_name in all_items.keys():
                item_obj = ItemFactory.get_item(item_name)
                if not item_obj:
                    continue
                    
                for alias in item_obj.aliases:
                    alias = alias.lower().replace(' ', '_')
                    if search_string in alias:
                        matches.append((item_name, len(alias) - len(search_string)))
            
            # Return the best match (smallest length difference)
            if matches:
                matches.sort(key=lambda x: x[1])
                return matches[0][0]
                
        return None