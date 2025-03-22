from world.room.room import Room

class RepairRoom(Room):
    """A room that functions as a blacksmith for repairing items"""
    
    def __init__(self, name, description, smith_name="Blacksmith", 
                 repair_cost_multiplier=0.3, region=None, **kwargs):
        """Initialize a repair room"""
        super().__init__(name, description, region, **kwargs)
        self.smith_name = smith_name
        self.repair_cost_multiplier = repair_cost_multiplier
        self.dialogues = []  # List of possible smith dialogues
        self.add_tag("repair")
    
    def add_dialogue(self, dialogue):
        """Add a possible smith dialogue"""
        self.dialogues.append(dialogue)
        
    def get_random_dialogue(self):
        """Get a random smith dialogue"""
        import random
        if not self.dialogues:
            return f"{self.smith_name} hammers at the anvil."
        return random.choice(self.dialogues)
    
    def get_repair_cost(self, item_value):
        """Calculate repair cost for an item"""
        return max(1, int(item_value * self.repair_cost_multiplier))
    
    def to_dict(self):
        """Serialize repair room to dictionary"""
        data = super().to_dict()
        data.update({
            "smith_name": self.smith_name,
            "repair_cost_multiplier": self.repair_cost_multiplier,
            "dialogues": self.dialogues
        })
        return data
    
    @classmethod
    def from_dict(cls, data, regions=None):
        """Create a repair room from dictionary data"""
        room = super().from_dict(data, regions)
        room.smith_name = data.get("smith_name", "Blacksmith")
        room.repair_cost_multiplier = data.get("repair_cost_multiplier", 0.3)
        room.dialogues = data.get("dialogues", [])
        return room
