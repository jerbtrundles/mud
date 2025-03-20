# enemy_drops.py
import random
from core.utils import calculate_chance

def get_enemy_drops(enemy_name, enemy_health_percentage, player_level):
    """
    Generate drops when an enemy is defeated
    
    Args:
        enemy_name (str): The name of the defeated enemy
        enemy_health_percentage (float): Original enemy health as percentage of max
                                         (higher percentage = stronger enemy)
        player_level (int): Current player level
        
    Returns:
        dict: Dictionary of {item_name: quantity} representing drops
    """
    drops = {}
    
    # Base drop rates for different enemy types
    drop_rates = {
        # format: {item_category: base_chance}
        "goblin": {
            "common_treasure_box": 0.1,  # 10% chance
            "uncommon_treasure_box": 0.03,
            "common_box_key": 0.15,
            "gold": (2, 10)  # Gold range (min, max)
        },
        "skeleton": {
            "common_treasure_box": 0.15,
            "uncommon_treasure_box": 0.05,
            "rare_treasure_box": 0.01,
            "common_box_key": 0.2,
            "uncommon_box_key": 0.05,
            "gold": (3, 12)
        },
        "troll": {
            "common_treasure_box": 0.2,
            "uncommon_treasure_box": 0.1,
            "rare_treasure_box": 0.03,
            "common_box_key": 0.25,
            "uncommon_box_key": 0.1,
            "rare_box_key": 0.02,
            "gold": (5, 20)
        },
        "orc": {
            "common_treasure_box": 0.18,
            "uncommon_treasure_box": 0.08,
            "rare_treasure_box": 0.02,
            "common_box_key": 0.23,
            "uncommon_box_key": 0.07,
            "gold": (4, 15)
        },
        "spider": {
            "common_treasure_box": 0.08,
            "common_box_key": 0.12,
            "antidote": 0.2,
            "gold": (1, 8)
        },
        "giant spider": {
            "uncommon_treasure_box": 0.12,
            "uncommon_box_key": 0.18,
            "antidote": 0.2,
            "gold": (1, 8)
        },
        "ghost": {
            "uncommon_treasure_box": 0.15,
            "rare_treasure_box": 0.05,
            "uncommon_box_key": 0.2,
            "rare_box_key": 0.05,
            "gold": (3, 15)
        },
        "rat": {
            "common_treasure_box": 0.05,
            "common_box_key": 0.1,
            "gold": (1, 5)
        },
        "bat": {
            "common_box_key": 0.08,
            "gold": (1, 4)
        },
        "slime": {
            "common_treasure_box": 0.07,
            "common_box_key": 0.1,
            "gold": (1, 6)
        },
        "zombie": {
            "common_treasure_box": 0.12,
            "uncommon_treasure_box": 0.04,
            "common_box_key": 0.18,
            "uncommon_box_key": 0.04,
            "gold": (2, 10)
        }
    }
    
    # Get proper drop rates for this enemy
    # Match by partial name (e.g., "hobgoblin" should use "goblin" rates)
    enemy_rate = None
    for rate_name, rates in drop_rates.items():
        if rate_name in enemy_name:
            enemy_rate = rates
            break
    
    # Use generic rates if no specific match
    if not enemy_rate:
        enemy_rate = {
            "common_treasure_box": 0.1,
            "common_box_key": 0.15,
            "gold": (1, 8)
        }
    
    # Add gold/coins drop (almost always drops some gold)
    if "gold" in enemy_rate and random.random() < 0.9:  # 90% chance for gold
        gold_range = enemy_rate["gold"]
        # Adjust gold based on enemy health and player level
        min_gold = max(1, int(gold_range[0] * enemy_health_percentage))
        max_gold = max(min_gold, int(gold_range[1] * enemy_health_percentage))
        
        # Player level bonus
        level_bonus = max(0, player_level - 1)  # No bonus at level 1
        if level_bonus > 0:
            min_gold += level_bonus // 2
            max_gold += level_bonus
            
        gold_amount = random.randint(min_gold, max_gold)
        drops["coin"] = gold_amount
    
    # Process treasure box drops
    for drop_type, base_chance in enemy_rate.items():
        # Skip non-treasure drops
        if drop_type == "gold" or not (drop_type.endswith("_treasure_box") or drop_type.endswith("_box_key")):
            continue
            
        # Calculate actual drop chance with modifiers
        modifiers = []
        
        # Higher level enemies drop better loot
        if enemy_health_percentage > 0.8:
            modifiers.append(0.1)  # +10% for strong enemies
        
        # Higher player levels slightly increase rare drops
        if player_level > 1 and ("rare" in drop_type or "epic" in drop_type or "legendary" in drop_type):
            level_bonus = min(0.1, (player_level - 1) * 0.02)  # Up to +10% at level 6+
            modifiers.append(level_bonus)
        
        # Calculate final chance with all modifiers
        final_chance = calculate_chance(base_chance, modifiers)
        
        # Check if this item drops
        if random.random() < final_chance:
            drops[drop_type] = 1  # Most drops are quantity 1
    
    # Special case: extremely rare legendary drops from any enemy
    if random.random() < 0.001 * player_level * enemy_health_percentage:  # Very rare, affected by level and enemy strength
        if random.random() < 0.7:
            drops["legendary_box_key"] = 1
        else:
            drops["legendary_treasure_box"] = 1
    
    return drops