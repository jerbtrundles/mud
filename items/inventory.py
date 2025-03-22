# items/inventory.py
"""
Enhanced inventory system with categorization, sorting, and search functionality.
"""

from collections import defaultdict

class Inventory:
    """Class representing an inventory of items with advanced functionality"""
    
    def __init__(self, capacity=None):
        """
        Initialize an inventory
        
        Args:
            capacity (int, optional): Maximum number of items the inventory can hold
        """
        self.items = {}  # Dict of {item_id: quantity}
        self.capacity = capacity  # None means unlimited
        
    def add_item(self, item_id, quantity=1):
        """
        Add an item to the inventory
        
        Args:
            item_id (str): ID of the item to add
            quantity (int): Number of items to add
            
        Returns:
            tuple: (success, message)
        """
        # Check if adding would exceed capacity
        if self.capacity is not None:
            current_count = sum(self.items.values())
            if current_count + quantity > self.capacity:
                return False, f"Not enough space in inventory for {quantity} more items."
        
        # Add the item
        if item_id in self.items:
            self.items[item_id] += quantity
        else:
            self.items[item_id] = quantity
            
        return True, f"Added {quantity}x {item_id} to inventory."
    
    def remove_item(self, item_id, quantity=1):
        """
        Remove an item from the inventory
        
        Args:
            item_id (str): ID of the item to remove
            quantity (int): Number of items to remove
            
        Returns:
            tuple: (success, message)
        """
        if item_id not in self.items:
            return False, f"Item '{item_id}' not found in inventory."
            
        if self.items[item_id] < quantity:
            return False, f"Not enough of item '{item_id}' in inventory."
            
        # Remove the item
        self.items[item_id] -= quantity
        
        # If quantity reaches 0, remove the item completely
        if self.items[item_id] <= 0:
            del self.items[item_id]
            
        return True, f"Removed {quantity}x {item_id} from inventory."
    
    def has_item(self, item_id, quantity=1):
        """
        Check if inventory has the specified item and quantity
        
        Args:
            item_id (str): ID of the item to check
            quantity (int): Required quantity
            
        Returns:
            bool: True if inventory has enough of the item
        """
        return item_id in self.items and self.items[item_id] >= quantity
    
    def get_quantity(self, item_id):
        """
        Get the quantity of a specific item
        
        Args:
            item_id (str): ID of the item to check
            
        Returns:
            int: Quantity of the item, or 0 if not found
        """
        return self.items.get(item_id, 0)
    
    def list_items(self):
        """
        Get a list of all items and their quantities
        
        Returns:
            list: List of (item_id, quantity) tuples
        """
        return list(self.items.items())
    
    def find_items_by_prefix(self, prefix):
        """
        Find items by prefix for partial matching
        
        Args:
            prefix (str): The prefix to search for
            
        Returns:
            list: List of (item_id, quantity) tuples matching the prefix
        """
        return [(item_id, qty) for item_id, qty in self.items.items() 
                if item_id.startswith(prefix)]
    
    def find_item_by_name(self, name, item_registry=None):
        """
        Find an item by its name with fuzzy matching
        
        Args:
            name (str): Name to search for
            item_registry: Optional registry for checking display names/aliases
            
        Returns:
            str: The matched item_id, or None if not found
        """
        # Convert name to lowercase for case-insensitive matching
        search_term = name.lower().replace(' ', '_')
        
        # Direct match on item_id
        if search_term in self.items:
            return search_term
            
        # If no direct match and we have an item registry, use it for better matching
        if item_registry:
            best_match = None
            best_score = float('inf')  # Lower is better
            
            for item_id in self.items:
                item = item_registry.get_item(item_id)
                if not item:
                    continue
                    
                # Check if search term is in item name
                if search_term in item_id:
                    score = len(item_id) - len(search_term)
                    if score < best_score:
                        best_match = item_id
                        best_score = score
                
                # Check if search term is in any aliases
                if hasattr(item, 'aliases'):
                    for alias in item.aliases:
                        alias_lower = alias.lower().replace(' ', '_')
                        if search_term in alias_lower:
                            score = len(alias_lower) - len(search_term)
                            if score < best_score:
                                best_match = item_id
                                best_score = score
            
            return best_match
        
        # No item registry, just use basic string matching
        for item_id in self.items:
            if search_term in item_id:
                return item_id
                
        return None
    
    def categorize_items(self, item_registry=None):
        """
        Categorize items by type
        
        Args:
            item_registry: Registry to look up item types
            
        Returns:
            dict: Dictionary of {category: [(item_id, quantity), ...]}
        """
        categories = defaultdict(list)
        
        for item_id, quantity in self.items.items():
            # Determine category
            category = "misc"  # Default category
            
            if item_registry:
                item = item_registry.get_item(item_id)
                if item and hasattr(item, 'type'):
                    category = item.type
            
            categories[category].append((item_id, quantity))
            
        return dict(categories)
    
    def sort_items(self, key="name", reverse=False):
        """
        Sort items by a key
        
        Args:
            key (str): Sort key ("name", "quantity", "value")
            reverse (bool): Sort in reverse order
            
        Returns:
            list: Sorted list of (item_id, quantity) tuples
        """
        items = list(self.items.items())
        
        if key == "name":
            return sorted(items, key=lambda x: x[0], reverse=reverse)
        elif key == "quantity":
            return sorted(items, key=lambda x: x[1], reverse=reverse)
        
        # Default to name
        return sorted(items, key=lambda x: x[0], reverse=reverse)
    
    def clear(self):
        """Clear all items from inventory"""
        self.items = {}
    
    def is_empty(self):
        """Check if inventory is empty"""
        return len(self.items) == 0
    
    def get_total_items(self):
        """Get total number of items (sum of all quantities)"""
        return sum(self.items.values())
    
    def to_dict(self):
        """Convert inventory to dictionary for serialization"""
        return {
            "items": dict(self.items),
            "capacity": self.capacity
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create inventory from dictionary data"""
        inventory = cls(capacity=data.get("capacity"))
        inventory.items = data.get("items", {})
        return inventory