# entities/player.py
"""
Player entity class with inventory and equipment management.
"""

import time
from entities.entity import Entity
from items.inventory import Inventory

class Player(Entity):
    """Player character entity with specialized functionality"""
    
    def __init__(self, name="Adventurer", description="A brave adventurer seeking fortune and glory.", 
                 health=100, attack=10, defense=5, level=1, **kwargs):
        """
        Initialize player character
        
        Args:
            name (str): Player name
            description (str): Player description
            health (int): Starting/maximum health
            attack (int): Base attack power
            defense (int): Base defense
            level (int): Starting level
            **kwargs: Additional attributes
        """
        super().__init__(name, description, health, attack, defense, level, **kwargs)
        
        # Player-specific attributes
        self.inventory = Inventory()
        self.equipment = {
            "head": None,
            "chest": None,
            "hands": None,
            "legs": None,
            "feet": None,
            "neck": None,
            "ring": None,
            "weapon": None
        }
        self.experience = 0
        self.exp_to_next_level = self._calculate_exp_for_level(level + 1)
        
        # Temporary bonuses
        self.temp_attack_bonus = 0
        self.temp_defense_bonus = 0
        self.temp_buff_end_time = 0
        
        # Skills and abilities
        self.learned_skills = {}  # {skill_name: skill_obj}
        
        # Add player tag
        self.add_tag("player")
    
    def _calculate_exp_for_level(self, target_level):
        """
        Calculate experience needed for a specific level
        
        Args:
            target_level (int): The level to calculate for
            
        Returns:
            int: Experience points needed
        """
        # Simple formula: 20 * level^1.5
        return int(20 * (target_level ** 1.5))
    
    def gain_experience(self, amount):
        """
        Add experience points and level up if enough
        
        Args:
            amount (int): Amount of experience to add
            
        Returns:
            bool: True if leveled up
        """
        self.experience += amount
        
        # Check for level up
        if self.experience >= self.exp_to_next_level:
            return self.level_up()
            
        return False
    
    def level_up(self):
        """
        Increase player's level and stats
        
        Returns:
            bool: True if leveled up
        """
        self.level += 1
        
        # Improve stats
        old_max_health = self.max_health
        self.max_health += 10
        self.health = self.max_health  # Fully heal on level up
        
        self.attack += 2
        self.defense += 1
        
        # Set new experience threshold
        self.exp_to_next_level = self._calculate_exp_for_level(self.level + 1)
        
        return True
    
    def get_attack(self):
        """Calculate total attack power including equipment and bonuses"""
        base_attack = super().get_attack()
        
        # Add weapon bonus
        weapon_bonus = 0
        if self.equipment["weapon"]:
            from items.item_factory import ItemFactory
            weapon = ItemFactory.get_item(self.equipment["weapon"])
            if weapon:
                weapon_bonus = weapon.get_attack_bonus()
        
        # Add temporary bonuses
        self._update_temp_buffs()
        
        return base_attack + weapon_bonus + self.temp_attack_bonus
    
    def attack_power(self):
        """Legacy method for backward compatibility"""
        return self.get_attack()
    
    def get_defense(self):
        """Calculate total defense including equipment and bonuses"""
        base_defense = super().get_defense()
        
        # Add armor bonuses from all equipment slots
        armor_bonus = 0
        for slot, item_name in self.equipment.items():
            if slot != "weapon" and item_name:
                from items.item_factory import ItemFactory
                item = ItemFactory.get_item(item_name)
                if item and hasattr(item, "get_defense_bonus"):
                    armor_bonus += item.get_defense_bonus()
        
        # Add temporary bonuses
        self._update_temp_buffs()
        
        return base_defense + armor_bonus + self.temp_defense_bonus
    
    def defense_power(self):
        """Legacy method for backward compatibility"""
        return self.get_defense()
    
    def _update_temp_buffs(self):
        """Update temporary buffs (check if expired)"""
        import time
        current_time = time.time()
        
        if current_time > self.temp_buff_end_time:
            self.temp_attack_bonus = 0
            self.temp_defense_bonus = 0
    
    def equip_item(self, item_id):
        """
        Equip an item to the appropriate slot
        
        Args:
            item_id (str): ID of the item to equip
            
        Returns:
            tuple: (success, old_item_id or message)
        """
        # Get item from inventory
        if not self.inventory.has_item(item_id):
            return False, f"You don't have {item_id} in your inventory."
        
        # Get item details to determine slot
        from items.item_factory import ItemFactory
        item = ItemFactory.get_item(item_id)
        
        if not item:
            return False, f"Item {item_id} not found in item registry."
        
        # Check requirements
        if hasattr(item, 'meets_requirements') and not item.meets_requirements(self):
            return False, f"You don't meet the requirements to equip {item.display_name()}."
        
        # Determine equipment slot
        slot = None
        
        if item.type == "weapon":
            slot = "weapon"
        elif item.type == "armor" and hasattr(item, "slot"):
            slot = item.slot
            
        if not slot or slot not in self.equipment:
            return False, f"Cannot determine equipment slot for {item.display_name()}."
        
        # Remember old item
        old_item = self.equipment[slot]
        
        # Equip new item
        self.equipment[slot] = item_id
        
        # Remove from inventory
        self.inventory.remove_item(item_id)
        
        return True, old_item
    
    def unequip_item(self, slot):
        """
        Remove an item from an equipment slot
        
        Args:
            slot (str): The slot to unequip from
            
        Returns:
            tuple: (success, item_id or message)
        """
        if slot not in self.equipment:
            return False, f"Invalid equipment slot: {slot}"
            
        item_id = self.equipment[slot]
        if not item_id:
            return False, f"Nothing equipped in {slot} slot."
            
        # Unequip the item
        self.equipment[slot] = None
        
        return True, item_id
    
    def get_equipped_item(self, slot):
        """
        Get the item equipped in a specific slot
        
        Args:
            slot (str): The slot to check
            
        Returns:
            str: Item ID or None
        """
        if slot not in self.equipment:
            return None
            
        return self.equipment[slot]
    
    def get_equipment_list(self):
        """
        Get a formatted list of all equipped items
        
        Returns:
            list: Formatted equipment strings
        """
        equipped_items = []
        
        for slot, item_id in self.equipment.items():
            if not item_id:
                continue
                
            from items.item_factory import ItemFactory
            item = ItemFactory.get_item(item_id)
            if not item:
                continue
                
            slot_name = item.get_slot_name() if hasattr(item, "get_slot_name") else slot.capitalize()
            
            if slot == "weapon":
                equipped_items.append(f"{slot_name}: {item.display_name()} (+{item.attack_bonus} ATK)")
            elif hasattr(item, "defense_bonus"):
                equipped_items.append(f"{slot_name}: {item.display_name()} (+{item.defense_bonus} DEF)")
            else:
                equipped_items.append(f"{slot_name}: {item.display_name()}")
                
        return equipped_items
    
    def add_to_inventory(self, item_id, quantity=1):
        """Add an item to inventory - for backward compatibility"""
        return self.inventory.add_item(item_id, quantity)[0]
    
    def remove_from_inventory(self, item_id, quantity=1):
        """Remove an item from inventory - for backward compatibility"""
        return self.inventory.remove_item(item_id, quantity)[0]
    
    def has_item(self, item_id, quantity=1):
        """Check if player has an item - for backward compatibility"""
        return self.inventory.has_item(item_id, quantity)
    
    def get_item_quantity(self, item_id):
        """Get quantity of an item - for backward compatibility"""
        return self.inventory.get_quantity(item_id)
    
    def find_item(self, search_text):
        """
        Find an item by name or alias - for backward compatibility
        
        Args:
            search_text (str): Text to search for
            
        Returns:
            str: Item ID or None
        """
        from items.item_factory import ItemFactory
        return self.inventory.find_item_by_name(search_text, ItemFactory)
    
    def get_item(self, item_id):
        """
        Get an item instance from inventory - for backward compatibility
        
        Args:
            item_id (str): ID of the item
            
        Returns:
            Item: Item instance or None
        """
        if not self.inventory.has_item(item_id):
            return None
            
        from items.item_factory import ItemFactory
        return ItemFactory.get_item(item_id)
    
    def get_inventory_list(self):
        """Get a list of inventory items - for backward compatibility"""
        items = []
        
        from items.item_factory import ItemFactory
        for item_id, quantity in self.inventory.list_items():
            item = ItemFactory.get_item(item_id)
            if item:
                if quantity > 1:
                    items.append(f"{item.display_name()} (x{quantity})")
                else:
                    items.append(item.display_name())
            else:
                # Fallback for unknown items
                if quantity > 1:
                    items.append(f"{item_id.replace('_', ' ')} (x{quantity})")
                else:
                    items.append(item_id.replace('_', ' '))
                    
        return items
    
    def learn_skill(self, skill):
        """
        Learn a new skill
        
        Args:
            skill: Skill object to learn
            
        Returns:
            bool: True if learned
        """
        if skill.name in self.learned_skills:
            return False
            
        if self.level < skill.level_requirement:
            return False
            
        self.learned_skills[skill.name] = skill
        return True
    
    def has_skill(self, skill_name):
        """Check if player has learned a skill"""
        return skill_name in self.learned_skills
    
    def use_skill(self, skill_name, target=None, current_time=None):
        """
        Use a learned skill
        
        Args:
            skill_name (str): Name of skill to use
            target: Optional target for the skill
            current_time: Current game time for cooldown check
            
        Returns:
            tuple: (success, message)
        """
        if skill_name not in self.learned_skills:
            return False, f"You haven't learned {skill_name}."
            
        skill = self.learned_skills[skill_name]
        
        # Check cooldown
        can_use, message = skill.can_use(self, current_time or time.time())
        if not can_use:
            return False, message
            
        # Use the skill
        return True, skill.use(self, target)
    
    def _on_death(self):
        """Handle player death"""
        super()._on_death()
        # Additional player death handling
    
    def to_dict(self):
        """Convert player to dictionary for serialization"""
        data = super().to_dict()
        
        # Add player-specific data
        data.update({
            "inventory": self.inventory.to_dict(),
            "equipment": self.equipment,
            "exp_to_next_level": self.exp_to_next_level,
            "temp_attack_bonus": self.temp_attack_bonus,
            "temp_defense_bonus": self.temp_defense_bonus,
            "temp_buff_end_time": self.temp_buff_end_time,
        })
        
        # Add skills if any
        if self.learned_skills:
            data["learned_skills"] = {}
            for skill_name, skill in self.learned_skills.items():
                if hasattr(skill, 'to_dict'):
                    data["learned_skills"][skill_name] = skill.to_dict()
                else:
                    data["learned_skills"][skill_name] = {"name": skill_name}
        
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create a player from dictionary data"""
        # Create base player
        player = super().from_dict(data)
        
        # Set player-specific properties
        if "inventory" in data:
            from items.inventory import Inventory
            player.inventory = Inventory.from_dict(data["inventory"])
            
        if "equipment" in data:
            player.equipment = data["equipment"]
            
        if "exp_to_next_level" in data:
            player.exp_to_next_level = data["exp_to_next_level"]
        else:
            player.exp_to_next_level = player._calculate_exp_for_level(player.level + 1)
            
        player.temp_attack_bonus = data.get("temp_attack_bonus", 0)
        player.temp_defense_bonus = data.get("temp_defense_bonus", 0)
        player.temp_buff_end_time = data.get("temp_buff_end_time", 0)
        
        # Restore skills (requires Skill module)
        if "learned_skills" in data:
            # This would require the skill system to be imported and initialized
            pass
        
        return player