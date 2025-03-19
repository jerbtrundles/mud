# herbs.py
from items.item import Item
from items.consumable import Consumable

HERBS = {
    "herb_bundle": Item(
        "herb_bundle", 
        "A bundle of medicinal herbs carefully tied together.",
        value=3,
        stackable=True,
        max_stack=10,
        usable=True,
        aliases=["herbs", "medicinal herbs", "bundle"]
    ),
    "glowing_mushroom": Item(
        "glowing_mushroom", 
        "A mushroom that emits a soft blue glow. Has alchemical properties.",
        value=5,
        stackable=True,
        max_stack=10,
        usable=True,
        aliases=["mushroom", "luminous mushroom", "blue mushroom"]
    ),
    "waterbloom": Item(
        "waterbloom", 
        "A delicate aquatic flower that thrives in dark waters. Used in advanced potions.",
        value=7,
        stackable=True,
        max_stack=5,
        usable=True,
        aliases=["water flower", "cave lily", "aquatic bloom"]
    ),
    "antidote": Consumable(
        "antidote", 
        "A blue potion that cures poison and disease.",
        health_restore=5,
        effects={"cure_status": True}, 
        value=7,
        type="drink",
        aliases=["blue potion", "cure", "medicine"]
    ),
    "elixir_of_clarity": Consumable(
        "elixir_of_clarity", 
        "A purple potion that enhances perception and reflexes.",
        health_restore=0,
        effects={"dodge_chance": 0.2, "duration": 120},
        value=15,
        type="drink",
        aliases=["clarity potion", "purple potion", "reflex potion"]
    )
}

def get_herb(herb_name):
    """Get an herb from the predefined herbs"""
    return HERBS.get(herb_name)
