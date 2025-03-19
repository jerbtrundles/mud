# treasure_box.py
import random
from items.item import Item
from core.utils import calculate_chance, get_random_element

class TreasureBox(Item):
    """
    A locked treasure box that can be opened with the appropriate key.
    Contains random loot based on the box's rarity level.
    """
    def __init__(self, name, description, rarity="common", required_key=None, value=5, aliases=None):
        """
        Initialize a treasure box
        
        Args:
            name (str): Internal name of the box
            description (str): Human-readable description
            rarity (str): Rarity level (common, uncommon, rare, epic, legendary)
            required_key (str): Name of the key item required to open this box
            value (int): Base value in coins
            aliases (list): Alternative names for the item
        """
        super().__init__(name, description, value, stackable=False, usable=True, aliases=aliases)
        self.rarity = rarity
        self.required_key = required_key or f"{rarity}_box_key"
        self.type = "treasure_box"
        
        # Set default aliases if none provided
        if not aliases:
            self.aliases = [rarity + " box", "box", "chest", "treasure"]
    
    def can_use(self, game_state):
        """Check if the box can be used (opened) - player must have the right key"""
        return game_state.player.has_item(self.required_key)
    
    def use(self, game_state):
        """Try to open the treasure box with a key"""
        if not self.can_use(game_state):
            return False, f"You need a {self.required_key.replace('_', ' ')} to open this {self.display_name()}."
        
        # Remove key if it's consumed when used
        from items.item_factory import ItemFactory
        key_item = ItemFactory.get_item(self.required_key)
        if key_item and hasattr(key_item, 'single_use') and key_item.single_use:
            game_state.player.remove_from_inventory(self.required_key)
            key_consumed_msg = f"The {key_item.display_name()} breaks after use."
        else:
            key_consumed_msg = ""
        
        # Generate loot based on rarity
        loot = self.generate_loot(game_state)
        
        # Add loot to player inventory
        loot_messages = []
        coins_found = 0
        
        for item_name, quantity in loot.items():
            if item_name == "coin":
                coins_found = quantity
                game_state.coins += quantity
                loot_messages.append(f"{quantity} coins")
            else:
                # Add non-coin items to inventory
                for _ in range(quantity):
                    game_state.player.add_to_inventory(item_name)
                
                # Get display name for message
                item_obj = ItemFactory.get_item(item_name)
                if item_obj:
                    if quantity > 1:
                        loot_messages.append(f"{quantity}x {item_obj.display_name()}")
                    else:
                        loot_messages.append(item_obj.display_name())
                else:
                    loot_messages.append(f"{quantity}x {item_name.replace('_', ' ')}")
        
        # Create result message
        if loot_messages:
            loot_list = ", ".join(loot_messages)
            result_msg = f"You open the {self.display_name()} and find: {loot_list}."
            if key_consumed_msg:
                result_msg += " " + key_consumed_msg
            return True, result_msg
        else:
            return True, f"You open the {self.display_name()}, but it's empty! {key_consumed_msg}"
    
    def generate_loot(self, game_state):
        """
        Generate random loot based on the box's rarity
        
        Returns:
            dict: Dictionary of {item_name: quantity}
        """
        loot = {}
        
        # Base number of items depends on rarity
        rarity_item_counts = {
            "common": (1, 2),     # 1-2 items
            "uncommon": (2, 3),   # 2-3 items
            "rare": (2, 4),       # 2-4 items
            "epic": (3, 5),       # 3-5 items
            "legendary": (4, 6)   # 4-6 items
        }
        
        # Coin amounts based on rarity
        rarity_coin_ranges = {
            "common": (5, 15),       # 5-15 coins
            "uncommon": (10, 25),    # 10-25 coins
            "rare": (20, 50),        # 20-50 coins
            "epic": (40, 80),        # 40-80 coins
            "legendary": (75, 150)   # 75-150 coins
        }
        
        # Chance to find special items based on rarity
        rarity_special_chance = {
            "common": 0.1,      # 10% chance for special item
            "uncommon": 0.2,    # 20% chance
            "rare": 0.4,        # 40% chance
            "epic": 0.6,        # 60% chance
            "legendary": 0.9    # 90% chance
        }
        
        # Always add coins
        coin_range = rarity_coin_ranges.get(self.rarity, (5, 15))
        coin_amount = random.randint(coin_range[0], coin_range[1])
        
        # Player level can influence coin amount (higher level = more coins)
        player_level_bonus = game_state.player.level - 1  # No bonus at level 1
        if player_level_bonus > 0:
            coin_amount += random.randint(1, player_level_bonus * 5)
            
        loot["coin"] = coin_amount
        
        # Determine number of additional items
        item_count_range = rarity_item_counts.get(self.rarity, (1, 2))
        item_count = random.randint(item_count_range[0], item_count_range[1])
        
        # Get possible loot items based on rarity
        possible_loot = self._get_possible_loot(self.rarity)
        
        # Add random items from possible loot
        for _ in range(item_count):
            if not possible_loot:
                break
                
            # Select an item based on its weight
            item_choices = list(possible_loot.keys())
            item_weights = [info["weight"] for info in possible_loot.values()]
            selected_item = random.choices(item_choices, weights=item_weights, k=1)[0]
            
            # Determine quantity
            quantity_range = possible_loot[selected_item].get("quantity", (1, 1))
            quantity = random.randint(quantity_range[0], quantity_range[1])
            
            # Add to loot
            if selected_item in loot:
                loot[selected_item] += quantity
            else:
                loot[selected_item] = quantity
                
            # Don't pick the same item twice unless it's consumable
            from items.item_factory import ItemFactory
            item_obj = ItemFactory.get_item(selected_item)
            if item_obj and not getattr(item_obj, "stackable", False):
                del possible_loot[selected_item]
        
        # Chance for a special item (gem, weapon, armor)
        special_chance = rarity_special_chance.get(self.rarity, 0.1)
        if random.random() < special_chance:
            special_items = self._get_special_loot(self.rarity)
            if special_items:
                special_item = random.choice(list(special_items.keys()))
                loot[special_item] = 1
        
        return loot
    
    def _get_possible_loot(self, rarity):
        """Get possible loot items for a given rarity"""
        # This is a simplified loot table - you can expand it as needed
        loot_table = {
            "common": {
                "healing_potion": {"weight": 5, "quantity": (1, 1)},
                "bread": {"weight": 3, "quantity": (1, 2)},
                "stick": {"weight": 2, "quantity": (1, 2)},
                "cloth": {"weight": 2, "quantity": (1, 2)},
                "torch": {"weight": 1, "quantity": (1, 1)}
            },
            "uncommon": {
                "healing_potion": {"weight": 5, "quantity": (1, 2)},
                "cooked_meat": {"weight": 3, "quantity": (1, 2)},
                "stamina_potion": {"weight": 2, "quantity": (1, 1)},
                "gem": {"weight": 1, "quantity": (1, 1)}
            },
            "rare": {
                "strong_healing_potion": {"weight": 4, "quantity": (1, 1)},
                "stamina_potion": {"weight": 3, "quantity": (1, 2)},
                "ruby": {"weight": 2, "quantity": (1, 1)},
                "sapphire": {"weight": 2, "quantity": (1, 1)}
            },
            "epic": {
                "strong_healing_potion": {"weight": 4, "quantity": (1, 2)},
                "emerald": {"weight": 3, "quantity": (1, 1)},
                "stamina_potion": {"weight": 2, "quantity": (1, 3)}
            },
            "legendary": {
                "strong_healing_potion": {"weight": 3, "quantity": (2, 3)},
                "diamond": {"weight": 2, "quantity": (1, 1)},
                "stamina_potion": {"weight": 2, "quantity": (2, 4)}
            }
        }
        
        # Combine loot tables from current rarity and lower rarities
        rarities_to_include = []
        if rarity == "legendary":
            rarities_to_include = ["epic", "rare", "uncommon", "common", "legendary"]
        elif rarity == "epic":
            rarities_to_include = ["rare", "uncommon", "common", "epic"]
        elif rarity == "rare":
            rarities_to_include = ["uncommon", "common", "rare"]
        elif rarity == "uncommon":
            rarities_to_include = ["common", "uncommon"]
        else:
            rarities_to_include = ["common"]
            
        combined_loot = {}
        for r in rarities_to_include:
            if r in loot_table:
                for item, info in loot_table[r].items():
                    # Higher rarities have higher weight for their specific items
                    if r == rarity:
                        info["weight"] *= 2
                    combined_loot[item] = info
                
        return combined_loot
    
    def _get_special_loot(self, rarity):
        """Get possible special loot items (rare equipment/items)"""
        special_loot = {
            "common": {
                "rusty_sword": 5,
                "leather_armor": 5
            },
            "uncommon": {
                "steel_sword": 5,
                "chainmail": 5,
                "uncommon_box_key": 2
            },
            "rare": {
                "ancient_blade": 5,
                "plate_armor": 5,
                "rare_box_key": 2
            },
            "epic": {
                "enchanted_sword": 5,
                "reinforced_leather_armor": 5,
                "epic_box_key": 2
            },
            "legendary": {
                "legendary_box_key": 5,
                "ancient_scroll": 3,
                "golden_crown": 2
            }
        }
        
        # Return appropriate special loot based on rarity
        result = {}
        
        # Include current rarity and possible one level higher
        if rarity in special_loot:
            result.update({item: {"weight": weight} for item, weight in special_loot[rarity].items()})
            
        # Small chance for items from 1 tier lower (if available)
        lower_rarities = {
            "legendary": "epic",
            "epic": "rare",
            "rare": "uncommon",
            "uncommon": "common"
        }
        
        if rarity in lower_rarities and random.random() < 0.3:  # 30% chance
            lower_rarity = lower_rarities[rarity]
            if lower_rarity in special_loot:
                result.update({item: {"weight": weight/2} for item, weight in special_loot[lower_rarity].items()})
        
        return result


