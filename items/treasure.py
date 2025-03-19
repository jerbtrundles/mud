# treasure.py
from items.item import Item

class Gem(Item):
    def __init__(self, name, description, value=10, rarity="common", aliases=None):
        """
        Gem class for valuable collectibles
        
        Args:
            name (str): Internal name of the gem
            description (str): Human-readable description
            value (int): Base value in coins
            rarity (str): Rarity level affecting value
            aliases (list): Alternative names for the item
        """
        super().__init__(name, description, value, stackable=True, max_stack=10, aliases=aliases)
        self.rarity = rarity
        self.type = "gem"
    
    def get_sell_price(self):
        """Get the sell price based on rarity"""
        rarity_multiplier = {
            "common": 1,
            "uncommon": 1.5,
            "rare": 2.5,
            "epic": 4,
            "legendary": 10
        }
        return max(1, int(self.value * rarity_multiplier.get(self.rarity, 1)))
    
    def __str__(self):
        return f"{self.display_name()} ({self.rarity.capitalize()} gem)"


class QuestItem(Item):
    def __init__(self, name, description, quest=None, value=0, aliases=None):
        """
        Quest item for storyline progress
        
        Args:
            name (str): Internal name of the item
            description (str): Human-readable description
            quest (str): Associated quest name
            value (int): Base value in coins (usually zero for quest items)
            aliases (list): Alternative names for the item
        """
        super().__init__(name, description, value, aliases=aliases)
        self.quest = quest
        self.type = "quest_item"
    
    def can_sell(self):
        """Quest items usually cannot be sold"""
        return False

