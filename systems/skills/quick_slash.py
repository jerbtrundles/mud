import random
from skill import Skill

class QuickSlash(Skill):
    """A fast attack with lower cooldown but less damage"""
    def __init__(self):
        super().__init__(
            name="quick_slash",
            description="A quick attack that deals less damage but has a very short cooldown.",
            level_req=1,
            cooldown=10,  # 10 second cooldown
            cost=0
        )
    
    def use(self, game_state, target=None):
        """Use quick slash in combat"""
        super().use(game_state)
        
        # Check if in combat
        if not target or not hasattr(target, 'health'):
            return "You make a quick slash with your weapon. This skill must be used in combat."
        
        # Calculate damage (70% of normal attack)
        base_damage = int(game_state.player.attack_power() * 0.7)
        damage_range = int(base_damage * 0.1)  # 10% variance
        final_damage = random.randint(base_damage - damage_range, base_damage + damage_range)
        
        # Apply damage
        actual_damage = target.take_damage(final_damage)
        
        game_state.add_to_history(f"You perform a quick slash against the {target.name}, dealing {actual_damage} damage!", (220, 150, 150))
        
        return None