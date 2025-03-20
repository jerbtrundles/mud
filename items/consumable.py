# consumable.py
from items.item import Item

class Consumable(Item):
    def __init__(self, name, description, value=5, 
                 health_restore=0, effects=None, cure_effects=None, type="consumable", 
                 stackable=True, max_stack=5, aliases=None):
        """
        Consumable class for food and drink items
        
        Args:
            name (str): Internal name of the item
            description (str): Human-readable description
            value (int): Base value in coins
            health_restore (int): Amount of health restored when consumed
            effects (dict): Additional effects (e.g., {"strength": 2, "duration": 60})
            cure_effects (list): List of status effects this item cures (e.g., ["poison", "bleeding"])
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
        self.cure_effects = cure_effects or []
        self.type = type  # Can be "food", "drink", or generic "consumable"
    
    def use(self, game_state):
        """Use/consume the item"""
        player = game_state.player
        message = []
        
        # Restore health if applicable
        if self.health_restore > 0:
            # Get the current region and its environment effects
            current_region = game_state.world.get_region_for_room(game_state.current_room)
            
            if current_region:
                # Get environmental effects from the region's environment system
                env_effects = current_region.environment_system.get_effects(game_state.current_room)
                healing_bonus = env_effects.get("healing_bonus", 1.0)  # Default multiplier of 1.0
            else:
                healing_bonus = 1.0  # No effects if no region found
            
            # Apply healing with environment bonus
            base_heal = self.health_restore
            modified_heal = int(base_heal * healing_bonus)
            actual_heal = player.heal(modified_heal)
            
            # Mention the environmental bonus if significant
            if healing_bonus > 1.1:  # More than 10% bonus
                if current_region:
                    weather = current_region.environment_system.get_weather(game_state.current_room)
                    message.append(f"You consume the {self.display_name()} and recover {actual_heal} health points.")
                    message.append(f"The {weather} environment enhances the healing effect!")
                else:
                    message.append(f"You consume the {self.display_name()} and recover {actual_heal} health points.")
            else:
                message.append(f"You consume the {self.display_name()} and recover {actual_heal} health points.")
                
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
        
        # Cure status effects if applicable
        if self.cure_effects and hasattr(game_state, 'status_effect_manager'):
            cured_effects = []
            for effect_name in self.cure_effects:
                if game_state.status_effect_manager.has_effect(effect_name):
                    if game_state.status_effect_manager.remove_effect(effect_name, suppress_message=True):
                        cured_effects.append(effect_name)
            
            if cured_effects:
                if len(cured_effects) == 1:
                    message.append(f"The {self.display_name()} cures your {cured_effects[0]}!")
                else:
                    effect_list = ", ".join(cured_effects)
                    message.append(f"The {self.display_name()} cures your {effect_list}!")
        
        return True, "\n".join(message)

# Predefined consumables
CONSUMABLES = {
    "antidote": Consumable(
        "antidote", 
        "A green potion that neutralizes poison.",
        health_restore=5,  # Minor healing
        value=8,
        type="drink",
        cure_effects=["poison"],  # Specifically cures poison
        aliases=["poison antidote", "green potion", "cure"]
    ),
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