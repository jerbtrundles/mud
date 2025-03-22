from room import Room

class ShopRoom(Room):
    """A room that functions as a shop"""
    
    def __init__(self, name, description, shopkeeper_name="Shopkeeper", region=None, **kwargs):
        """Initialize a shop room"""
        super().__init__(name, description, region, **kwargs)
        self.shopkeeper_name = shopkeeper_name
        self.inventory = {}  # {"item_id": {"price": 10, "description": "..."}, ...}
        self.dialogues = []  # List of possible shopkeeper dialogues
        self.add_tag("shop")
    
    def add_inventory_item(self, item_id, price, description=None):
        """Add an item to the shop inventory"""
        self.inventory[item_id] = {"price": price, "description": description}
        
    def remove_inventory_item(self, item_id):
        """Remove an item from the shop inventory"""
        if item_id in self.inventory:
            del self.inventory[item_id]
            return True
        return False
    
    def get_price(self, item_id):
        """Get the price of an item"""
        if item_id in self.inventory:
            return self.inventory[item_id]["price"]
        return None
    
    def add_dialogue(self, dialogue):
        """Add a possible shopkeeper dialogue"""
        self.dialogues.append(dialogue)
        
    def get_random_dialogue(self):
        """Get a random shopkeeper dialogue"""
        import random
        if not self.dialogues:
            return f"{self.shopkeeper_name} nods at you."
        return random.choice(self.dialogues)
    
    def to_dict(self):
        """Serialize shop room to dictionary"""
        data = super().to_dict()
        data.update({
            "shopkeeper_name": self.shopkeeper_name,
            "inventory": self.inventory,
            "dialogues": self.dialogues
        })
        return data
    
    @classmethod
    def from_dict(cls, data, regions=None):
        """Create a shop room from dictionary data"""
        room = super().from_dict(data, regions)
        room.shopkeeper_name = data.get("shopkeeper_name", "Shopkeeper")
        room.inventory = data.get("inventory", {})
        room.dialogues = data.get("dialogues", [])
        return room
