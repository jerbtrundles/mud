from world.room.room import Room

class GardenRoom(Room):
    """A room that functions as a garden for gathering herbs"""
    
    def __init__(self, name, description, gardener_name="Gardener", 
                 regrowth_time=300, region=None, **kwargs):
        """Initialize a garden room"""
        super().__init__(name, description, region, **kwargs)
        self.gardener_name = gardener_name
        self.regrowth_time = regrowth_time
        self.dialogues = []  # List of possible gardener dialogues
        self.last_gather_time = 0  # Last time items were gathered
        self.add_tag("garden")
    
    def add_dialogue(self, dialogue):
        """Add a possible gardener dialogue"""
        self.dialogues.append(dialogue)
        
    def get_random_dialogue(self):
        """Get a random gardener dialogue"""
        import random
        if not self.dialogues:
            return f"{self.gardener_name} nods at you."
        return random.choice(self.dialogues)
    
    def can_gather(self, current_time):
        """Check if enough time has passed for regrowth"""
        return current_time - self.last_gather_time >= self.regrowth_time
    
    def gather(self, current_time):
        """Gather herbs from the garden"""
        if not self.can_gather(current_time):
            return None
            
        import random
        if not self.items:
            return None
            
        # Pick a random herb
        herb_index = random.randint(0, len(self.items) - 1)
        herb = self.items.pop(herb_index)
        
        # Update gather time if garden is empty
        if not self.items:
            self.last_gather_time = current_time
            
        return herb
    
    def to_dict(self):
        """Serialize garden room to dictionary"""
        data = super().to_dict()
        data.update({
            "gardener_name": self.gardener_name,
            "regrowth_time": self.regrowth_time,
            "dialogues": self.dialogues,
            "last_gather_time": self.last_gather_time
        })
        return data
    
    @classmethod
    def from_dict(cls, data, regions=None):
        """Create a garden room from dictionary data"""
        room = super().from_dict(data, regions)
        room.gardener_name = data.get("gardener_name", "Gardener")
        room.regrowth_time = data.get("regrowth_time", 300)
        room.dialogues = data.get("dialogues", [])
        room.last_gather_time = data.get("last_gather_time", 0)
        return room
