# armor.py
from items.item import Item

ARMOR_SLOTS = {
    "head": "Helmet",
    "chest": "Armor",
    "hands": "Gloves",
    "legs": "Leggings",
    "feet": "Boots",
    "neck": "Amulet",
    "ring": "Ring"
}

class Armor(Item):
    def __init__(self, name, description, defense_bonus, slot, value=15, 
                 durability=None, requirements=None, aliases=None,
                 special_effects=None):
        """
        Armor class for all armor items
        
        Args:
            name (str): Internal name of the armor
            description (str): Human-readable description
            defense_bonus (int): Defense bonus provided by the armor
            slot (str): Which equipment slot this armor belongs to
            value (int): Base value in coins
            durability (int, optional): Durability points, None for indestructible
            requirements (dict, optional): Player requirements to use (e.g., {"level": 2})
            aliases (list): Alternative names for the armor
            special_effects (dict, optional): Special effects this armor provides
        """
        super().__init__(name, description, value, stackable=False, usable=False, aliases=aliases)
        self.defense_bonus = defense_bonus
        self.durability = durability
        self.max_durability = durability
        self.requirements = requirements or {}
        self.special_effects = special_effects or {}
        self.slot = slot
        self.type = "armor"
    
    def get_defense_bonus(self):
        """Return the defense bonus provided by this armor"""
        return self.defense_bonus

    def get_slot_name(self):
        """Return the human-readable slot name"""
        return ARMOR_SLOTS.get(self.slot, "Unknown")

    def meets_requirements(self, player):
        """Check if player meets the requirements to use this armor"""
        for req, value in self.requirements.items():
            if req == "level" and player.level < value:
                return False
        return True
    
    def __str__(self):
        return f"{self.display_name()} (+{self.defense_bonus} DEF, {self.get_slot_name()})"

# Predefined armor

# Helmets
HELMETS = {
    "leather_cap": Armor(
        "leather_cap",
        "A simple leather cap offering minimal protection.",
        defense_bonus=1,
        slot="head",
        value=5,
        aliases=["cap", "leather hat"]
    ),
    "iron_helmet": Armor(
        "iron_helmet",
        "A solid iron helmet that protects your head from blows.",
        defense_bonus=3,
        slot="head",
        value=15,
        requirements={"level": 2},
        aliases=["helmet", "iron cap"]
    ),
    "enchanted_circlet": Armor(
        "enchanted_circlet",
        "A silver circlet with a glowing blue gem that enhances mental focus.",
        defense_bonus=2,
        slot="head",
        value=30,
        requirements={"level": 3},
        special_effects={"magic_resistance": 10},
        aliases=["circlet", "silver circlet", "magical headpiece"]
    ),
}

# Chest Armor (already had some, let's rename the existing ones)
CHEST_ARMOR = {
    "leather_armor": Armor(
        "leather_armor", 
        "Simple leather armor offering basic protection.",
        defense_bonus=3,
        slot="chest",
        value=15,
        aliases=["leather", "light armor"]
    ),
    "chainmail": Armor(
        "chainmail", 
        "A shirt of interlocking metal rings providing good protection.",
        defense_bonus=6,
        slot="chest",
        value=30,
        requirements={"level": 2},
        aliases=["chain", "chain armor", "mail"]
    ),
    "plate_armor": Armor(
        "plate_armor", 
        "Heavy plate armor offering superior protection.",
        defense_bonus=10,
        slot="chest",
        value=45,
        requirements={"level": 3},
        aliases=["plate", "heavy armor", "metal armor"]
    )
}

# Gloves
GLOVES = {
    "leather_gloves": Armor(
        "leather_gloves",
        "Simple leather gloves that provide minimal protection.",
        defense_bonus=1,
        slot="hands",
        value=5,
        aliases=["gloves", "leather mitts"]
    ),
    "chainmail_gauntlets": Armor(
        "chainmail_gauntlets",
        "Gauntlets made of fine chainmail that protect your hands and wrists.",
        defense_bonus=2,
        slot="hands",
        value=12,
        requirements={"level": 2},
        aliases=["gauntlets", "chain gloves"]
    ),
    "plate_gauntlets": Armor(
        "plate_gauntlets",
        "Heavy metal gauntlets that offer excellent protection for your hands.",
        defense_bonus=3,
        slot="hands",
        value=25,
        requirements={"level": 3},
        aliases=["metal gauntlets", "armored gloves"]
    ),
    "thief_gloves": Armor(
        "thief_gloves",
        "Lightweight gloves made of supple leather that improve dexterity.",
        defense_bonus=1,
        slot="hands",
        value=20,
        special_effects={"dexterity": 5},
        aliases=["nimble gloves", "dexterous gloves"]
    )
}

