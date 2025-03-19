# enemy_manager.py
import random
import time
from entities.enemy import Enemy
from config.config import GameConfig
from core.utils import calculate_chance, get_random_element

class EnemyManager:
    def __init__(self, world):
        self.world = world
        self.enemies = []
        self.max_active_enemies = 5  # Maximum number of active enemies
        self.last_spawn_time = time.time()
        self.spawn_interval = 2  # Seconds between spawn checks
        self.game_state = None  # Will be set later

        EnemyManager._active_instance = self
        
        self.enemy_types = {
            "goblin": {
                "health": 20, 
                "attack": 5, 
                "experience": 5,
                "allowed_rooms": ["entrance", "cavern", "goblin_den"],
                "respawn_delay": 45
            },
            "skeleton": {
                "health": 30, 
                "attack": 8, 
                "experience": 5,
                "allowed_rooms": ["cavern", "narrow_passage"],
                "respawn_delay": 60
            },
            "troll": {
                "health": 50, 
                "attack": 12, 
                "experience": 5,
                "allowed_rooms": ["underground_lake", "hidden_grotto"],
                "respawn_delay": 90
            },
            "spider": {
                "health": 15, 
                "attack": 4, 
                "experience": 5,
                "allowed_rooms": ["entrance", "cavern"],
                "respawn_delay": 30
            },
            "orc": {
                "health": 35, 
                "attack": 9, 
                "experience": 5,
                "allowed_rooms": ["cavern", "goblin_den"],
                "respawn_delay": 75
            },
            "ghost": {
                "health": 25, 
                "attack": 7, 
                "experience": 5,
                "allowed_rooms": ["narrow_passage", "treasure_room"],
                "respawn_delay": 80
            },
            "rat": {
                "health": 10, 
                "attack": 3, 
                "experience": 5,
                "allowed_rooms": ["entrance", "cavern", "underground_lake"],
                "respawn_delay": 20
            },
            "bat": {
                "health": 8, 
                "attack": 2, 
                "experience": 5,
                "allowed_rooms": ["cavern", "narrow_passage", "hidden_grotto"],
                "respawn_delay": 15
            },
            "slime": {
                "health": 18, 
                "attack": 4, 
                "experience": 5,
                "allowed_rooms": ["underground_lake", "hidden_grotto"],
                "respawn_delay": 35
            },
            "zombie": {
                "health": 22, 
                "attack": 6, 
                "experience": 5,
                "allowed_rooms": ["goblin_den", "narrow_passage"],
                "respawn_delay": 55
            }
        }
        
        # Define region-appropriate enemies
        self.region_enemies = {
            "cave_system": ["bat", "spider", "rat", "slime"],
            "goblin_territory": ["goblin", "orc", "troll", "zombie"],
            "town": []  # No enemies in town
        }
        
        # Initialize with some enemies
        self.initialize_enemies()
    
    def set_game_state(self, game_state):
        """Set a reference to the game state"""
        self.game_state = game_state
    
    # Update the check_spawns method to use region-specific spawn rates
    def check_spawns(self, game_state):
        """Check if it's time to spawn new enemies using region-specific rates"""
        current_time = time.time()
        
        # Check if enough time has passed since last spawn check
        if current_time - self.last_spawn_time >= self.spawn_interval:
            self.last_spawn_time = current_time
            
            current_room = game_state.current_room
            
            # Get the region for this room
            region = game_state.world.get_region_for_room(current_room)
            
            if not region:
                return None  # No region, no spawn
            
            # Get environment effects from the region
            env_effects = region.environment_system.get_effects(current_room)
            env_spawn_modifier = env_effects.get("enemy_spawn_rate", 1.0)
            
            # Get region's enemy density
            region_density = region.enemy_density
            
            # Combined modifier (environment and region)
            spawn_rate_modifier = env_spawn_modifier * region_density
            
            # Modified spawn chance
            base_chance = 0.7  # 70% base chance
            modified_chance = min(0.95, base_chance * spawn_rate_modifier)  # Cap at 95%
            
            # Greatly reduce spawn chance in town/settlement areas
            if region.region_type == "settlement":
                modified_chance *= 0.1  # 90% reduction
            
            # Apply the modified chance
            if random.random() < modified_chance:
                new_enemy = self.spawn_enemy_for_region(region.name, current_room)
                
                # If combined multiplier is high, sometimes spawn an extra enemy
                if spawn_rate_modifier > 1.5 and random.random() < 0.3:  # 30% chance for bonus spawn
                    if self.count_active_enemies() < self.max_active_enemies:
                        extra_enemy = self.spawn_enemy_for_region(region.name, current_room)
                        
                return new_enemy
        
        return None
    
    def spawn_random_enemy(self):
        """Spawn a new random enemy if below the maximum"""
        if self.count_active_enemies() >= self.max_active_enemies:
            return None
                
        # Choose a random enemy type
        enemy_type = random.choice(list(self.enemy_types.keys()))
        enemy_data = self.enemy_types[enemy_type]
        
        # Choose a random allowed room for this enemy type
        if enemy_data["allowed_rooms"]:
            room_name = random.choice(enemy_data["allowed_rooms"])
        else:
            # Fallback to any room if allowed_rooms is empty
            room_name = random.choice(self.world.get_all_room_names())
        
        # Create the enemy
        enemy = Enemy(
            enemy_type,
            enemy_data["health"],
            enemy_data["attack"],
            enemy_data["experience"],
            enemy_data["allowed_rooms"],
            enemy_data["respawn_delay"]
        )
        
        # Set the room
        enemy.current_room = room_name
        
        # Add to list and return the new enemy
        self.enemies.append(enemy)
        return enemy

    def initialize_enemies(self):
        """Create initial enemies when the game starts"""
        # Start with 3 random enemies in random rooms
        for _ in range(3):
            # For initial enemies, use any room in any region
            all_rooms = self.world.get_all_room_names()
            if all_rooms:
                random_room = random.choice(all_rooms)
                region_name = None
                
                # Try to find which region this room belongs to
                for region_name, region in self.world.regions.items():
                    if random_room in region.rooms:
                        break
                
                # Spawn an appropriate enemy
                if region_name:
                    self.spawn_enemy_for_region(region_name, random_room)
                else:
                    # Fallback if region not found (shouldn't happen)
                    self.spawn_random_enemy()
                    
    def count_active_enemies(self):
        """Count the number of currently active (alive) enemies"""
        return sum(1 for enemy in self.enemies if enemy.is_alive())

    def spawn_enemy_for_region(self, region_name, room_name):
        """Spawn an enemy appropriate for a specific region"""
        if self.count_active_enemies() >= self.max_active_enemies:
            return None
        
        # Get appropriate enemy types for this region
        appropriate_enemies = self.region_enemies.get(region_name, [])
        
        if not appropriate_enemies:
            # If no region-specific enemies or unknown region, use any enemy
            enemy_type = random.choice(list(self.enemy_types.keys()))
        else:
            # 80% chance to use region-appropriate enemy, 20% chance for any enemy
            if random.random() < 0.8:
                enemy_type = random.choice(appropriate_enemies)
            else:
                enemy_type = random.choice(list(self.enemy_types.keys()))
        
        # Create the enemy
        enemy_data = self.enemy_types[enemy_type]
        enemy = Enemy(
            enemy_type,
            enemy_data["health"],
            enemy_data["attack"],
            enemy_data["experience"],
            enemy_data["allowed_rooms"],
            enemy_data["respawn_delay"]
        )
        
        # Override the current_room to ensure it spawns in the desired room
        enemy.current_room = room_name
        
        # Add to list and return the new enemy
        self.enemies.append(enemy)
        return enemy
    
    def get_enemies_in_room(self, room_name):
        """Get all living enemies in a specific room"""
        return [enemy for enemy in self.enemies if enemy.is_alive() and enemy.current_room == room_name]

    def get_enemy_by_name_in_room(self, name, room_name):
        """Find a specific enemy by name in a room, with improved partial matching"""
        name = name.lower()
        enemies = self.get_enemies_in_room(room_name)
        
        # First check for exact match
        for enemy in enemies:
            if enemy.name.lower() == name:
                return enemy
        
        # Check for full word match (e.g., "goblin" matches "goblin warrior")
        for enemy in enemies:
            if name in enemy.name.lower().split():
                return enemy
                
        # Then check for partial match anywhere in the name
        best_match = None
        best_score = float('inf')  # Lower is better
        
        for enemy in enemies:
            if name in enemy.name.lower():
                # Score based on how close the length is to the search term
                score = len(enemy.name) - len(name)
                if score < best_score:
                    best_match = enemy
                    best_score = score
        
        # If we found a partial match, return it
        if best_match:
            return best_match
                    
        return None

    # Add the static method for accessing enemies from other modules
    @classmethod
    def get_enemies_in_room_static(cls, room_name):
        """Static method to get enemies in a room (for use in other modules)"""
        if cls._active_instance:
            return cls._active_instance.get_enemies_in_room(room_name)
        return []
    
    # Add the update method to the EnemyManager class

    def update(self, game_state):
        """Update all enemies and potentially spawn new ones"""
        # Check for respawns and movement for existing enemies
        self.update_existing_enemies(game_state)
        
        # Clean up long-dead enemies
        self.clean_up_dead_enemies()
        
        # Check if we should spawn new enemies
        new_enemy = self.check_spawns(game_state)
        if new_enemy and new_enemy.current_room == game_state.current_room:
            # Notify player about the new enemy
            game_state.add_to_history(f"A {new_enemy.name} appears!", game_state.ENEMY_COLOR)

    def update_existing_enemies(self, game_state):
        """Update all existing enemies (movement, respawn, etc)"""
        current_time = time.time()
        
        for enemy in self.enemies:
            # Check for enemy respawns
            if not enemy.is_alive():
                if enemy.check_respawn() and enemy.current_room == game_state.current_room:
                    # Only notify if respawn happens in player's room
                    game_state.add_to_history(f"A {enemy.name} appears!", game_state.ENEMY_COLOR)
                continue
                
            # Check if it's time for this enemy to move
            if current_time - enemy.last_move_time >= GameConfig.ENEMY_MOVE_INTERVAL:
                # Calculate movement probability based on enemy type
                # More aggressive enemies move more often
                aggressiveness = 0.7  # Base 70% chance to move
                
                # Adjust based on enemy type
                if "goblin" in enemy.name or "orc" in enemy.name:
                    aggressiveness += 0.1  # More active
                elif "slime" in enemy.name or "zombie" in enemy.name:
                    aggressiveness -= 0.2  # Sluggish
                    
                # Use calculate_chance to get final movement probability
                move_chance = calculate_chance(aggressiveness, [])
                
                if random.random() < move_chance:  # Check if enemy should move
                    old_room = enemy.current_room
                    
                    # Get the direction of the move (for player notification)
                    direction = None
                    if enemy.move():
                        # Find which direction was taken to get to the new room
                        old_room_data = game_state.world.get_room(old_room)
                        if old_room_data and "exits" in old_room_data:
                            for exit_dir, exit_room in old_room_data["exits"].items():
                                if exit_room == enemy.current_room:
                                    direction = exit_dir
                                    break
                    
                    # Notify player if enemy leaves or enters their room
                    if old_room == game_state.current_room and enemy.current_room != game_state.current_room:
                        if direction:
                            game_state.add_to_history(f"The {enemy.name} leaves to the {direction}.", game_state.ENEMY_COLOR)
                        else:
                            game_state.add_to_history(f"The {enemy.name} leaves the area.", game_state.ENEMY_COLOR)
                    elif old_room != game_state.current_room and enemy.current_room == game_state.current_room:
                        # Find which direction the enemy came from
                        from_direction = None
                        current_room_data = game_state.world.get_room(game_state.current_room)
                        if current_room_data and "exits" in current_room_data:
                            for exit_dir, exit_room in current_room_data["exits"].items():
                                if exit_room == old_room:
                                    from_direction = exit_dir
                                    break
                        
                        if from_direction:
                            game_state.add_to_history(f"A {enemy.name} arrives from the {from_direction}!", game_state.ENEMY_COLOR)
                        else:
                            game_state.add_to_history(f"A {enemy.name} appears in the area!", game_state.ENEMY_COLOR)
                        
                # Random chance for enemies in the same room to attack the player
                if enemy.current_room == game_state.current_room:
                    # Calculate attack chance based on enemy temperament
                    base_attack_chance = 0.4  # 40% base chance to attack
                    
                    # Adjust based on enemy type
                    attack_modifiers = []
                    
                    if "goblin" in enemy.name or "orc" in enemy.name:
                        attack_modifiers.append(0.2)  # More aggressive
                    elif "slime" in enemy.name:
                        attack_modifiers.append(-0.1)  # Less aggressive
                    
                    # Use calculate_chance to get final attack probability
                    attack_chance = calculate_chance(base_attack_chance, attack_modifiers)
                    
                    if random.random() < attack_chance:  # Check if enemy attacks
                        damage = max(1, enemy.attack - game_state.player.defense_power())
                        game_state.player.take_damage(damage)
                        game_state.add_to_history(f"The {enemy.name} attacks you for {damage} damage!", game_state.COMBAT_COLOR)
                        
                        # Check if player died
                        if game_state.player.health <= 0:
                            game_state.add_to_history("You have been defeated! Game over.", game_state.COMBAT_COLOR)
                            game_state.game_over = True
                            
                enemy.last_move_time = current_time

    def clean_up_dead_enemies(self):
        """Remove dead enemies that have been dead for too long"""
        current_time = time.time()
        to_remove = []
        
        for i, enemy in enumerate(self.enemies):
            if not enemy.is_alive() and enemy.death_time is not None:
                # If it's been dead for more than 5 minutes, remove it completely
                if current_time - enemy.death_time > 300:  # 5 minutes
                    to_remove.append(i)
        
        # Remove enemies (in reverse order to maintain indices)
        for i in sorted(to_remove, reverse=True):
            del self.enemies[i]