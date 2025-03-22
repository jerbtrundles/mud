# status_effects.py
import time
import random

class StatusEffect:
    """Base class for all status effects"""
    def __init__(self, duration=30, strength=1):
        self.name = "generic_effect"
        self.display_name = "Generic Effect"
        self.description = "A generic status effect"
        self.duration = duration  # seconds
        self.strength = strength  # intensity of effect (1 = normal, 2 = strong, etc.)
        self.start_time = time.time()
        self.last_tick_time = time.time()
        self.tick_interval = 10  # seconds between effect triggering
        self.icon = "?"  # Single character for display
        self.message_color = (255, 255, 255)  # Default color for messages
    
    def is_expired(self, current_time=None):
        """Check if the effect has expired"""
        if current_time is None:
            current_time = time.time()
        return current_time >= (self.start_time + self.duration)
    
    def should_tick(self, current_time=None):
        """Check if it's time for the effect to trigger again"""
        if current_time is None:
            current_time = time.time()
        return current_time >= (self.last_tick_time + self.tick_interval)
    
    def apply_tick(self, game_state, current_time=None):
        """Apply the effect's periodic action"""
        if current_time is None:
            current_time = time.time()
        if self.should_tick(current_time):
            self.last_tick_time = current_time
            return self._tick_effect(game_state)
        return False, None
    
    def _tick_effect(self, game_state):
        """To be overridden by specific effects"""
        return False, "No effect"
    
    def apply_initial(self, game_state):
        """Apply initial effects when first applied"""
        return False, "No initial effect"
    
    def apply_removal(self, game_state):
        """Apply effects upon being removed/cured"""
        return False, "Effect has worn off."
    
    def get_time_remaining(self, current_time=None):
        """Get remaining time in seconds"""
        if current_time is None:
            current_time = time.time()
        return max(0, (self.start_time + self.duration) - current_time)
    
    def get_status_text(self):
        """Get text description for status display"""
        seconds_left = self.get_time_remaining()
        return f"{self.display_name} ({int(seconds_left)}s)"

