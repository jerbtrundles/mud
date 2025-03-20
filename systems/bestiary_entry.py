# bestiary_entry.py
class BestiaryEntry:
    """Class representing a single enemy entry in the bestiary"""
    def __init__(self, enemy_name):
        self.name = enemy_name
        self.encounters = 0
        self.kills = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        self.discovered = False
        self.last_seen_location = None
        self.weakness = None
        self.resistance = None
    
    def update(self, killed=False, damage_dealt=0, damage_taken=0, location=None):
        """Update the bestiary entry with new information"""
        self.encounters += 1
        if killed:
            self.kills += 1
        self.damage_dealt += damage_dealt
        self.damage_taken += damage_taken
        if location:
            self.last_seen_location = location
        if not self.discovered:
            self.discovered = True
    
    def get_kill_ratio(self):
        """Calculate kill to encounter ratio"""
        if self.encounters == 0:
            return 0
        return self.kills / self.encounters
        
    def get_stats(self):
        """Get stats about this enemy"""
        kill_ratio = self.get_kill_ratio() * 100  # as percentage
        
        stats = {
            "encounters": self.encounters,
            "kills": self.kills,
            "kill_ratio": f"{kill_ratio:.1f}%",
            "damage_dealt": self.damage_dealt,
            "damage_taken": self.damage_taken,
            "avg_damage_per_encounter": self.damage_dealt / max(1, self.encounters),
            "last_seen": self.last_seen_location
        }
        return stats