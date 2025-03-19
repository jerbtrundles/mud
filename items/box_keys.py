# box_keys.py
from items.treasure import Key

# Define special keys for treasure boxes
BOX_KEYS = {
    "common_box_key": Key(
        "common_box_key",
        "A simple iron key that can open common treasure boxes.",
        unlocks=["common_treasure_box"],
        value=2,
        single_use=True,
        aliases=["iron key", "simple key", "common key"]
    ),
    "uncommon_box_key": Key(
        "uncommon_box_key",
        "A well-crafted bronze key with small engravings. Opens uncommon treasure boxes.",
        unlocks=["uncommon_treasure_box"],
        value=5,
        single_use=True,
        aliases=["bronze key", "engraved key", "uncommon key"]
    ),
    "rare_box_key": Key(
        "rare_box_key",
        "A silver key with an unusual shape. It feels slightly warm to the touch.",
        unlocks=["rare_treasure_box"],
        value=12,
        single_use=True,
        aliases=["silver key", "warm key", "rare key"]
    ),
    "epic_box_key": Key(
        "epic_box_key",
        "A golden key with glowing blue gems embedded in its handle.",
        unlocks=["epic_treasure_box"],
        value=25,
        single_use=True,
        aliases=["golden key", "gem key", "epic key"]
    ),
    "legendary_box_key": Key(
        "legendary_box_key",
        "A mysterious key that seems to shift and change as you look at it. Powerful magic emanates from it.",
        unlocks=["legendary_treasure_box"],
        value=50,
        single_use=True,
        aliases=["magical key", "shifting key", "legendary key"]
    ),
    "master_key": Key(
        "master_key",
        "A masterfully crafted skeleton key that can open any treasure box. Extremely rare.",
        unlocks=["common_treasure_box", "uncommon_treasure_box", "rare_treasure_box", "epic_treasure_box", "legendary_treasure_box"],
        value=100,
        single_use=False,  # This key is reusable!
        aliases=["skeleton key", "master skeleton key", "universal key"]
    )
}

def get_box_key(key_name):
    """Get a box key from the predefined keys"""
    return BOX_KEYS.get(key_name)