# Leggings
LEGGINGS = {
    "leather_leggings": Armor(
        "leather_leggings",
        "Simple leather pants that provide basic protection.",
        defense_bonus=2,
        slot="legs",
        value=10,
        aliases=["leather pants", "leggings"]
    ),
    "chainmail_leggings": Armor(
        "chainmail_leggings",
        "Leggings crafted from interwoven metal rings.",
        defense_bonus=4,
        slot="legs",
        value=22,
        requirements={"level": 2},
        aliases=["chain leggings", "mail pants"]
    ),
    "plate_greaves": Armor(
        "plate_greaves",
        "Heavy metal plates that protect your legs from serious damage.",
        defense_bonus=6,
        slot="legs",
        value=35,
        requirements={"level": 3},
        aliases=["greaves", "leg plates", "plate leggings"]
    )
}

# Boots
BOOTS = {
    "leather_boots": Armor(
        "leather_boots",
        "Simple leather boots that provide basic foot protection.",
        defense_bonus=1,
        slot="feet",
        value=8,
        aliases=["boots", "leather shoes"]
    ),
    "chain_boots": Armor(
        "chain_boots",
        "Boots reinforced with chainmail for added protection.",
        defense_bonus=2,
        slot="feet",
        value=18,
        requirements={"level": 2},
        aliases=["reinforced boots", "chainmail footwear"]
    ),
    "plate_boots": Armor(
        "plate_boots",
        "Heavy boots made of solid metal plates.",
        defense_bonus=3,
        slot="feet",
        value=28,
        requirements={"level": 3},
        aliases=["metal boots", "armored boots"]
    ),
    "explorer_boots": Armor(
        "explorer_boots",
        "Enchanted boots that make walking easier and reduce fatigue.",
        defense_bonus=2,
        slot="feet",
        value=35,
        special_effects={"movement_speed": 1.2},
        aliases=["hiking boots", "traveler's boots"]
    )
}

# Amulets (these would focus more on special effects than defense)
AMULETS = {
    "basic_amulet": Armor(
        "basic_amulet",
        "A simple amulet with a small protective enchantment.",
        defense_bonus=1,
        slot="neck",
        value=10,
        aliases=["pendant", "necklace"]
    ),
    "healing_amulet": Armor(
        "healing_amulet",
        "A ruby amulet that slowly regenerates health over time.",
        defense_bonus=1,
        slot="neck",
        value=30,
        special_effects={"health_regen": 0.5},  # 0.5 health per minute
        aliases=["ruby amulet", "regeneration pendant"]
    ),
    "protection_amulet": Armor(
        "protection_amulet",
        "A powerful amulet that grants resistance to damage.",
        defense_bonus=2,
        slot="neck",
        value=45,
        requirements={"level": 3},
        special_effects={"damage_reduction": 0.1},  # 10% damage reduction
        aliases=["warding amulet", "protective pendant"]
    )
}

# Rings (these would also focus more on special effects)
RINGS = {
    "simple_ring": Armor(
        "simple_ring",
        "A plain metal ring with a minor enchantment.",
        defense_bonus=0,
        slot="ring",
        value=5,
        aliases=["metal ring", "band"]
    ),
    "strength_ring": Armor(
        "strength_ring",
        "A ring that enhances the wearer's physical strength.",
        defense_bonus=0,
        slot="ring",
        value=25,
        special_effects={"strength": 2},  # +2 to attack power
        aliases=["empowering ring", "might ring"]
    ),
    "mage_ring": Armor(
        "mage_ring",
        "A sapphire ring that enhances magical abilities.",
        defense_bonus=0,
        slot="ring",
        value=35,
        special_effects={"magic_power": 3},
        aliases=["sapphire ring", "arcane ring"]
    ),
    "vampire_ring": Armor(
        "vampire_ring",
        "A dark ring that drains a small amount of health from enemies.",
        defense_bonus=0,
        slot="ring",
        value=50,
        requirements={"level": 4},
        special_effects={"life_steal": 0.05},  # 5% of damage dealt returned as health
        aliases=["blood ring", "draining ring"]
    )
}

ARMORS = {}
ARMORS.update(HELMETS)
ARMORS.update(CHEST_ARMOR)
ARMORS.update(GLOVES)
ARMORS.update(LEGGINGS)
ARMORS.update(BOOTS)
ARMORS.update(AMULETS)
ARMORS.update(RINGS)

def get_armor(armor_name):
    """Get an armor from the predefined armors"""
    return ARMORS.get(armor_name)