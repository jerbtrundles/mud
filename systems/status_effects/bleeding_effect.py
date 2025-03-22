import time
from status_effects import StatusEffect

class BleedingEffect(StatusEffect):
    """Bleeding status effect that deals damage over time"""
    def __init__(self, duration=20, strength=1):
        super().__init__(duration, strength)
        self.name = "bleeding"
        self.display_name = "Bleeding"
        self.description = "Taking damage over time from bleeding wounds"
        self.tick_interval = 4  # 4 seconds between damage ticks
        self.icon = "💧"  # Blood drop icon
        self.message_color = (200, 0, 0)  # Deep red for bleeding
        self.verbose = False  # Set to False to reduce message noise
        self.last_health_message = 0  # Track when we last showed a health message
        self.health_message_interval = 12  # Only show health message every 12 seconds
    
    def _tick_effect(self, game_state):
        """Apply bleeding damage"""
        # Calculate damage based on strength
        base_damage = 1  # Base damage per tick
        total_damage = base_damage * self.strength
        
        # Apply damage to player
        damage_taken = game_state.player.take_damage(total_damage)
        current_time = time.time()
        
        # Return whether damage was applied and a message
        if damage_taken > 0:
            # Only show health message periodically to reduce noise
            if self.verbose or (current_time - self.last_health_message >= self.health_message_interval):
                self.last_health_message = current_time
                return True, f"Your wounds bleed for {damage_taken} damage! ({game_state.player.health}/{game_state.player.max_health} HP)"
            else:
                # Return True for damage but no message to display
                return True, None
        return False, None
    
    def apply_initial(self, game_state):
        """Initial bleeding application"""
        return True, "Your wounds are bleeding! You'll take damage over time."
    
    def apply_removal(self, game_state):
        """When bleeding stops"""
        return True, "Your bleeding has stopped."

# Add to the import and creation in enhanced combat when appropriate
def apply_bleeding_effect(game_state, duration, strength):
    """Helper function to apply bleeding effect to player"""
    bleed = BleedingEffect(duration=duration, strength=strength)
    game_state.status_effect_manager.add_effect(bleed)
    return bleed
