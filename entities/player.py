# player.py
import time
from items.item_factory import ItemFactory

class Player:
    def __init__(self):
        self.name = "Adventurer"
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.defense = 5
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 20
        
        # Equipment slots
        self.equipment = {
            "head": None,
            "chest": None,
            "hands": None,
            "legs": None,
            "feet": None,
            "neck": None,
            "ring": None,
            "weapon": None  # Move weapon into equipment dict for consistency
        }

        # Temporary stat buffs
        self.temp_attack_bonus = 0
        self.temp_defense_bonus = 0
        self.temp_buff_end_time = 0
        
        # Inventory storage (use a dict for stacking)
        self.inventory = {}  # Format: {item_name: quantity}
    
    def take_damage(self, amount):
        """Take damage with defense reduction"""
        actual_damage = max(1, amount - self.defense_power())
        self.health = max(0, self.health - actual_damage)
        return actual_damage
    
    def heal(self, amount):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
        return amount
    
    def attack_power(self):
        """Calculate total attack power including equipment and buffs"""
        # Check temporary buffs
        self._update_temp_buffs()
        
        # Base attack + weapon bonus + temp buffs
        weapon_bonus = 0
        if self.equipment["weapon"]:
            weapon = ItemFactory.get_item(self.equipment["weapon"])
            if weapon:
                weapon_bonus = weapon.get_attack_bonus()
                
        return self.attack + weapon_bonus + self.temp_attack_bonus
    
    def defense_power(self):
        """Calculate total defense including equipment and buffs"""
        # Check temporary buffs
        self._update_temp_buffs()
        
        # Base defense + armor bonus + temp buffs
        armor_bonus = 0

        for slot, item_name in self.equipment.items():
            if slot != "weapon" and item_name:  # Skip weapon slot
                item = ItemFactory.get_item(item_name)
                if item and hasattr(item, "get_defense_bonus"):
                    armor_bonus += item.get_defense_bonus()
                    
        return self.defense + armor_bonus + self.temp_defense_bonus
    
    def _update_temp_buffs(self):
        """Update temporary buffs (check if they've expired)"""
        current_time = time.time()
        if current_time > self.temp_buff_end_time:
            self.temp_attack_bonus = 0
            self.temp_defense_bonus = 0
    
    def gain_experience(self, amount):
        """Add experience and level up if necessary"""
        self.experience += amount
        if self.experience >= self.exp_to_next_level:
            self.level_up()
            return True
        return False
    
    def level_up(self):
        """Increase player's level and stats"""
        self.level += 1
        self.attack += 2
        self.defense += 1
        self.max_health += 10
        self.health = self.max_health
        self.experience -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        return self.level
    
    def equip_item(self, item_name):
        """Equip an item to the appropriate slot"""
        item = ItemFactory.get_item(item_name)
        
        if not item:
            return False, "Item not found."
            
        if not item.meets_requirements(self):
            return False, f"You don't meet the requirements to equip the {item.display_name()}."
        
        if item.type == "weapon":
            old_item = self.equipment["weapon"]
            self.equipment["weapon"] = item_name
            return True, old_item
            
        elif item.type == "armor":
            if not hasattr(item, "slot"):
                return False, f"The {item.display_name()} cannot be equipped."
                
            slot = item.slot
            if slot not in self.equipment:
                return False, f"Invalid equipment slot: {slot}"
                
            old_item = self.equipment[slot]
            self.equipment[slot] = item_name
            return True, old_item
            
        return False, f"You can't equip the {item.display_name()}."

    def unequip_item(self, slot):
        """Remove an item from an equipment slot"""
        if slot not in self.equipment:
            return False, f"Invalid equipment slot: {slot}"
            
        old_item = self.equipment[slot]
        if not old_item:
            return False, f"Nothing equipped in {slot} slot."
            
        self.equipment[slot] = None
        return True, old_item
    
    # Add a method to get equipped item in a slot
    def get_equipped_item(self, slot):
        """Get the item equipped in a specific slot"""
        if slot not in self.equipment:
            return None
            
        item_name = self.equipment[slot]
        if not item_name:
            return None
            
        return ItemFactory.get_item(item_name)

    def get_equipment_list(self):
        """Get a formatted list of all equipped items"""
        equipped_items = []
        
        for slot, item_name in self.equipment.items():
            if item_name:
                item = ItemFactory.get_item(item_name)
                if item:
                    slot_name = item.get_slot_name() if hasattr(item, "get_slot_name") else slot.capitalize()
                    
                    if slot == "weapon":
                        equipped_items.append(f"{slot_name}: {item.display_name()} (+{item.attack_bonus} ATK)")
                    elif hasattr(item, "defense_bonus"):
                        equipped_items.append(f"{slot_name}: {item.display_name()} (+{item.defense_bonus} DEF)")
                    else:
                        equipped_items.append(f"{slot_name}: {item.display_name()}")
                        
        return equipped_items
    
    def add_to_inventory(self, item_name, quantity=1):
        """Add an item to inventory"""
        item = ItemFactory.get_item(item_name)
        if not item:
            return False
            
        if item_name in self.inventory:
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity
        return True
    
    def remove_from_inventory(self, item_name, quantity=1):
        """Remove an item from inventory"""
        if item_name in self.inventory:
            if self.inventory[item_name] <= quantity:
                # Remove the item completely
                del self.inventory[item_name]
            else:
                # Reduce the quantity
                self.inventory[item_name] -= quantity
            return True
        return False
    
    def has_item(self, item_name, quantity=1):
        """Check if player has the specified item quantity"""
        return item_name in self.inventory and self.inventory[item_name] >= quantity
    
    def get_item_quantity(self, item_name):
        """Get quantity of a specific item"""
        return self.inventory.get(item_name, 0)
    
    def get_inventory_list(self):
        """Get a list of items in inventory with quantities"""
        inventory_list = []
        for item_name, quantity in self.inventory.items():
            item = ItemFactory.get_item(item_name)
            if item:
                if quantity > 1:
                    inventory_list.append(f"{item.display_name()} (x{quantity})")
                else:
                    inventory_list.append(item.display_name())
        return inventory_list
    
    def use_item(self, item_name, game_state):
        """Use an item from inventory"""
        if not self.has_item(item_name):
            return False, f"You don't have a {item_name.replace('_', ' ')}."
            
        item = ItemFactory.get_item(item_name)
        if not item:
            return False, f"Unknown item: {item_name.replace('_', ' ')}."
            
        if not item.can_use(game_state):
            return False, f"You can't use the {item.display_name()} here."
            
        # Use the item
        success, message = item.use(game_state)
        
        # If successfully used a consumable, remove it from inventory
        if success and (item.type == "consumable" or 
                       (item.type == "key" and hasattr(item, "single_use") and item.single_use)):
            self.remove_from_inventory(item_name)
            
        return success, message
    
    def find_item(self, search_string):
        """
        Find an item in the player's inventory by name or alias
        with partial string matching.
        
        Args:
            search_string (str): The name to search for
            
        Returns:
            str: The internal item name, or None if not found
        """
        search_string = search_string.lower()
        
        # First check for exact match
        for item_name in self.inventory:
            if item_name.replace('_', ' ') == search_string:
                return item_name
                
        # Check for partial match
        best_match = None
        best_score = float('inf')  # Lower is better
        
        for item_name in self.inventory:
            item = ItemFactory.get_item(item_name)
            if not item:
                continue
                
            # Check if search string is in name
            if search_string in item_name.replace('_', ' '):
                score = len(item_name) - len(search_string)
                if score < best_score:
                    best_match = item_name
                    best_score = score
            
            # Check if search string is in aliases
            for alias in item.aliases:
                if search_string in alias.lower():
                    score = len(alias) - len(search_string)
                    if score < best_score:
                        best_match = item_name
                        best_score = score
        
        return best_match

    def get_item(self, item_name):
        """
        Get an item instance from the player's inventory
        
        Args:
            item_name (str): The internal name of the item
            
        Returns:
            Item: The item instance, or None if not in inventory
        """
        if item_name in self.inventory:
            return ItemFactory.get_item(item_name)
        return None