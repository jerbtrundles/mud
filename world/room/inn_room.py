from world.room.room import Room

class InnRoom(Room):
    """A room that functions as an inn for resting"""
    
    def __init__(self, name, description, innkeeper_name="Innkeeper", 
                 rest_cost=5, region=None, **kwargs):
        """Initialize an inn room"""
        super().__init__(name, description, region, **kwargs)
        self.innkeeper_name = innkeeper_name
        self.rest_cost = rest_cost
        self.dialogues = []  # List of possible innkeeper dialogues
        self.add_tag("inn")
    
    def add_dialogue(self, dialogue):
        """Add a possible innkeeper dialogue"""
        self.dialogues.append(dialogue)
        
    def get_random_dialogue(self):
        """Get a random innkeeper dialogue"""
        import random
        if not self.dialogues:
            return f"{self.innkeeper_name} welcomes you to the inn."
        return random.choice(self.dialogues)
    
    def to_dict(self):
        """Serialize inn room to dictionary"""
        data = super().to_dict()
        data.update({
            "innkeeper_name": self.innkeeper_name,
            "rest_cost": self.rest_cost,
            "dialogues": self.dialogues
        })
        return data
    
    @classmethod
    def from_dict(cls, data, regions=None):
        """Create an inn room from dictionary data"""
        room = super().from_dict(data, regions)
        room.innkeeper_name = data.get("innkeeper_name", "Innkeeper")
        room.rest_cost = data.get("rest_cost", 5)
        room.dialogues = data.get("dialogues", [])
        return room
