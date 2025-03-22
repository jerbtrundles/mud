# entities/enemy.py
"""
Enemy entity class with AI behavior patterns and specialized functionality.
"""

import random
import time
from entities.entity import Entity

class Enemy(Entity):
    """Enemy entity with AI behavior and specialized functionality"""
    
    def __init__(self, name, description, health, attack, defense=0, level=1, 
                 experience=None, allowed_rooms=None, respawn_delay=60, 
                 ai_type="basic", special_attacks=None, drops=None, **kwargs):
        """
        Initialize an enemy entity
        
        Args:
            name (str): Enemy name
            description (str): Enemy description
            health (int): Starting/maximum health
            attack (int): Base attack power
            defense (int): Base defense
            level (int): Enemy level
            experience (int): Experience gained when defeated (defaults to level*5)
            allowed_rooms (list): List of room IDs where this enemy can spawn
            respawn_delay (int): Seconds until respawn after death
            ai_type (str): Type of AI behavior ("basic", "aggressive", "ranged", etc.)
            special_attacks (dict): Dictionary of special attacks this enemy can use
            drops (dict): Dictionary defining item drops when defeated
            **kwargs: Additional attributes
        """
        super().__init__(name, description, health, attack, defense, level, **kwargs)
        
        # Enemy-specific attributes
        self.experience = experience if experience is not None else level * 5
        self.allowed_rooms = allowed_rooms or []
        self.current_room = None
        self.respawn_delay = respawn_delay
        self.last_move_time = time.time()
        self.death_time = None
        self.ai_type = ai_type
        self.special_attacks = special_attacks or {}
        self.drops = drops or {}
        
        # Behavior flags
        self.is_aggressive = ai_type in ["aggressive", "berserker"]
        self.is_fleeing = False
        self.flee_threshold = 0.2  # Flee at 20% health by default
        
        # Add enemy tag
        self.add_tag("enemy")
    
    def _on_death(self):
        """Handle enemy death"""
        super()._on_death()
        self.death_time = time.time()
    
    def respawn(self):
        """
        Respawn the enemy
        
        Returns:
            bool: True if respawned
        """
        if self.is_alive():
            return False
            
        # Check if enough time has passed
        current_time = time.time()
        if self.death_time is None or current_time - self.death_time < self.respawn_delay:
            return False
            
        # Reset health and status
        self.health = self.max_health
        self.is_alive_flag = True
        self.is_fleeing = False
        self.death_time = None
        
        # Move to a random allowed room
        if self.allowed_rooms:
            self.current_room = random.choice(self.allowed_rooms)
            
        return True
    
    def move(self, available_rooms=None):
        """
        Move to a different room
        
        Args:
            available_rooms (list): Optional list of room IDs to choose from
                                  Defaults to allowed_rooms if not provided
        
        Returns:
            bool: True if moved
        """
        if not self.is_alive():
            return False
            
        rooms = available_rooms or self.allowed_rooms
        
        # Can't move if no rooms available
        if not rooms or len(rooms) <= 1:
            return False
            
        # Choose a room different from current
        candidates = [room for room in rooms if room != self.current_room]
        if not candidates:
            return False
            
        self.current_room = random.choice(candidates)
        self.last_move_time = time.time()
        
        return True
    
    def should_move(self, current_time=None):
        """
        Check if enemy should move based on time and AI type
        
        Args:
            current_time (float): Current time, defaults to time.time()
            
        Returns:
            bool: True if should move
        """
        if not self.is_alive():
            return False
            
        if current_time is None:
            current_time = time.time()
            
        # Base move interval depends on AI type
        if self.ai_type == "stationary":
            return False  # Never moves
        elif self.ai_type == "aggressive":
            move_interval = 10  # Move more frequently
        elif self.ai_type == "cautious":
            move_interval = 25  # Move less frequently
        else:
            move_interval = 15  # Default
            
        # Check time since last move
        return (current_time - self.last_move_time) >= move_interval
    
    def decide_action(self, game_state):
        """
        Decide what action to take based on AI type and situation
        
        Args:
            game_state: The current game state
            
        Returns:
            tuple: (action_type, target, params)
        """
        # If dead, no action
        if not self.is_alive():
            return ("none", None, {})
            
        # If not in same room as player, potential movement
        if self.current_room != game_state.current_room:
            if self.should_move():
                # Decide whether to move toward player based on AI type
                if self.ai_type == "aggressive" and random.random() < 0.7:
                    return ("move_toward_player", game_state.current_room, {})
                else:
                    return ("move_random", None, {})
            return ("none", None, {})
        
        # In same room as player, decide on combat action
        player = game_state.player
        
        # Check if should flee
        health_percentage = self.get_health_percentage()
        if health_percentage <= self.flee_threshold and self.ai_type != "berserker":
            self.is_fleeing = True
            return ("flee", None, {})
        
        # Choose attack type based on AI behavior
        # Default is regular attack
        attack_type = "regular_attack"
        attack_params = {}
        
        # Check for special attacks
        if self.special_attacks and random.random() < 0.3:  # 30% chance for special attack
            special_attack = self._choose_special_attack()
            if special_attack:
                attack_type = "special_attack"
                attack_params = {"special_type": special_attack}
        
        # Different AI types have different combat behaviors
        if self.ai_type == "cautious" and health_percentage < 0.5:
            # Cautious enemies are more likely to use defensive moves when hurt
            if random.random() < 0.4:
                return ("defensive_move", player, {})
        
        elif self.ai_type == "berserker":
            # Berserkers do more damage when low on health
            attack_params["rage_bonus"] = max(1.0, 2.0 - health_percentage * 2)  # Up to 2x damage when near death
        
        elif self.ai_type == "tactical":
            # Tactical enemies might attempt special maneuvers
            if random.random() < 0.25:
                tactics = ["flank", "feint", "disarm"]
                tactic = random.choice(tactics)
                return ("tactical_move", player, {"tactic": tactic})
        
        # Return the decided action
        return (attack_type, player, attack_params)
    
    def _choose_special_attack(self):
        """
        Choose a special attack based on available options and probabilities
        
        Returns:
            str: Name of special attack, or None
        """
        if not self.special_attacks:
            return None
            
        # Build a weighted list of possible attacks
        attacks = []
        weights = []
        
        for attack_name, attack_data in self.special_attacks.items():
            attacks.append(attack_name)
            weights.append(attack_data.get("chance", 0.1))
            
        # Choose based on weights
        if attacks:
            return random.choices(attacks, weights=weights, k=1)[0]
            
        return None
    
    def execute_action(self, action_type, target, params, game_state):
        """
        Execute a decided action
        
        Args:
            action_type (str): Type of action to execute
            target: Target of the action
            params (dict): Additional parameters
            game_state: The current game state
            
        Returns:
            tuple: (success, message)
        """
        if action_type == "none":
            return True, None
            
        elif action_type == "move_toward_player":
            if target and self.move([target]):
                return True, f"The {self.name} moves toward you."
            return False, None
            
        elif action_type == "move_random":
            if self.move():
                return True, f"The {self.name} moves away."
            return False, None
            
        elif action_type == "flee":
            # Try to move to a different room
            if self.move():
                return True, f"The {self.name} flees!"
            return False, f"The {self.name} tries to flee but can't escape!"
            
        elif action_type == "regular_attack":
            # Apply rage bonus for berserkers
            rage_bonus = params.get("rage_bonus", 1.0)
            damage_modifier = rage_bonus
            
            # Calculate damage
            base_damage = random.randint(
                max(1, int(self.attack * 0.8)),
                int(self.attack * 1.2)
            )
            
            modified_damage = int(base_damage * damage_modifier)
            
            # Apply to target if it's a player
            if target and hasattr(target, 'take_damage'):
                actual_damage = target.take_damage(modified_damage)
                
                # Build message
                if rage_bonus > 1.5:
                    return True, f"The {self.name} attacks you in a berserk rage for {actual_damage} damage!"
                else:
                    return True, f"The {self.name} attacks you for {actual_damage} damage."
                
            return False, None
            
        elif action_type == "special_attack":
            special_type = params.get("special_type")
            if not special_type or special_type not in self.special_attacks:
                return False, None
                
            attack_data = self.special_attacks[special_type]
            
            # Get message for this attack
            message = attack_data.get("message", f"The {self.name} uses a special attack!")
            
            # Handle different types of special attacks
            if special_type == "poison":
                # Apply poison status effect
                if hasattr(game_state, 'status_effect_manager'):
                    from systems.status_effects.status_effects import PoisonEffect
                    poison = PoisonEffect(
                        duration=attack_data.get("duration", 30),
                        strength=attack_data.get("strength", 1)
                    )
                    game_state.status_effect_manager.add_effect(poison)
                
                # Also deal some direct damage
                if target and hasattr(target, 'take_damage'):
                    damage = random.randint(
                        max(1, int(self.attack * 0.5)),
                        int(self.attack * 0.8)
                    )
                    target.take_damage(damage)
                    
            elif special_type == "ranged":
                # Ranged attack with damage multiplier
                if target and hasattr(target, 'take_damage'):
                    damage_mult = attack_data.get("damage_mult", 1.2)
                    damage = int(random.randint(
                        max(1, int(self.attack * 0.7)),
                        int(self.attack * 1.0)
                    ) * damage_mult)
                    
                    target.take_damage(damage)
                    
            elif special_type == "magic":
                # Magic attack with damage multiplier
                if target and hasattr(target, 'take_damage'):
                    damage_mult = attack_data.get("damage_mult", 1.5)
                    damage = int(random.randint(
                        max(1, int(self.attack * 0.8)),
                        int(self.attack * 1.1)
                    ) * damage_mult)
                    
                    target.take_damage(damage)
            
            # Return success and message
            return True, message
            
        elif action_type == "defensive_move":
            # Defensive moves might temporarily increase defense or reduce damage
            self.temp_defense_bonus = int(self.defense * 0.5)  # 50% defense boost
            self.temp_buff_end_time = time.time() + 30  # 30 second buff
            
            return True, f"The {self.name} takes a defensive stance."
            
        elif action_type == "tactical_move":
            tactic = params.get("tactic")
            if tactic == "flank":
                # Flanking gives a damage bonus on next attack
                self.attributes["next_attack_bonus"] = 1.5
                return True, f"The {self.name} moves to flank you."
                
            elif tactic == "feint":
                # Feinting might reduce player's defense temporarily
                if target and hasattr(target, 'temp_defense_bonus'):
                    target.temp_defense_bonus = max(-2, target.temp_defense_bonus - 2)
                    target.temp_buff_end_time = time.time() + 20  # 20 second debuff
                    return True, f"The {self.name} feints, leaving you off-balance."
                    
            elif tactic == "disarm":
                # Attempt to disarm (small chance)
                if random.random() < 0.1:  # 10% chance
                    # Not actually disarming, just reducing attack
                    if target and hasattr(target, 'temp_attack_bonus'):
                        target.temp_attack_bonus = max(-3, target.temp_attack_bonus - 3)
                        target.temp_buff_end_time = time.time() + 15  # 15 second debuff
                        return True, f"The {self.name} knocks your weapon aside momentarily!"
                return True, f"The {self.name} tries to disarm you but fails."
        
        # Fallback
        return False, None
    
    def get_drops(self, player_level=1, player_luck=0):
        """
        Generate drops when defeated
        
        Args:
            player_level (int): Level of player who defeated this enemy
            player_luck (int): Luck stat of player (if implemented)
            
        Returns:
            dict: Dictionary of {item_id: quantity} for drops
        """
        drops = {}
        
        # If enemy has specific drop data, use that
        if self.drops:
            # Process common drops (higher chance)
            if "common" in self.drops:
                for drop_info in self.drops["common"]:
                    item_name, min_qty, max_qty, base_chance = drop_info
                    
                    # Apply luck modifier to chance
                    modified_chance = base_chance * (1 + (player_luck * 0.05))
                    
                    if random.random() < modified_chance:
                        quantity = random.randint(min_qty, max_qty)
                        drops[item_name] = drops.get(item_name, 0) + quantity
            
            # Process uncommon drops (lower chance)
            if "uncommon" in self.drops:
                for drop_info in self.drops["uncommon"]:
                    item_name, min_qty, max_qty, base_chance = drop_info
                    
                    # Apply luck and level modifiers
                    level_factor = min(1.5, self.experience / 10)  # Proxy for enemy level
                    modified_chance = base_chance * level_factor * (1 + (player_luck * 0.1))
                    
                    if random.random() < modified_chance:
                        quantity = random.randint(min_qty, max_qty)
                        drops[item_name] = drops.get(item_name, 0) + quantity
            
            # Process rare drops (very low chance)
            if "rare" in self.drops:
                for drop_info in self.drops["rare"]:
                    item_name, min_qty, max_qty, base_chance = drop_info
                    
                    # Apply luck and level modifiers
                    level_factor = min(2.0, self.experience / 8)
                    modified_chance = base_chance * level_factor * (1 + (player_luck * 0.15))
                    
                    if random.random() < modified_chance:
                        quantity = random.randint(min_qty, max_qty)
                        drops[item_name] = drops.get(item_name, 0) + quantity
        
        # Add generic drops (coins almost always, other items occasionally)
        if not drops or random.random() < 0.3:  # 30% chance for additional generic drops
            # Calculate coin drop based on enemy level/experience
            enemy_level = max(1, self.experience // 5)  # Approximate level
            
            if random.random() < 0.9:  # 90% chance for coins
                base_coins = enemy_level * 2
                coin_amount = max(1, int(base_coins * random.uniform(0.7, 1.3)))  # ±30% variation
                drops["coin"] = drops.get("coin", 0) + coin_amount
            
            # Small chance for generic consumables
            if random.random() < 0.15:  # 15% chance
                if random.random() < 0.7:  # 70% of the time, healing potion
                    drops["healing_potion"] = drops.get("healing_potion", 0) + 1
                else:  # 30% of the time, something else
                    other_items = ["bread", "strong_healing_potion", "stamina_potion"]
                    item = random.choice(other_items)
                    drops[item] = drops.get(item, 0) + 1
        
        return drops
    
    def to_dict(self):
        """Convert enemy to dictionary for serialization"""
        data = super().to_dict()
        
        # Add enemy-specific data
        data.update({
            "allowed_rooms": self.allowed_rooms,
            "current_room": self.current_room,
            "respawn_delay": self.respawn_delay,
            "last_move_time": self.last_move_time,
            "death_time": self.death_time,
            "ai_type": self.ai_type,
            "is_aggressive": self.is_aggressive,
            "is_fleeing": self.is_fleeing,
            "flee_threshold": self.flee_threshold
        })
        
        # Save special attacks and drops if present
        if self.special_attacks:
            data["special_attacks"] = self.special_attacks
            
        if self.drops:
            data["drops"] = self.drops
            
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create an enemy from dictionary data"""
        # Create base enemy
        enemy = super().from_dict(data)
        
        # Set enemy-specific properties
        enemy.allowed_rooms = data.get("allowed_rooms", [])
        enemy.current_room = data.get("current_room")
        enemy.respawn_delay = data.get("respawn_delay", 60)
        enemy.last_move_time = data.get("last_move_time", time.time())
        enemy.death_time = data.get("death_time")
        enemy.ai_type = data.get("ai_type", "basic")
        enemy.is_aggressive = data.get("is_aggressive", enemy.ai_type in ["aggressive", "berserker"])
        enemy.is_fleeing = data.get("is_fleeing", False)
        enemy.flee_threshold = data.get("flee_threshold", 0.2)
        
        # Restore special attacks and drops
        if "special_attacks" in data:
            enemy.special_attacks = data["special_attacks"]
            
        if "drops" in data:
            enemy.drops = data["drops"]
            
        return enemy