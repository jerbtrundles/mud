# region.py
import random
import time
from world.environment import EnvironmentSystem

class Region:
    """
    A region that contains rooms and manages region-specific systems
    """
    def __init__(self, name, display_name, description, region_type="wilderness", difficulty=1):
        self.name = name  # Internal name (snake_case)
        self.display_name = display_name  # Human-readable name
        self.description = description
        self.region_type = region_type
        self.difficulty = difficulty
        self.rooms = {}  # {room_name: room_data}
        
        # Region-specific systems
        self.environment_system = EnvironmentSystem()
        
        # Region state
        self.discovered = False
        self.danger_level = difficulty  # Can fluctuate
        self.enemy_density = self._calculate_base_enemy_density()
        
        # Environment bias for this region
        self.environment_bias = {}
        
        # Time tracking
        self.last_update_time = time.time()
    
    def _calculate_base_enemy_density(self):
        """Calculate the base enemy density for a region based on its properties"""
        base_density = 1.0
        
        if self.region_type == "monster_lair":
            base_density = 1.5
        elif self.region_type == "settlement":
            base_density = 0.2
        elif self.region_type == "dungeon":
            base_density = 1.0
            
        # Adjust based on difficulty
        density = base_density * (1 + (self.difficulty * 0.2))
        
        return density
    
    def add_room(self, room_name, room_data):
        """Add a room to this region"""
        self.rooms[room_name] = room_data
        room_data["region"] = self.name
        return room_data
    
    def get_room(self, room_name):
        """Get a room in this region by name"""
        return self.rooms.get(room_name)
    
    def get_all_room_names(self):
        """Get names of all rooms in this region"""
        return list(self.rooms.keys())
    
    def set_environment_bias(self, weather_type, bias_factor):
        """Set an environment bias for this region"""
        self.environment_bias[weather_type] = bias_factor
    
    def get_environment_bias(self):
        """Get the environment bias dictionary for this region"""
        return self.environment_bias
    
    def update(self, game_state):
        """Update region state"""
        current_time = time.time()
        
        # Only update periodically
        if current_time - self.last_update_time < 60:  # Update every minute
            return
            
        # Random fluctuations in danger level
        if random.random() < 0.05:  # 5% chance
            base_difficulty = self.difficulty
            
            # Decide whether to increase or decrease
            if self.danger_level > base_difficulty and random.random() < 0.7:
                # More likely to return to base level if currently higher
                self.danger_level = max(base_difficulty, self.danger_level - 0.5)
            elif self.danger_level < base_difficulty and random.random() < 0.7:
                # More likely to return to base level if currently lower
                self.danger_level = min(base_difficulty, self.danger_level + 0.5)
            elif random.random() < 0.5:
                # Otherwise random change
                change = 0.5 if random.random() < 0.5 else -0.5
                self.danger_level = max(0, self.danger_level + change)
        
        # Update environment system
        if random.random() < 0.2:  # 20% chance to update environment
            self.environment_system.update(game_state)
        
        self.last_update_time = current_time
    
    def discover(self):
        """Mark this region as discovered"""
        if not self.discovered:
            self.discovered = True
            return True
        return False
    
    def get_summary(self):
        """Get a text summary of this region"""
        summary = []
        summary.append(f"Region: {self.display_name}")
        summary.append(f"Type: {self.region_type.replace('_', ' ').title()}")
        summary.append(f"Description: {self.description}")
        
        # Difficulty rating as stars
        difficulty_stars = "★" * int(self.difficulty) if self.difficulty > 0 else "None"
        summary.append(f"Difficulty: {difficulty_stars}")
        
        # Danger level might be different from base difficulty
        if self.danger_level > self.difficulty + 0.2:
            summary.append(f"Current Danger: Elevated")
        elif self.danger_level < self.difficulty - 0.2:
            summary.append(f"Current Danger: Reduced")
        else:
            summary.append(f"Current Danger: Normal")
        
        return summary