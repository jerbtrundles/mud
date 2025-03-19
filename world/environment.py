# environment.py
import random
import time

class EnvironmentSystem:
    def __init__(self):
        # Weather types and their effects
        self.weather_types = {
            "clear": {
                "description": "The air is clear and still.",
                "messages": [
                    "Rays of light filter through cracks in the ceiling.",
                    "The air is surprisingly fresh here.",
                    "It's quiet and peaceful."
                ],
                "effects": {}  # No special effects
            },
            "misty": {
                "description": "A thick mist hangs in the air, limiting visibility.",
                "messages": [
                    "Wisps of fog curl around your ankles.",
                    "The mist makes it difficult to see far ahead.",
                    "Ghostly shapes seem to form and dissipate in the fog."
                ],
                "effects": {"enemy_accuracy": -2}  # Enemies have harder time hitting player
            },
            "humid": {
                "description": "The air is damp and humid, making movement sluggish.",
                "messages": [
                    "Droplets of water collect on the walls.",
                    "Your clothes cling uncomfortably to your skin.",
                    "The humid air feels heavy in your lungs."
                ],
                "effects": {"player_attack": -1}  # Player attacks less effectively
            },
            "stormy": {
                "description": "Distant rumblings and occasional tremors shake the cave.",
                "messages": [
                    "A tremor causes small rocks to fall from the ceiling.",
                    "The ground beneath your feet vibrates slightly.",
                    "A crash of thunder reverberates through the cavern."
                ],
                "effects": {"enemy_spawn_rate": 1.5}  # More enemies spawn
            },
            "magical": {
                "description": "The air shimmers with magical energy.",
                "messages": [
                    "Tiny motes of light dance in the air around you.",
                    "You feel a tingling sensation on your skin.",
                    "Your wounds seem to heal slightly faster here."
                ],
                "effects": {"healing_bonus": 1.2}  # Healing items more effective
            }
        }
        
        # Environment states for different room types - just some sensible defaults
        self.environment_states = {
            "entrance": ["clear", "misty", "stormy"],
            "cavern": ["clear", "misty", "humid", "stormy", "magical"],
            "passage": ["clear", "misty", "humid"],
            "lake": ["misty", "humid", "magical"],
            "treasure": ["clear", "magical"],
            "den": ["humid", "stormy"],
            "grotto": ["misty", "magical"],
            "shop": ["clear"]
        }
        
        # Default environment for rooms not specifically defined
        self.default_environments = ["clear", "misty"]
        
        # Track current weather in rooms
        self.current_weather = {}
        
        # Time tracking
        self.last_weather_change = time.time()
        self.weather_duration = 300  # 5 minutes before weather can change
    
    def _get_possible_weathers_for_room(self, room_name):
        """Get possible weather types for a room based on its name"""
        # Try to match room name to a known type
        for room_type, weather_list in self.environment_states.items():
            if room_type in room_name:
                return weather_list
        return self.default_environments
    
    def set_weather(self, room_name, weather_type):
        """Manually set weather for a room"""
        if weather_type in self.weather_types:
            self.current_weather[room_name] = weather_type
            return True
        return False
    
    def get_weather(self, room_name):
        """Get current weather for a room"""
        return self.current_weather.get(room_name, "clear")
    
    def set_random_weather(self, room_name, weather_bias=None):
        """Set random weather for a room with optional bias"""
        possible_weathers = self._get_possible_weathers_for_room(room_name)
        
        # Apply bias if provided
        if weather_bias:
            # Create a weighted list based on bias
            weighted_weathers = []
            for weather in possible_weathers:
                weight = weather_bias.get(weather, 1.0)
                # Convert to integer frequency
                for _ in range(int(weight * 10)):
                    weighted_weathers.append(weather)
            
            if weighted_weathers:
                self.current_weather[room_name] = random.choice(weighted_weathers)
                return self.current_weather[room_name]
        
        # No bias or empty weighted list, use simple random choice
        self.current_weather[room_name] = random.choice(possible_weathers)
        return self.current_weather[room_name]
    
    def initialize_weather(self, region):
        """Initialize weather for all rooms in a region"""
        weather_bias = region.get_environment_bias()
        for room_name in region.get_all_room_names():
            self.set_random_weather(room_name, weather_bias)
    
    def update(self, game_state):
        """Update weather for the current room"""
        current_time = time.time()
        current_room = game_state.current_room
        
        # Check if enough time has passed since last weather change
        if current_time - self.last_weather_change > self.weather_duration:
            # 25% chance to change weather
            if random.random() < 0.25:
                # Get the region for bias information
                region = game_state.world.get_region_for_room(current_room)
                weather_bias = region.get_environment_bias() if region else None
                
                old_weather = self.get_weather(current_room)
                self.set_random_weather(current_room, weather_bias)
                new_weather = self.get_weather(current_room)
                
                # Only notify if weather actually changed
                if old_weather != new_weather:
                    self._describe_weather_change(game_state, old_weather, new_weather)
                    
            self.last_weather_change = current_time
    
    def _describe_weather_change(self, game_state, old_weather, new_weather):
        """Describe the change in weather to the player"""
        new_weather_data = self.weather_types.get(new_weather, self.weather_types["clear"])
        game_state.add_to_history("\nThe environment changes...", (100, 200, 255))
        game_state.add_to_history(new_weather_data["description"], (100, 200, 255))
    
    def get_weather_description(self, room_name):
        """Get a description of the current weather in a room"""
        weather = self.get_weather(room_name)
        return self.weather_types[weather]["description"]
    
    def get_effects(self, room_name):
        """Get current weather effects for a room"""
        weather = self.get_weather(room_name)
        return self.weather_types[weather]["effects"]
    
    def get_random_ambient_message(self, game_state):
        """Get a random ambient message based on current weather"""
        room_name = game_state.current_room
        weather = self.get_weather(room_name)
        
        if random.random() < 0.001:
            messages = self.weather_types[weather]["messages"]
            return random.choice(messages)
        
        return None