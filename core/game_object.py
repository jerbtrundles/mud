# core/game_object.py
"""
Base GameObject class that all in-game objects inherit from.
This provides common functionality and structure for all game objects.
"""

class GameObject:
    """Base class for all objects in the game world"""
    
    def __init__(self, name, description, **kwargs):
        """
        Initialize a base game object
        
        Args:
            name (str): Internal name of the object (snake_case)
            description (str): Human-readable description
            **kwargs: Additional attributes for derived classes
        """
        self.name = name
        self.description = description
        self.attributes = kwargs  # Store additional attributes
        self.tags = set()  # Tags for filtering/searching
        
    def add_tag(self, tag):
        """Add a tag to this object"""
        self.tags.add(tag.lower())
        
    def has_tag(self, tag):
        """Check if this object has a specified tag"""
        return tag.lower() in self.tags
        
    def display_name(self):
        """Return a formatted display name"""
        return self.name.replace('_', ' ').title()
    
    def to_dict(self):
        """Convert object to a dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "attributes": self.attributes,
            "tags": list(self.tags)
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an object from a dictionary"""
        obj = cls(
            name=data["name"], 
            description=data["description"], 
            **data.get("attributes", {})
        )
        for tag in data.get("tags", []):
            obj.add_tag(tag)
        return obj
    
    def __str__(self):
        return self.display_name()