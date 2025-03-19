# armor.py
from items.item import Item

class Armor(Item):
    def __init__(self, name, description, defense_bonus, value=15, 
                 durability=None, requirements=None, aliases=None):
        """
        Armor class for all armor items
        
        Args:
            name (str): Internal name of the armor
            description (str): Human-readable description
            defense_bonus (int): Defense bonus provided by the armor
            value (int): Base value in coins
            durability (int, optional): Durability points, None for indestructible
            requirements (dict, optional): Player requirements to use (e.g., {"level": 2})
            aliases (list): Alternative names for the armor
        """
        super().__init__(name, description, value, stackable=False, usable=False, aliases=aliases)
        self.defense_bonus = defense_bonus
        self.durability = durability
        self.max_durability = durability
        self.requirements = requirements or {}
        self.type = "armor"
    
    def get_defense_bonus(self):
        """Return the defense bonus provided by this armor"""
        return self.defense_bonus
    
    def meets_requirements(self, player):
        """Check if player meets the requirements to use this armor"""
        for req, value in self.requirements.items():
            if req == "level" and player.level < value:
                return False
        return True
    
    def __str__(self):
        return f"{self.display_name()} (+{self.defense_bonus} DEF)"

# Predefined armor
ARMORS = {
    "leather_armor": Armor(
        "leather_armor", 
        "Simple leather armor offering basic protection.",
        defense_bonus=3,
        value=15,
        aliases=["leather", "light armor"]
    ),
    "chainmail": Armor(
        "chainmail", 
        "A shirt of interlocking metal rings providing good protection.",
        defense_bonus=6,
        value=30,
        requirements={"level": 2},
        aliases=["chain", "chain armor", "mail"]
    ),
    "plate_armor": Armor(
        "plate_armor", 
        "Heavy plate armor offering superior protection.",
        defense_bonus=10,
        value=45,
        requirements={"level": 3},
        aliases=["plate", "heavy armor", "metal armor"]
    )
}

def get_armor(armor_name):
    """Get an armor from the predefined armors"""
    return ARMORS.get(armor_name)