# consumable.py
from items.item import Item

class Consumable(Item):
    def __init__(self, name, description, value=5, 
                 health_restore=0, effects=None, type="consumable", 
                 stackable=True, max_stack=5, aliases=None):
        """
        Consumable class for food and drink items
        
        Args:
            name (str): Internal name of the item
            description (str): Human-readable description
            value (int): Base value in coins
            health_restore (int): Amount of health restored when consumed
            effects (dict): Additional effects (e.g., {"strength": 2, "duration": 60})
            type (str): Specific type ("food", "drink", or generic "consumable")
            stackable (bool): Whether multiple of this item can stack in inventory
            max_stack (int): Maximum number of items in a stack
            aliases (list): Alternative names for the item
        """
        super().__init__(
            name, description, value, 
            stackable=stackable, max_stack=max_stack, usable=True,
            aliases=aliases
        )
        self.health_restore = health_restore
        self.effects = effects or {}
        self.type = type  # Can be "food", "drink", or generic "consumable"
    
    def use(self, game_state):
        """Use/consume the item"""
        player = game_state.player
        message = []
        
        # Restore health if applicable
        if self.health_restore > 0:
            player.heal(self.health_restore)
            message.append(f"You consume the {self.display_name()} and recover {self.health_restore} health points.")
            message.append(f"Health: {player.health}/{player.max_health}")
        else:
            message.append(f"You consume the {self.display_name()}.")
        
        # Apply additional effects
        for effect, value in self.effects.items():
            if effect == "strength":
                # Example temp buff implementation
                player.temp_attack_bonus = value
                player.temp_buff_end_time = game_state.get_game_time() + self.effects.get("duration", 60)
                message.append(f"You feel stronger! +{value} to attack for {self.effects.get('duration', 60)} seconds.")
        
        return True, "\n".join(message)


# Predefined consumables
CONSUMABLES = {
    "healing_potion": Consumable(
        "healing_potion", 
        "A red potion that restores health.",
        health_restore=20,
        value=5,
        type="drink",
        aliases=["potion", "red potion", "health potion", "heal potion"]
    ),
    "strong_healing_potion": Consumable(
        "strong_healing_potion", 
        "A vibrant red potion that restores significant health.",
        health_restore=50,
        value=15,
        type="drink",
        aliases=["strong potion", "big potion", "large potion"]
    ),
    "stamina_potion": Consumable(
        "stamina_potion", 
        "A green potion that temporarily increases attack power.",
        health_restore=0,
        value=10,
        type="drink",
        effects={"strength": 5, "duration": 60},
        aliases=["green potion", "strength potion"]
    ),
    "bread": Consumable(
        "bread", 
        "A small loaf of bread. Slightly restores health.",
        health_restore=5,
        value=2,
        type="food",
        aliases=["loaf", "food"]
    ),
    "cooked_meat": Consumable(
        "cooked_meat", 
        "A piece of cooked meat. Restores health.",
        health_restore=15,
        value=4,
        type="food",
        aliases=["meat", "steak", "food"]
    ),
    "apple": Consumable(
        "apple", 
        "A fresh apple. Slightly restores health.",
        health_restore=3,
        value=1,
        type="food",
        aliases=["fruit", "food"]
    )
}

def get_consumable(consumable_name):
    """Get a consumable from the predefined consumables"""
    return CONSUMABLES.get(consumable_name)