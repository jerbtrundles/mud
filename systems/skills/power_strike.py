import random
from skill import Skill

class PowerStrike(Skill):
    """A powerful attack that deals extra damage"""
    def __init__(self):
        super().__init__(
            name="power_strike",
            description="A powerful strike that deals 50% more damage but has a longer cooldown.",
            level_req=2,
            cooldown=45,  # 45 second cooldown
            cost=0
        )
    
    def use(self, game_state, target=None):
        """Use power strike in combat"""
        super().use(game_state)
        
        # Check if in combat
        if not target or not hasattr(target, 'health'):
            return "You swing your weapon forcefully, but hit only air. This skill must be used in combat."
        
        # Calculate damage (50% more than normal attack)
        base_damage = int(game_state.player.attack_power() * 1.5)
        damage_range = int(base_damage * 0.2)  # 20% variance
        final_damage = random.randint(base_damage - damage_range, base_damage + damage_range)
        
        # Apply damage
        actual_damage = target.take_damage(final_damage)
        
        game_state.add_to_history(f"You execute a powerful strike against the {target.name}, dealing {actual_damage} damage!", (255, 50, 50))
        
        return None