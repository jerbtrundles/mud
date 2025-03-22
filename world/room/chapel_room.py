from world.room.room import Room

class ChapelRoom(Room):
    """A room that functions as a chapel for healing and blessings"""
    
    def __init__(self, name, description, cleric_name="Cleric", 
                 blessing_cost=10, healing_cost=15, region=None, **kwargs):
        """Initialize a chapel room"""
        super().__init__(name, description, region, **kwargs)
        self.cleric_name = cleric_name
        self.blessing_cost = blessing_cost
        self.healing_cost = healing_cost
        self.dialogues = []  # List of possible cleric dialogues
        self.add_tag("chapel")
    
    def add_dialogue(self, dialogue):
        """Add a possible cleric dialogue"""
        self.dialogues.append(dialogue)
        
    def get_random_dialogue(self):
        """Get a random cleric dialogue"""
        import random
        if not self.dialogues:
            return f"{self.cleric_name} offers a blessing."
        return random.choice(self.dialogues)
    
    def to_dict(self):
        """Serialize chapel room to dictionary"""
        data = super().to_dict()
        data.update({
            "cleric_name": self.cleric_name,
            "blessing_cost": self.blessing_cost,
            "healing_cost": self.healing_cost,
            "dialogues": self.dialogues
        })
        return data
    
    @classmethod
    def from_dict(cls, data, regions=None):
        """Create a chapel room from dictionary data"""
        room = super().from_dict(data, regions)
        room.cleric_name = data.get("cleric_name", "Cleric")
        room.blessing_cost = data.get("blessing_cost", 10)
        room.healing_cost = data.get("healing_cost", 15)
        room.dialogues = data.get("dialogues", [])
        return room