class Key(Item):
    def __init__(self, name, description, unlocks=None, value=5, single_use=True, aliases=None):
        """
        Key item for unlocking doors or containers
        
        Args:
            name (str): Internal name of the key
            description (str): Human-readable description
            unlocks (list): List of room/container names this key unlocks
            value (int): Base value in coins
            single_use (bool): Whether the key is consumed upon use
            aliases (list): Alternative names for the item
        """
        super().__init__(name, description, value, usable=True, aliases=aliases)
        self.unlocks = unlocks or []
        self.single_use = single_use
        self.type = "key"
    
    def can_use(self, game_state):
        """
        Check if the key can be used in the current context
        - Checks for locked doors
        - Checks for treasure boxes in the room
        - Checks for treasure boxes in player's inventory
        """
        current_room = game_state.current_room
        
        # Check if current room has any locked exits this key unlocks
        room = game_state.world.get_room(current_room)
        if not room:
            return False
            
        # Check for doors this key can unlock
        for direction, destination in room.get("exits", {}).items():
            dest_room = game_state.world.get_room(destination)
            if dest_room and dest_room.get("locked", False) and destination in self.unlocks:
                return True
        
        # Check for treasure boxes in the room that this key can unlock
        if "items" in room:
            for item_name in room["items"]:
                # Check if this is a treasure box
                from items.item_factory import ItemFactory
                item = ItemFactory.get_item(item_name)
                if item and getattr(item, "type", "item") == "treasure_box" and (
                    item_name in self.unlocks or  # Specific unlock
                    getattr(item, "required_key", None) == self.name  # Required key match
                ):
                    return True
        
        # Also check player's inventory for treasure boxes
        for item_name in game_state.player.inventory:
            from items.item_factory import ItemFactory
            item = ItemFactory.get_item(item_name)
            if item and getattr(item, "type", "item") == "treasure_box" and (
                item_name in self.unlocks or  # Specific unlock
                getattr(item, "required_key", None) == self.name  # Required key match
            ):
                return True
                    
        return False

    def use(self, game_state):
        """
        Use the key to unlock something (door, treasure box in room, or treasure box in inventory)
        """
        current_room = game_state.current_room
        room = game_state.world.get_room(current_room)
        
        # First, try to unlock a door
        for direction, destination in room.get("exits", {}).items():
            dest_room = game_state.world.get_room(destination)
            if dest_room and dest_room.get("locked", False) and destination in self.unlocks:
                dest_room["locked"] = False
                message = f"You use the {self.display_name()} to unlock the way to the {destination.replace('_', ' ')}."
                
                # Handle key consumption for doors
                if self.single_use:
                    game_state.player.remove_from_inventory(self.name)
                    return True, message + " The key crumbles to dust after use."
                return True, message
        
        # If no door was unlocked, try to find a treasure box in the room
        box_found = False
        box = None
        box_name = None
        box_in_inventory = False
        
        # Import ItemFactory here to avoid circular imports
        from items.item_factory import ItemFactory
        
        # First check the room for boxes
        if "items" in room:
            for item_index, item_name in enumerate(room["items"]):
                item = ItemFactory.get_item(item_name)
                
                # Safe checking for treasure boxes
                if not item:
                    continue
                
                item_type = getattr(item, "type", "item")
                if item_type != "treasure_box":
                    continue
                    
                # Check if this key can unlock this box
                required_key = getattr(item, "required_key", None)
                if item_name in self.unlocks or required_key == self.name:
                    # Found a box to unlock in the room!
                    box_found = True
                    box_name = item_name
                    box = item
                    # Remove the box from the room
                    room["items"].pop(item_index)
                    break
        
        # If no box found in room, check player's inventory
        if not box_found:
            inventory_items = list(game_state.player.inventory.keys())
            for item_name in inventory_items:
                item = ItemFactory.get_item(item_name)
                
                # Safe checking for treasure boxes
                if not item:
                    continue
                    
                item_type = getattr(item, "type", "item")
                if item_type != "treasure_box":
                    continue
                    
                # Check if this key can unlock this box
                required_key = getattr(item, "required_key", None)
                if item_name in self.unlocks or required_key == self.name:
                    # Found a box to unlock in inventory!
                    box_found = True
                    box_name = item_name
                    box = item
                    box_in_inventory = True
                    # Remove the box from inventory
                    game_state.player.remove_from_inventory(item_name)
                    break
        
        # If we found a box to unlock (either in room or inventory)
        if box_found and box and box_name:
            # Generate the loot (if the box has a generate_loot method)
            loot = {}
            if hasattr(box, "generate_loot") and callable(box.generate_loot):
                loot = box.generate_loot(game_state)
            else:
                # Fallback - simple random loot
                import random
                loot = {"coin": random.randint(5, 15)}
            
            # Process the loot
            loot_messages = []
            for loot_item, quantity in loot.items():
                if loot_item == "coin":
                    game_state.coins += quantity
                    loot_messages.append(f"{quantity} coins")
                else:
                    # Add to player's inventory
                    for _ in range(quantity):
                        game_state.player.add_to_inventory(loot_item)
                    
                    # Create display message
                    loot_item_obj = ItemFactory.get_item(loot_item)
                    if loot_item_obj:
                        if quantity > 1:
                            loot_messages.append(f"{quantity}x {loot_item_obj.display_name()}")
                        else:
                            loot_messages.append(loot_item_obj.display_name())
                    else:
                        if quantity > 1:
                            loot_messages.append(f"{quantity}x {loot_item.replace('_', ' ')}")
                        else:
                            loot_messages.append(loot_item.replace('_', ' '))
            
            # Create result message
            if loot_messages:
                loot_list = ", ".join(loot_messages)
                if box_in_inventory:
                    message = f"You use the {self.display_name()} to unlock the {box.display_name()} from your inventory and find: {loot_list}."
                else:
                    message = f"You use the {self.display_name()} to unlock the {box.display_name()} and find: {loot_list}."
            else:
                if box_in_inventory:
                    message = f"You use the {self.display_name()} to unlock the {box.display_name()} from your inventory, but it's empty!"
                else:
                    message = f"You use the {self.display_name()} to unlock the {box.display_name()}, but it's empty!"
            
            # Important: Consume the key manually if it's single-use
            if self.single_use:
                # Explicitly remove the key from player's inventory
                game_state.player.remove_from_inventory(self.name)
                return True, message + " The key breaks after use."
            return True, message
        
        return False, f"There's nothing here that the {self.display_name()} can unlock."

