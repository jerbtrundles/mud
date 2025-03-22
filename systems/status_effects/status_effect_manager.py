import time

class StatusEffectManager:
    """Manages all status effects on the player"""
    def __init__(self, game_state):
        self.game_state = game_state
        self.active_effects = {}  # {effect_name: StatusEffect}
    
    def add_effect(self, effect):
        """Add a status effect to the player"""
        # Check if already affected
        existing = self.active_effects.get(effect.name)
        if existing:
            # If new effect is stronger, replace the old one
            if effect.strength > existing.strength:
                self.remove_effect(effect.name, suppress_message=True)
                self.active_effects[effect.name] = effect
                success, message = effect.apply_initial(self.game_state)
                if success and message:
                    self.game_state.add_to_history(message, effect.message_color)
            # If new effect has longer duration, extend the current one
            elif effect.get_time_remaining() > existing.get_time_remaining():
                existing.duration = effect.duration
                existing.start_time = time.time()
                self.game_state.add_to_history(f"Your {effect.display_name.lower()} has been extended!", effect.message_color)
            # Otherwise, do nothing but notify player
            else:
                self.game_state.add_to_history(f"You're already suffering from {effect.display_name.lower()}.", effect.message_color)
        else:
            # Apply new effect
            self.active_effects[effect.name] = effect
            success, message = effect.apply_initial(self.game_state)
            if success and message:
                self.game_state.add_to_history(message, effect.message_color)
    
    def remove_effect(self, effect_name, suppress_message=False):
        """Remove a status effect"""
        if effect_name in self.active_effects:
            effect = self.active_effects[effect_name]
            success, message = effect.apply_removal(self.game_state)
            
            # Only show message if not suppressed
            if success and message and not suppress_message:
                self.game_state.add_to_history(message, effect.message_color)
                
            del self.active_effects[effect_name]
            return True
        return False
    
    def update(self):
        """Update all active effects (call this from game loop)"""
        current_time = time.time()
        effects_to_remove = []
        
        for name, effect in self.active_effects.items():
            # Check if effect has expired
            if effect.is_expired(current_time):
                effects_to_remove.append(name)
                continue
            
            # Apply effect tick
            success, message = effect.apply_tick(self.game_state, current_time)
            if success and message:
                self.game_state.add_to_history(message, effect.message_color)
        
        # Remove expired effects
        for name in effects_to_remove:
            self.remove_effect(name)
    
    def has_effect(self, effect_name):
        """Check if player has a specific effect"""
        return effect_name in self.active_effects
    
    def get_status_text(self):
        """Get text describing all current status effects"""
        if not self.active_effects:
            return ""
            
        status_texts = []
        for effect in self.active_effects.values():
            status_texts.append(f"{effect.icon} {effect.get_status_text()}")
            
        return "; ".join(status_texts)
    
    def cure_all_effects(self):
        """Remove all status effects"""
        effect_names = list(self.active_effects.keys())  # Create a copy
        for name in effect_names:
            self.remove_effect(name)