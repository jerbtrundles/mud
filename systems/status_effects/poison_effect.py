import time
from status_effects import StatusEffect

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
        self.verbose = False  # Set to False to reduce message noise
        self.last_health_message = 0  # Track when we last showed a health message
        self.health_message_interval = 15  # Only show health message every 15 seconds
    
    def _tick_effect(self, game_state):
        """Apply poison damage"""
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
                return True, f"You take {damage_taken} poison damage! ({game_state.player.health}/{game_state.player.max_health} HP)"
            else:
                # Return True for damage but no message to display
                return True, None
        return False, None
    
    def apply_initial(self, game_state):
        """Initial poison application"""
        return True, "You've been poisoned! The venom courses through your veins."
    
    def apply_removal(self, game_state):
        """When poison wears off"""
        return True, "The poison has worn off. You feel better."