# Define different treasure box types
TREASURE_BOXES = {
    "common_treasure_box": TreasureBox(
        "common_treasure_box",
        "A simple wooden box with a basic lock. It might contain some useful items.",
        rarity="common",
        required_key="common_box_key",
        value=5,
        aliases=["wooden box", "small chest", "common chest"]
    ),
    "uncommon_treasure_box": TreasureBox(
        "uncommon_treasure_box",
        "A sturdy box with iron reinforcements. The lock looks more complex than usual.",
        rarity="uncommon",
        required_key="uncommon_box_key",
        value=15,
        aliases=["iron box", "reinforced chest", "sturdy chest"]
    ),
    "rare_treasure_box": TreasureBox(
        "rare_treasure_box",
        "An ornate box with silver decorations. It feels heavy, suggesting valuable contents.",
        rarity="rare",
        required_key="rare_box_key",
        value=30,
        aliases=["silver box", "ornate chest", "valuable chest"]
    ),
    "epic_treasure_box": TreasureBox(
        "epic_treasure_box",
        "A beautiful gold-inlaid box with intricate patterns. The lock is masterfully crafted.",
        rarity="epic",
        required_key="epic_box_key",
        value=50,
        aliases=["golden box", "intricate chest", "premium chest"]
    ),
    "legendary_treasure_box": TreasureBox(
        "legendary_treasure_box",
        "A stunning box that seems to shimmer with magical energy. The lock has strange runes.",
        rarity="legendary",
        required_key="legendary_box_key",
        value=100,
        aliases=["magical box", "runic chest", "legendary chest"]
    )
}

def get_treasure_box(box_name):
    """Get a treasure box from the predefined boxes"""
    return TREASURE_BOXES.get(box_name)

def get_random_treasure_box(rarity=None):
    """
    Get a random treasure box, optionally of a specific rarity
    
    Args:
        rarity (str, optional): Specific rarity to get, or None for weighted random
        
    Returns:
        TreasureBox: A treasure box instance
    """
    if rarity:
        # Find a box of the specified rarity
        for box_name, box in TREASURE_BOXES.items():
            if box.rarity == rarity:
                return box
    
    # Default weight distribution for random boxes
    box_weights = {
        "common_treasure_box": 100,
        "uncommon_treasure_box": 50,
        "rare_treasure_box": 20,
        "epic_treasure_box": 5,
        "legendary_treasure_box": 1
    }
    
    # Select a random box based on weights
    box_names = list(box_weights.keys())
    weights = list(box_weights.values())
    
    selected_box_name = random.choices(box_names, weights=weights, k=1)[0]
    return TREASURE_BOXES.get(selected_box_name)