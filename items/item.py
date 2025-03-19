# item.py
class Item:
    def __init__(self, name, description, value=1, stackable=False, max_stack=1, usable=False, aliases=None):
        """
        Base class for all items in the game
        
        Args:
            name (str): Internal name of the item (snake_case)
            description (str): Human-readable description
            value (int): Base value in coins
            stackable (bool): Whether multiple of this item can stack in inventory
            max_stack (int): Maximum number of items in a stack
            usable (bool): Whether the item can be used
            aliases (list): Alternative names for the item
        """
        self.name = name
        self.description = description
        self.value = value
        self.stackable = stackable
        self.max_stack = max_stack if stackable else 1
        self.usable = usable
        self.aliases = aliases or []
        self.type = "item"  # Base type for generic items
        
        # Automatically add some basic aliases
        base_name = name.replace('_', ' ')
        parts = base_name.split()
        if len(parts) > 1 and parts[-1] not in self.aliases:
            # Add the last word as an alias (e.g., "healing potion" -> "potion")
            self.aliases.append(parts[-1])
        if len(parts) > 1 and parts[0] not in self.aliases:
            # Add the first word as an alias (e.g., "rusty sword" -> "rusty")
            self.aliases.append(parts[0])
    
    def display_name(self):
        """Return a friendly display name (spaces instead of underscores)"""
        return self.name.replace('_', ' ')
    
    def can_use(self, game_state):
        """Check if the item can be used in the current context"""
        return self.usable
    
    def use(self, game_state):
        """Use the item - to be overridden by subclasses"""
        if not self.usable:
            return False, f"You can't figure out how to use the {self.display_name()}."
        return True, f"You use the {self.display_name()}."
    
    def get_sell_price(self):
        """Get the price a shop will pay for this item"""
        return max(1, self.value // 2)
    
    def get_buy_price(self):
        """Get the price a shop will charge for this item"""
        return self.value
    
    def can_sell(self):
        """Check if the item can be sold to shops"""
        return True
    
    def __str__(self):
        return self.display_name()