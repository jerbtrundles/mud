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


class PoisonEffect(StatusEffect):
    """Poison status effect that deals damage over time"""
    def __init__(self, duration=30, strength=1):
        super().__init__(duration, strength)
        self.name = "poison"
        self.display_name = "Poisoned"
        self.description = "Taking damage over time from poison"
        self.tick_interval = 5  # 5 seconds between damage ticks
        self.icon = "☠"  # Poison icon
        self.message_color = (0, 180, 0)  # Green for poison
    
    def _tick_effect(self, game_state):
        """Apply poison damage"""
        # Calculate damage based on strength
        base_damage = 1  # Base damage per tick
        total_damage = base_damage * self.strength
        
        # Apply damage to player
        damage_taken = game_state.player.take_damage(total_damage)
        
        # Return whether damage was applied and a message
        if damage_taken > 0:
            return True, f"You take {damage_taken} poison damage! ({game_state.player.health}/{game_state.player.max_health} HP)"
        return False, None
    
    def apply_initial(self, game_state):
        """Initial poison application"""
        return True, "You've been poisoned! The venom courses through your veins."
    
    def apply_removal(self, game_state):
        """When poison wears off"""
        return True, "The poison has worn off. You feel better."
