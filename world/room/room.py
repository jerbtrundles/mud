# world/room.py
"""
Room class hierarchy for different types of rooms in the game.
"""

from core.game_object import GameObject

class Room(GameObject):
    """Base class for all rooms in the game"""
    
    def __init__(self, name, description, region=None, **kwargs):
        """
        Initialize a base room
        
        Args:
            name (str): Internal name of the room (snake_case)
            description (str): Human-readable description
            region (Region, optional): The region this room belongs to
            **kwargs: Additional attributes for derived classes
        """
        super().__init__(name, description, **kwargs)
        self.region = region
        self.exits = {}  # {"north": "room_id", "south": "room_id", ...}
        self.items = []  # List of item IDs
        self.visited = False  # Whether player has visited this room
        self.add_tag("room")
        
    def add_exit(self, direction, destination, locked=False, key_item=None):
        """Add an exit to this room"""
        self.exits[direction] = {"destination": destination, "locked": locked, "key_item": key_item}
        
    def get_exit(self, direction):
        """Get exit information for a direction"""
        return self.exits.get(direction)
        
    def get_exit_directions(self):
        """Get all available exit directions"""
        return list(self.exits.keys())
    
    def add_item(self, item_id):
        """Add an item to this room"""
        if item_id not in self.items:
            self.items.append(item_id)
            
    def remove_item(self, item_id):
        """Remove an item from this room"""
        if item_id in self.items:
            self.items.remove(item_id)
            return True
        return False
    
    def get_items(self):
        """Get all items in this room"""
        return self.items.copy()
    
    def mark_visited(self):
        """Mark this room as visited"""
        self.visited = True
        
    def to_dict(self):
        """Serialize room to dictionary"""
        data = super().to_dict()
        data.update({
            "region": self.region.name if self.region else None,
            "exits": self.exits,
            "items": self.items,
            "visited": self.visited
        })
        return data
    
    @classmethod
    def from_dict(cls, data, regions=None):
        """Create a room from dictionary data"""
        region = None
        if regions and data.get("region"):
            region = regions.get(data["region"])
            
        room = cls(
            name=data["name"],
            description=data["description"],
            region=region
        )
        room.exits = data.get("exits", {})
        room.items = data.get("items", [])
        room.visited = data.get("visited", False)
        
        # Restore tags
        for tag in data.get("tags", []):
            room.add_tag(tag)
            
        return room
    
    def describe(self):
        """Return a full description of the room and its contents"""
        desc = self.description
        
        # Add exit information
        if self.exits:
            exit_list = ", ".join(self.get_exit_directions())
            desc += f"\nExits: {exit_list}"
        else:
            desc += "\nThere are no visible exits."
            
        # Add item information if any
        if self.items:
            desc += "\nYou see:"
            for item_id in self.items:
                # In a real implementation, you'd get the display name from an item registry
                item_name = item_id.replace('_', ' ')
                desc += f"\n- {item_name}"
                
        return desc
