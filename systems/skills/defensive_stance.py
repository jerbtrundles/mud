from skills import Skill

class DefensiveStance(Skill):
    """Temporarily increases defense at the cost of attack"""
    def __init__(self):
        super().__init__(
            name="defensive_stance",
            description="Enter a defensive stance, increasing defense by 5 but reducing attack by 2 for 30 seconds.",
            level_req=3,
            cooldown=60,  # 60 second cooldown
            cost=0
        )
        self.active = False
        self.effect_end_time = 0
        self.defense_bonus = 5
        self.attack_penalty = 2
    
    def use(self, game_state, target=None):
        """Enter defensive stance"""
        super().use(game_state)
        
        # Set effect duration
        current_time = game_state.get_game_time()
        self.effect_end_time = current_time + 30  # 30 second effect
        self.active = True
        
        # Apply effect to player
        game_state.player.temp_defense_bonus += self.defense_bonus
        game_state.player.temp_attack_penalty = self.attack_penalty
        
        game_state.add_to_history("You enter a defensive stance, sacrificing offense for defense.", (100, 100, 255))
        game_state.add_to_history(f"Defense +{self.defense_bonus}, Attack -{self.attack_penalty} for 30 seconds.", (100, 100, 255))
        
        return None
    
    def update(self, game_state):
        """Check if effect has expired"""
        if not self.active:
            return
            
        current_time = game_state.get_game_time()
        if current_time >= self.effect_end_time:
            # Remove effect
            game_state.player.temp_defense_bonus -= self.defense_bonus
            game_state.player.temp_attack_penalty = 0
            self.active = False
            
            game_state.add_to_history("Your defensive stance ends as you return to a normal fighting position.", (100, 100, 255))