# utils.py
import os
import time
import random
from datetime import datetime

def get_timestamp():
    """Get a formatted timestamp for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dir_exists(directory):
    """Ensure a directory exists, creating it if necessary"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def format_time_delta(seconds):
    """Format a time delta in a human-readable way"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours} hours, {minutes} minutes"

def get_random_element(collection, weights=None):
    """Get a random element from a collection, optionally with weights"""
    if not collection:
        return None
    
    if weights:
        # Normalize weights if needed
        if len(weights) != len(collection):
            weights = None
    
    if weights:
        return random.choices(collection, weights=weights, k=1)[0]
    else:
        return random.choice(collection)

def clamp(value, min_value, max_value):
    """Clamp a value between a minimum and maximum"""
    return max(min_value, min(value, max_value))

def dice_roll(num_dice, sides, modifier=0):
    """Roll dice with the format NdS+M (N dice with S sides, plus modifier M)"""
    result = sum(random.randint(1, sides) for _ in range(num_dice)) + modifier
    return result

def calculate_chance(base_chance, modifiers=None):
    """Calculate a chance with modifiers"""
    final_chance = base_chance
    
    if modifiers:
        for modifier in modifiers:
            if isinstance(modifier, (int, float)):
                # Additive modifier
                final_chance += modifier
            elif isinstance(modifier, tuple) and len(modifier) == 2:
                # Multiplicative modifier (name, value)
                final_chance *= modifier[1]
    
    # Clamp between 0 and 1
    return clamp(final_chance, 0, 1)

def parse_duration(duration_str):
    """Parse a duration string into seconds"""
    if not duration_str:
        return 0
        
    duration_str = duration_str.lower()
    total_seconds = 0
    
    # Parse formats like "1h30m", "45s", "2d", etc.
    parts = []
    current_num = ""
    
    for char in duration_str:
        if char.isdigit():
            current_num += char
        elif char in "dhms":
            if current_num:
                parts.append((int(current_num), char))
                current_num = ""
    
    # Add any trailing number without a unit as seconds
    if current_num:
        parts.append((int(current_num), "s"))
    
    # Calculate total seconds
    for value, unit in parts:
        if unit == "d":
            total_seconds += value * 86400  # days
        elif unit == "h":
            total_seconds += value * 3600   # hours
        elif unit == "m":
            total_seconds += value * 60     # minutes
        elif unit == "s":
            total_seconds += value          # seconds
    
    return total_seconds

def get_weather_description(weather_type, intensity=1.0):
    """Generate a weather description based on type and intensity"""
    base_descriptions = {
        "clear": [
            "The air is still and clear.",
            "Visibility is excellent in these conditions.",
            "The atmosphere is calm and serene."
        ],
        "misty": [
            "A light mist hangs in the air.",
            "Wisps of fog curl around your ankles.",
            "The mist limits visibility somewhat."
        ],
        "humid": [
            "The air is damp and humid.",
            "Moisture clings to every surface.",
            "The humid air feels heavy to breathe."
        ],
        "stormy": [
            "Distant rumblings can be heard.",
            "The air crackles with energy.",
            "Occasional tremors shake the ground."
        ],
        "magical": [
            "The air shimmers with strange energy.",
            "Tiny motes of light dance in the air.",
            "You feel a tingling sensation on your skin."
        ]
    }
    
    # Get base description
    if weather_type not in base_descriptions:
        weather_type = "clear"
        
    descriptions = base_descriptions[weather_type]
    base_desc = get_random_element(descriptions)
    
    # Add intensity modifiers
    if intensity < 0.5:
        intensity_desc = "very mild"
    elif intensity < 0.8:
        intensity_desc = "mild"
    elif intensity < 1.2:
        intensity_desc = "moderate"
    elif intensity < 1.5:
        intensity_desc = "strong"
    else:
        intensity_desc = "extreme"
    
    # For very mild effects, don't mention intensity
    if intensity >= 0.8:
        return f"{base_desc} The {intensity_desc} {weather_type} conditions affect the environment."
    else:
        return base_desc

def get_environment_effect_description(effect_name, value):
    """Generate a description of an environmental effect"""
    effect_descriptions = {
        "enemy_accuracy": {
            "positive": "The clear conditions give enemies better accuracy.",
            "negative": "The poor visibility makes it harder for enemies to hit you."
        },
        "player_attack": {
            "positive": "The conditions enhance your attacks.",
            "negative": "The conditions make it harder to move and attack effectively."
        },
        "enemy_spawn_rate": {
            "positive": "The environment seems peaceful; creatures are less likely to appear.",
            "negative": "The disturbances seem to be attracting more creatures to this area."
        },
        "healing_bonus": {
            "positive": "There's a restorative quality to the air here.",
            "negative": "The oppressive atmosphere makes recovery more difficult."
        }
    }
    
    if effect_name not in effect_descriptions:
        return ""
    
    if effect_name == "enemy_accuracy" or effect_name == "player_attack":
        return effect_descriptions[effect_name]["negative"] if value < 0 else effect_descriptions[effect_name]["positive"]
    elif effect_name == "enemy_spawn_rate":
        return effect_descriptions[effect_name]["negative"] if value > 1 else effect_descriptions[effect_name]["positive"]
    elif effect_name == "healing_bonus":
        return effect_descriptions[effect_name]["positive"] if value > 1 else effect_descriptions[effect_name]["negative"]
    
    return ""