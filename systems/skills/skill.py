class Skill:
    """Represents a special skill or ability that the player can learn and use"""
    def __init__(self, name, description, level_req=1, cooldown=30, cost=0):
        self.name = name  # Internal name
        self.display_name = name.replace('_', ' ').title()  # Formatted name
        self.description = description
        self.level_requirement = level_req  # Minimum player level required
        self.cooldown = cooldown  # Cooldown time in seconds
        self.cost = cost  # Cost in mana/energy (if implemented)
        self.last_used_time = 0  # Time when skill was last used
    
    def can_use(self, player, current_time):
        """Check if the skill can be used now"""
        # Check level requirement
        if player.level < self.level_requirement:
            return False, f"You need to be level {self.level_requirement} to use {self.display_name}."
        
        # Check cooldown
        time_since_last_use = current_time - self.last_used_time
        if time_since_last_use < self.cooldown:
            time_left = int(self.cooldown - time_since_last_use)
            return False, f"{self.display_name} is on cooldown. Available in {time_left} seconds."
        
        # Check cost (future - if mana/energy system implemented)
        # if player.mana < self.cost:
        #     return False, f"Not enough mana. {self.display_name} requires {self.cost} mana."
        
        return True, "Ready"
    
    def use(self, game_state, target=None):
        """Use the skill - to be overridden by specific skills"""
        # Mark as used
        self.last_used_time = game_state.get_game_time()
        
        # Deduct cost (future)
        # game_state.player.mana -= self.cost
        
        return "You use " + self.display_name

# Other skill implementations would follow similar pattern
# class PreciseAim(Skill):
#     """Increases critical hit chance for a short time"""
#     def __init__(self):
#         super().__init__(
#             name="precise_aim",
#             description="Focus your aim, increasing critical hit chance by 20% for 20 seconds.",
#             level_req=4,
#             cooldown=90,
#             cost=0
#         )
#         # Implementation left as exercise

# class WhirlwindAttack(Skill):
#     """Attack all enemies in the room"""
#     def __init__(self):
#         super().__init__(
#             name="whirlwind_attack",
#             description="Spin in a circle, attacking all enemies in the room for 70% of your normal damage.",
#             level_req=6,
#             cooldown=120,
#             cost=0
#         )
#         # Implementation left as exercise

# class FirstAid(Skill):
#     """Heal yourself for a small amount"""
#     def __init__(self):
#         super().__init__(
#             name="first_aid",
#             description="Apply first aid to heal for 20% of your maximum health.",
#             level_req=2,
#             cooldown=180,
#             cost=0
#         )
#         # Implementation left as exercise

# class KeenEye(Skill):
#     """Reveals hidden items in the room"""
#     def __init__(self):
#         super().__init__(
#             name="keen_eye",
#             description="Carefully search the area, revealing hidden items and secrets.",
#             level_req=3,
#             cooldown=300,
#             cost=0
#         )
#         # Implementation left as exercise

# class TreasureSense(Skill):
#     """Sense nearby treasure"""
#     def __init__(self):
#         super().__init__(
#             name="treasure_sense",
#             description="Gain a temporary sense for valuable items in nearby rooms.",
#             level_req=5,
#             cooldown=600,
#             cost=0
#         )
#         # Implementation left as exercise

# class StunningBlow(Skill):
#     """Stun an enemy, preventing their next attack"""
#     def __init__(self):
#         super().__init__(
#             name="stunning_blow",
#             description="Strike an enemy in a vulnerable spot, stunning them and preventing their next attack.",
#             level_req=7,
#             cooldown=150,
#             cost=0
#         )
#         # Implementation left as exercise

# class BattleCry(Skill):
#     """Increase attack power for a short time"""
#     def __init__(self):
#         super().__init__(
#             name="battle_cry",
#             description="Let out a fearsome battle cry, increasing your attack power by 5 for 30 seconds.",
#             level_req=5,
#             cooldown=180,
#             cost=0
#         )
#         # Implementation left as exercise

# class Shadowstep(Skill):
#     """Avoid all damage from the next attack"""
#     def __init__(self):
#         super().__init__(
#             name="shadowstep",
#             description="Move with supernatural speed, completely avoiding the next attack against you.",
#             level_req=8,
#             cooldown=300,
#             cost=0
#         )
#         # Implementation left as exercise

