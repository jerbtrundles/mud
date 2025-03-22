from world.room.room import Room

class NoticeBoardRoom(Room):
    """A room with a notice board for quests and announcements"""
    
    def __init__(self, name, description, region=None, **kwargs):
        """Initialize a notice board room"""
        super().__init__(name, description, region, **kwargs)
        self.notices = []  # List of notices
        self.add_tag("notice_board")
    
    def add_notice(self, notice):
        """Add a notice to the board"""
        self.notices.append(notice)
        
    def remove_notice(self, index):
        """Remove a notice from the board"""
        if 0 <= index < len(self.notices):
            del self.notices[index]
            return True
        return False
    
    def get_notices(self):
        """Get all notices on the board"""
        return self.notices.copy()
    
    def to_dict(self):
        """Serialize notice board room to dictionary"""
        data = super().to_dict()
        data.update({
            "notices": self.notices
        })
        return data
    
    @classmethod
    def from_dict(cls, data, regions=None):
        """Create a notice board room from dictionary data"""
        room = super().from_dict(data, regions)
        room.notices = data.get("notices", [])
        return room