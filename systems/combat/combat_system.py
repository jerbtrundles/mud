# systems/combat/combat_system.py
"""
A dedicated combat system module that handles all combat-related functionality.
"""

import random
import time
from enum import Enum

class CombatResult(Enum):
    """Possible results of a combat turn or full combat"""
    ONGOING = 0
    PLAYER_VICTORY = 1
    PLAYER_DEFEAT = 2
    PLAYER_FLED = 3
    ENEMY_FLED = 4

class CombatSystem:
    """Handles all combat interactions in the game"""
    
    def __init__(self, game_state):
        """
        Initialize the combat system
        
        Args:
            game_state: The game state object
        """
        self.game_state = game_state
        self.active_combat = False
        self.current_enemies = []  # List of enemies currently in combat
        self.turn_count = 0
        self.combat_log = []  # List of combat messages
        self.initiative_order = []  # List of entities in turn order
        self.current_actor_index = 0  # Index of current actor in initiative
        self.player_last_action = None
        
    def start_combat(self, enemies):
        """
        Start a combat encounter with specified enemies
        
        Args:
            enemies: List of enemies to fight
            
        Returns:
            bool: True if combat started successfully
        """
        if self.active_combat:
            self.log_message("Already in combat!")
            return False
            
        # Start new combat
        self.active_combat = True
        self.current_enemies = enemies if isinstance(enemies, list) else [enemies]
        self.turn_count = 0
        self.combat_log = []
        
        # Determine initiative order
        self._determine_initiative()
        
        # Initial combat message
        if len(self.current_enemies) == 1:
            enemy = self.current_enemies[0]
            self.log_message(f"Combat begins against {enemy.name}!")
        else:
            enemy_names = [e.name for e in self.current_enemies]
            self.log_message(f"Combat begins against {', '.join(enemy_names)}!")
            
        # Apply any start-of-combat effects
        self._apply_combat_start_effects()
        
        return True
    
    def _determine_initiative(self):
        """Determine the order of turns based on initiative"""
        # Simple implementation - could be expanded with initiative stats
        entities = [self.game_state.player] + self.current_enemies
        
        # Roll initiative for each entity (eventually based on dexterity/agility)
        init_rolls = []
        for entity in entities:
            init_value = random.randint(1, 20)
            # Add bonus if this entity has an initiative bonus
            if hasattr(entity, 'initiative_bonus'):
                init_value += entity.initiative_bonus
            init_rolls.append((entity, init_value))
        
        # Sort by initiative value (higher goes first)
        init_rolls.sort(key=lambda x: x[1], reverse=True)
        
        # Extract just the entities in order
        self.initiative_order = [entity for entity, _ in init_rolls]
        self.current_actor_index = 0
        
        # Log the initiative order
        self.log_message("Initiative order:")
        for i, entity in enumerate(self.initiative_order):
            if hasattr(entity, 'name'):
                self.log_message(f"{i+1}. {entity.name}")
            else:
                self.log_message(f"{i+1}. Player")
    
    def _apply_combat_start_effects(self):
        """Apply effects that trigger at the start of combat"""
        # Example: Surprise checks, ambush bonuses, etc.
        # This is a placeholder for expansion
        pass
    
    def process_turn(self):
        """
        Process a single combat turn
        
        Returns:
            CombatResult: The result of this turn
        """
        if not self.active_combat:
            return CombatResult.ONGOING
            
        # Get the current actor
        current_actor = self.initiative_order[self.current_actor_index]
        
        # Process actor's turn
        if current_actor == self.game_state.player:
            # Player's turn is processed through direct commands
            # This will be called by the command handler
            pass
        else:
            # AI turn
            self._process_enemy_turn(current_actor)
            
        # Advance to next actor
        self.current_actor_index = (self.current_actor_index + 1) % len(self.initiative_order)
        
        # If we've gone through all actors, increment turn counter
        if self.current_actor_index == 0:
            self.turn_count += 1
            self._apply_turn_end_effects()
            
        # Check combat results
        return self._check_combat_state()
    
    def _process_enemy_turn(self, enemy):
        """
        Process an enemy's turn
        
        Args:
            enemy: The enemy entity taking its turn
        """
        if not enemy.is_alive():
            self.log_message(f"{enemy.name} is defeated and cannot act.")
            return
            
        # Simple AI: almost always attack, but occasionally use special abilities
        player = self.game_state.player
        
        # Environmental effects that might affect enemy accuracy
        env_system = self.game_state.get_current_environment_system()
        env_effects = {}
        if env_system:
            env_effects = env_system.get_effects(self.game_state.current_room)
        
        # Determine attack hit chance (base 80%)
        hit_chance = 0.8
        enemy_accuracy_mod = env_effects.get("enemy_accuracy", 0)
        hit_chance += enemy_accuracy_mod / 10  # Convert to percentage
        hit_chance = max(0.5, min(0.95, hit_chance))  # Clamp between 50% and 95%
        
        # Player dodge chance (base 10%)
        dodge_chance = 0.1
        
        # Roll for hit
        if random.random() < dodge_chance:
            self.log_message(f"You nimbly dodge the {enemy.name}'s attack!")
            return
            
        if random.random() < hit_chance:
            # Determine if this is a special attack
            special_attack = None
            
            if hasattr(enemy, 'special_attacks') and enemy.special_attacks:
                for effect_name, effect_data in enemy.special_attacks.items():
                    if random.random() < effect_data.get("chance", 0):
                        special_attack = (effect_name, effect_data)
                        break
            
            # Calculate and apply damage
            if special_attack:
                self._process_special_attack(enemy, special_attack)
            else:
                # Regular attack
                self._process_regular_attack(enemy)
        else:
            # Miss
            self.log_message(f"The {enemy.name} attacks but misses you!")
    
    def _process_special_attack(self, enemy, special_attack):
        """
        Process a special attack from an enemy
        
        Args:
            enemy: The enemy performing the attack
            special_attack: Tuple of (effect_name, effect_data)
        """
        player = self.game_state.player
        attack_name, attack_data = special_attack
        
        # Calculate base damage for this attack
        base_damage = random.randint(
            max(1, enemy.attack - 2),
            enemy.attack + 2
        )
        
        # Apply modifiers based on attack type
        if attack_name == "poison":
            # Apply poison effect
            if hasattr(self.game_state, 'status_effect_manager'):
                from systems.status_effects.status_effects import PoisonEffect
                poison = PoisonEffect(
                    duration=attack_data.get("duration", 30),
                    strength=attack_data.get("strength", 1)
                )
                self.game_state.status_effect_manager.add_effect(poison)
                
            # Display message
            message = attack_data.get("message", f"The {enemy.name} poisons you!")
            self.log_message(message, color=(0, 180, 0))
            
        elif attack_name == "ranged":
            # Ranged attack with damage multiplier
            damage_mult = attack_data.get("damage_mult", 1.2)
            base_damage = int(base_damage * damage_mult)
            
            # Display message
            message = attack_data.get("message", f"The {enemy.name} attacks from a distance!")
            self.log_message(message)
            
        elif attack_name == "magic":
            # Magic attack with damage multiplier
            damage_mult = attack_data.get("damage_mult", 1.5)
            base_damage = int(base_damage * damage_mult)
            
            # Display message
            message = attack_data.get("message", f"The {enemy.name} casts a spell at you!")
            self.log_message(message)
            
        elif attack_name == "rend":
            # Apply bleeding status effect
            if hasattr(self.game_state, 'status_effect_manager'):
                from systems.status_effects.bleeding_effect import BleedingEffect
                bleed = BleedingEffect(
                    duration=attack_data.get("bleed_duration", 20),
                    strength=attack_data.get("bleed_damage", 1)
                )
                self.game_state.status_effect_manager.add_effect(bleed)
            
            # Display message
            message = attack_data.get("message", f"The {enemy.name} tears at your flesh!")
            self.log_message(message)
            
        else:
            # Default for unknown special attacks
            message = f"The {enemy.name} uses an unknown special attack!"
            self.log_message(message)
        
        # Apply damage to player
        final_damage = max(1, base_damage - player.defense_power())
        actual_damage = player.take_damage(final_damage)
        
        self.log_message(f"You take {actual_damage} damage!")
        self.log_message(f"Your health: {player.health}/{player.max_health}")
    
    def _process_regular_attack(self, enemy):
        """
        Process a regular attack from an enemy
        
        Args:
            enemy: The enemy performing the attack
        """
        player = self.game_state.player
        
        # Calculate base damage
        base_damage = random.randint(
            max(1, enemy.attack - 2),
            enemy.attack + 2
        )
        
        # Apply player defense
        final_damage = max(1, base_damage - player.defense_power())
        actual_damage = player.take_damage(final_damage)
        
        self.log_message(f"The {enemy.name} hits you for {actual_damage} damage!")
        self.log_message(f"Your health: {player.health}/{player.max_health}")
    
    def player_attack(self, target_enemy=None):
        """
        Execute a player attack
        
        Args:
            target_enemy: The enemy to attack, or None for auto-targeting
            
        Returns:
            tuple: (success, message)
        """
        if not self.active_combat:
            return False, "You're not in combat."
            
        # If no target specified and only one enemy, auto-target
        if target_enemy is None and len(self.current_enemies) == 1:
            target_enemy = self.current_enemies[0]
        elif target_enemy is None:
            return False, "You must specify which enemy to attack."
            
        # Verify target is in combat
        if target_enemy not in self.current_enemies:
            return False, f"That enemy is not in this combat."
            
        # Check if it's the player's turn
        current_actor = self.initiative_order[self.current_actor_index]
        if current_actor != self.game_state.player:
            return False, f"It's not your turn to act."
            
        # Calculate hit chance (base 90%)
        player_hit_chance = 0.9
        
        # Apply modifiers from equipment and environment
        env_system = self.game_state.get_current_environment_system()
        if env_system:
            env_effects = env_system.get_effects(self.game_state.current_room)
            if "player_accuracy" in env_effects:
                player_hit_chance += env_effects["player_accuracy"] / 10
                
        # Cap hit chance
        player_hit_chance = max(0.5, min(0.99, player_hit_chance))
        
        # Roll to hit
        if random.random() < player_hit_chance:
            # Critical hit check
            crit_chance = 0.05
            is_critical = random.random() < crit_chance
            
            # Calculate damage
            base_damage = random.randint(
                max(1, self.game_state.player.attack_power() - 2),
                self.game_state.player.attack_power() + 3
            )
            
            # Apply critical hit bonus
            if is_critical:
                base_damage = int(base_damage * 1.5)
                
            # Apply environmental modifiers
            if env_system:
                env_effects = env_system.get_effects(self.game_state.current_room)
                attack_modifier = env_effects.get("player_attack", 0)
                base_damage = max(1, base_damage + attack_modifier)
                
            # Apply damage to target
            actual_damage = target_enemy.take_damage(base_damage)
            
            # Log attack result
            if is_critical:
                self.log_message(f"You land a critical hit on the {target_enemy.name} for {actual_damage} damage!", color=(255, 100, 0))
            else:
                self.log_message(f"You hit the {target_enemy.name} for {actual_damage} damage!")
                
            # Check if enemy died
            if not target_enemy.is_alive():
                self.log_message(f"You have defeated the {target_enemy.name}!")
                
                # Award experience
                exp_gained = target_enemy.experience
                leveled_up = self.game_state.player.gain_experience(exp_gained)
                self.log_message(f"You gain {exp_gained} experience points.")
                
                if leveled_up:
                    self.log_message(f"You leveled up! You are now level {self.game_state.player.level}!", color=(255, 255, 0))
                    
                # Process loot drops
                self._process_enemy_drops(target_enemy)
                
                # Update bestiary
                if hasattr(self.game_state, 'bestiary'):
                    self.game_state.bestiary.record_encounter(
                        target_enemy.name, 
                        killed=True,
                        damage_dealt=actual_damage,
                        damage_taken=0,
                        location=self.game_state.current_room
                    )
                
                # Update quest progress
                if hasattr(self.game_state, 'quest_manager'):
                    self.game_state.quest_manager.update_quest_progress("kill", target_enemy.name, self.game_state.current_room)
        else:
            self.log_message(f"You swing at the {target_enemy.name} but miss!")
            
        # Record that player took their turn
        self.player_last_action = "attack"
        
        # Advance turn
        self.current_actor_index = (self.current_actor_index + 1) % len(self.initiative_order)
        
        # Process next turn automatically if it's not player's turn
        while self.active_combat and self.initiative_order[self.current_actor_index] != self.game_state.player:
            result = self.process_turn()
            if result != CombatResult.ONGOING:
                break
                
        return True, None
    
    def player_use_item(self, item):
        """
        Player uses an item during combat
        
        Args:
            item: The item to use
            
        Returns:
            tuple: (success, message)
        """
        if not self.active_combat:
            return False, "You're not in combat."
            
        # Check if it's the player's turn
        current_actor = self.initiative_order[self.current_actor_index]
        if current_actor != self.game_state.player:
            return False, f"It's not your turn to act."
            
        # Use the item (handled by the item system)
        success, message = item.use(self.game_state)
        
        if success:
            # Record that player took their turn
            self.player_last_action = "use_item"
            
            # Advance turn
            self.current_actor_index = (self.current_actor_index + 1) % len(self.initiative_order)
            
            # Process next turn automatically if it's not player's turn
            while self.active_combat and self.initiative_order[self.current_actor_index] != self.game_state.player:
                result = self.process_turn()
                if result != CombatResult.ONGOING:
                    break
                    
        return success, message
    
    def player_use_skill(self, skill, target=None):
        """
        Player uses a skill during combat
        
        Args:
            skill: The skill to use
            target: Optional target for the skill
            
        Returns:
            tuple: (success, message)
        """
        if not self.active_combat:
            return False, "You're not in combat."
            
        # Check if it's the player's turn
        current_actor = self.initiative_order[self.current_actor_index]
        if current_actor != self.game_state.player:
            return False, f"It's not your turn to act."
            
        # If no target provided but skill needs one, use first enemy
        if target is None and len(self.current_enemies) > 0:
            target = self.current_enemies[0]
            
        # Use the skill
        success, message = skill.use(self.game_state, target)
        
        if success:
            # Record that player took their turn
            self.player_last_action = "use_skill"
            
            # Advance turn
            self.current_actor_index = (self.current_actor_index + 1) % len(self.initiative_order)
            
            # Process next turn automatically if it's not player's turn
            while self.active_combat and self.initiative_order[self.current_actor_index] != self.game_state.player:
                result = self.process_turn()
                if result != CombatResult.ONGOING:
                    break
                    
        return success, message
    
    def player_flee(self):
        """
        Player attempts to flee combat
        
        Returns:
            tuple: (success, message)
        """
        if not self.active_combat:
            return False, "You're not in combat."
            
        # Check if it's the player's turn
        current_actor = self.initiative_order[self.current_actor_index]
        if current_actor != self.game_state.player:
            return False, f"It's not your turn to act."
            
        # Base 50% chance to flee successfully
        flee_chance = 0.5
        
        # Modifiers based on enemy types, environment, etc.
        # (placeholder for future expansion)
        
        if random.random() < flee_chance:
            self.log_message("You successfully flee from combat!")
            self.end_combat(CombatResult.PLAYER_FLED)
            return True, "You escaped!"
        else:
            self.log_message("You fail to escape!")
            
            # Player loses their turn
            self.player_last_action = "flee_attempt"
            
            # Advance turn
            self.current_actor_index = (self.current_actor_index + 1) % len(self.initiative_order)
            
            # Process next turn automatically if it's not player's turn
            while self.active_combat and self.initiative_order[self.current_actor_index] != self.game_state.player:
                result = self.process_turn()
                if result != CombatResult.ONGOING:
                    break
                    
            return False, "You failed to escape!"
    
    def _apply_turn_end_effects(self):
        """Apply effects that occur at the end of each combat turn"""
        # Apply status effects damage/healing
        if hasattr(self.game_state, 'status_effect_manager'):
            self.game_state.status_effect_manager.update()
            
        # Remove defeated enemies from initiative order
        self.initiative_order = [entity for entity in self.initiative_order if not hasattr(entity, 'is_alive') or entity.is_alive()]
        
        # Adjust current actor index if needed
        if self.current_actor_index >= len(self.initiative_order):
            self.current_actor_index = 0
    
    def _check_combat_state(self):
        """
        Check if combat should end
        
        Returns:
            CombatResult: The current state of combat
        """
        # Remove defeated enemies
        self.current_enemies = [e for e in self.current_enemies if e.is_alive()]
        
        # Check if all enemies are defeated
        if not self.current_enemies:
            self.end_combat(CombatResult.PLAYER_VICTORY)
            return CombatResult.PLAYER_VICTORY
            
        # Check if player is defeated
        if self.game_state.player.health <= 0:
            self.end_combat(CombatResult.PLAYER_DEFEAT)
            return CombatResult.PLAYER_DEFEAT
            
        # Combat continues
        return CombatResult.ONGOING
    
    def _process_enemy_drops(self, enemy):
        """
        Process loot drops from a defeated enemy
        
        Args:
            enemy: The defeated enemy
        """
        # Import only if needed to avoid circular imports
        from systems.enemy_drops import process_enemy_drops, display_drops
        
        drops = process_enemy_drops(enemy, self.game_state.player.level)
        display_drops(self.game_state, enemy.name, drops)
        
        # Add drops to player inventory or room
        for item_name, quantity in drops.items():
            if item_name == "coin":
                self.game_state.coins += quantity
            else:
                for _ in range(quantity):
                    self.game_state.player.add_to_inventory(item_name)
    
    def end_combat(self, result):
        """
        End the current combat encounter
        
        Args:
            result: CombatResult enum value
        """
        self.active_combat = False
        
        # Clean up and finalize combat
        if result == CombatResult.PLAYER_VICTORY:
            self.log_message("Victory! You have defeated all enemies.")
            
            # Update journal for combat tracking
            if hasattr(self.game_state, 'journal'):
                enemy_names = [e.name for e in self.initiative_order if e != self.game_state.player]
                self.game_state.journal.add_entry(f"Defeated {', '.join(enemy_names)} in combat.", "combat")
                
        elif result == CombatResult.PLAYER_DEFEAT:
            self.log_message("You have been defeated!")
            self.game_state.game_over = True
            
            # Update journal
            if hasattr(self.game_state, 'journal'):
                enemy_names = [e.name for e in self.current_enemies]
                self.game_state.journal.add_entry(f"Defeated by {', '.join(enemy_names)} in combat.", "death")
                
        elif result == CombatResult.PLAYER_FLED:
            self.log_message("You escaped from combat.")
            
        elif result == CombatResult.ENEMY_FLED:
            self.log_message("The enemies have fled.")
        
        # Clear combat state
        self.current_enemies = []
        self.initiative_order = []
        self.turn_count = 0
    
    def log_message(self, message, color=(200, 200, 200)):
        """
        Add a message to the combat log and game history
        
        Args:
            message: The message to log
            color: RGB color tuple for the message
        """
        self.combat_log.append((message, color))
        self.game_state.add_to_history(message, color)
    
    def get_combat_log(self):
        """Get the combat log entries"""
        return self.combat_log