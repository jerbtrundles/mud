class SkillManager:
    """Manages the player's learned skills and their usage"""
    def __init__(self, game_state):
        self.game_state = game_state
        self.skills = {}  # {skill_name: Skill}
        self.available_skills = self._initialize_skills()
    
    def _initialize_skills(self):
        """Initialize all possible skills in the game"""
        skills = {
            # Combat skills
            "power_strike": PowerStrike(),
            "quick_slash": QuickSlash(),
            "defensive_stance": DefensiveStance(),
            "precise_aim": PreciseAim(),
            "whirlwind_attack": WhirlwindAttack(),
            
            # Utility skills
            "first_aid": FirstAid(),
            "keen_eye": KeenEye(),
            "treasure_sense": TreasureSense(),
            
            # Advanced skills
            "stunning_blow": StunningBlow(),
            "battle_cry": BattleCry(),
            "shadowstep": Shadowstep(),
        }
        return skills
    
    def learn_skill(self, skill_name):
        """Learn a new skill if available"""
        if skill_name in self.available_skills and skill_name not in self.skills:
            skill = self.available_skills[skill_name]
            
            # Check level requirement
            if self.game_state.player.level < skill.level_requirement:
                return False, f"You need to be level {skill.level_requirement} to learn {skill.display_name}."
            
            # Add to learned skills
            self.skills[skill_name] = skill
            return True, f"You have learned {skill.display_name}!"
        
        elif skill_name in self.skills:
            return False, f"You already know {self.available_skills[skill_name].display_name}."
        else:
            return False, f"Skill '{skill_name}' does not exist."
    
    def use_skill(self, skill_name, target=None):
        """Use a learned skill"""
        if skill_name not in self.skills:
            return False, f"You don't know the skill '{skill_name}'."
        
        skill = self.skills[skill_name]
        current_time = self.game_state.get_game_time()
        
        # Check if skill can be used
        can_use, message = skill.can_use(self.game_state.player, current_time)
        if not can_use:
            return False, message
        
        # Use the skill
        return True, skill.use(self.game_state, target)
    
    def get_available_skills(self):
        """Get list of skills that could be learned at the current level"""
        available = []
        for skill_name, skill in self.available_skills.items():
            if skill_name not in self.skills and self.game_state.player.level >= skill.level_requirement:
                available.append((skill_name, skill))
        return available
    
    def get_learned_skills(self):
        """Get list of learned skills"""
        return [(name, skill) for name, skill in self.skills.items()]
    