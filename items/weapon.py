# weapon.py
from items.item import Item

class Weapon(Item):
    def __init__(self, name, description, attack_bonus, value=10, 
                 durability=None, requirements=None, aliases=None):
        """
        Weapon class for all weapon items
        
        Args:
            name (str): Internal name of the weapon
            description (str): Human-readable description
            attack_bonus (int): Attack bonus provided by the weapon
            value (int): Base value in coins
            durability (int, optional): Durability points, None for indestructible
            requirements (dict, optional): Player requirements to use (e.g., {"level": 3})
            aliases (list): Alternative names for the weapon
        """
        super().__init__(name, description, value, stackable=False, usable=False, aliases=aliases)
        self.attack_bonus = attack_bonus
        self.durability = durability
        self.max_durability = durability
        self.requirements = requirements or {}
        self.type = "weapon"
    
    def get_attack_bonus(self):
        """Return the attack bonus provided by this weapon"""
        return self.attack_bonus
    
    def meets_requirements(self, player):
        """Check if player meets the requirements to use this weapon"""
        for req, value in self.requirements.items():
            if req == "level" and player.level < value:
                return False
        return True
    
    def __str__(self):
        return f"{self.display_name()} (+{self.attack_bonus} ATK)"


# Predefined weapons
WEAPONS = {
    "rusty_sword": Weapon(
        "rusty_sword", 
        "An old, rusty sword. It's seen better days but still cuts.",
        attack_bonus=5,
        value=7,
        aliases=["rusty", "old sword"]
    ),
    "steel_sword": Weapon(
        "steel_sword", 
        "A well-crafted steel sword, sharp and reliable.",
        attack_bonus=10,
        value=25,
        requirements={"level": 2},
        aliases=["steel", "good sword"]
    ),
    "ancient_blade": Weapon(
        "ancient_blade", 
        "A mysterious blade of unknown origin. It seems to hum with power.",
        attack_bonus=15,
        value=50,
        requirements={"level": 3},
        aliases=["ancient", "mysterious blade", "powerful sword"]
    )
}

def get_weapon(weapon_name):
    """Get a weapon from the predefined weapons"""
    return WEAPONS.get(weapon_name)