class Tool(Item):
    def __init__(self, name, description, tool_type, value=5, aliases=None):
        """
        Tool item for special interactions
        
        Args:
            name (str): Internal name of the tool
            description (str): Human-readable description
            tool_type (str): Type of tool (e.g., "navigation", "digging")
            value (int): Base value in coins
            aliases (list): Alternative names for the item
        """
        super().__init__(name, description, value, usable=True, aliases=aliases)
        self.tool_type = tool_type
        self.type = "tool"
    
    def use(self, game_state):
        """Use the tool based on its type"""
        current_room = game_state.current_room
        
        if self.name == "torch" and current_room in ["entrance", "cavern", "narrow_passage"]:
            return True, "You light the torch, illuminating the dark cave around you."
            
        elif self.name == "boat" and current_room == "underground_lake":
            # Add special boat navigation logic
            return True, "You push the boat into the water and paddle to a small island in the center of the lake."
            
        elif self.name == "pickaxe" and current_room in ["narrow_passage", "hidden_grotto"]:
            # Mining mechanic
            return True, "You mine the wall, revealing small gems hidden in the rock."
            
        return False, f"You can't figure out how to use the {self.display_name()} here."

GEMS = {
    "gem": Gem(
        "gem", 
        "A small, sparkling gemstone.",
        value=10,
        rarity="common",
        aliases=["gemstone", "stone", "crystal"]
    ),
    "ruby": Gem(
        "ruby", 
        "A brilliant red gemstone that catches the light beautifully.",
        value=25,
        rarity="uncommon",
        aliases=["red gem", "red stone"]
    ),
    "sapphire": Gem(
        "sapphire", 
        "A deep blue gemstone of impressive clarity.",
        value=30,
        rarity="uncommon",
        aliases=["blue gem", "blue stone"]
    ),
    "emerald": Gem(
        "emerald", 
        "A vibrant green gemstone, rare and valuable.",
        value=40,
        rarity="rare",
        aliases=["green gem", "green stone"]
    ),
    "diamond": Gem(
        "diamond", 
        "A flawless diamond that sparkles with inner fire.",
        value=75,
        rarity="epic",
        aliases=["clear gem", "white gem"]
    )
}

QUEST_ITEMS = {
    "ancient_scroll": QuestItem(
        "ancient_scroll", 
        "A scroll with mysterious writing. It seems important.",
        aliases=["scroll", "parchment", "old scroll"]
    ),
    "golden_crown": QuestItem(
        "golden_crown", 
        "An ornate crown made of solid gold. It must be valuable.",
        aliases=["crown", "gold crown", "royal crown"]
    )
}

KEYS = {
    "ancient_key": Key(
        "ancient_key", 
        "An ornate key made of strange metal. It feels warm to the touch.",
        unlocks=["treasure_room"],
        value=5,
        aliases=["key", "ornate key", "strange key", "treasure key"]
    )
}

TOOLS = {
    "torch": Tool(
        "torch", 
        "A wooden torch that can be lit to illuminate dark areas.",
        tool_type="light",
        value=2,
        aliases=["light", "wooden torch", "fire"]
    ),
    "boat": Tool(
        "boat", 
        "A small wooden boat, just big enough for one person.",
        tool_type="navigation",
        value=10,
        aliases=["raft", "canoe", "wooden boat"]
    ),
    "pickaxe": Tool(
        "pickaxe", 
        "A sturdy pickaxe for mining.",
        tool_type="mining",
        value=8,
        aliases=["pick", "mining tool", "axe"]
    )
}

def get_gem(gem_name):
    """Get a gem from the predefined gems"""
    return GEMS.get(gem_name)

def get_quest_item(item_name):
    """Get a quest item from the predefined quest items"""
    return QUEST_ITEMS.get(item_name)

def get_key(key_name):
    """Get a key from the predefined keys"""
    return KEYS.get(key_name)

def get_tool(tool_name):
    """Get a tool from the predefined tools"""
    return TOOLS.get(tool_name)