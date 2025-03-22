from entities.enemy import Enemy
import random
import time

class RegionalEnemyManager:
    """Enhanced enemy manager that supports region-specific enemy spawns with level ranges"""
    def __init__(self, world):
        self.world = world
        self.enemies = []
        self.max_active_enemies = 5
        self.last_spawn_time = time.time()
        self.spawn_interval = 2  # Seconds between spawn checks
        self.game_state = None
        
        # Define enemy templates by region
        self.regional_enemies = {
            # Shadowed Depths (Level 1-3)
            "cave_system": {
                "bat": {
                    "level_range": (1, 2),
                    "health": (8, 12),  # (min, max) based on level
                    "attack": (2, 4),
                    "experience": (3, 5),
                    "spawn_weight": 35,  # Higher = more common
                    "respawn_delay": 15,
                    "drops": {
                        "common": [("coin", 1, 3, 0.8), ("bat_wing", 1, 1, 0.5)],
                        "uncommon": [("echo_crystal", 1, 1, 0.05)]
                    }
                },
                "rat": {
                    "level_range": (1, 2),
                    "health": (10, 15),
                    "attack": (3, 5),
                    "experience": (4, 6),
                    "spawn_weight": 30,
                    "respawn_delay": 20,
                    "drops": {
                        "common": [("coin", 1, 4, 0.7), ("rat_tail", 1, 1, 0.6)],
                        "uncommon": [("disease_cure", 1, 1, 0.03)]
                    }
                },
                "spider": {
                    "level_range": (1, 3),
                    "health": (12, 18),
                    "attack": (3, 6),
                    "experience": (5, 8),
                    "spawn_weight": 25,
                    "respawn_delay": 30,
                    "special_attacks": {
                        "poison": {
                            "chance": 0.3,
                            "duration": 30,
                            "strength": 1,
                            "message": "The spider's fangs inject venom into your bloodstream!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 1, 3, 0.6), ("spider_silk", 1, 1, 0.7)],
                        "uncommon": [("poison_sac", 1, 1, 0.08)]
                    }
                },
                "weak_goblin": {
                    "level_range": (2, 3),
                    "health": (15, 20),
                    "attack": (4, 6),
                    "experience": (6, 9),
                    "spawn_weight": 15,
                    "respawn_delay": 45,
                    "drops": {
                        "common": [("coin", 2, 6, 0.9), ("stick", 1, 1, 0.4)],
                        "uncommon": [("common_box_key", 1, 1, 0.1)]
                    }
                }
            },
            
            # Goblin Territory (Level 3-5)
            "goblin_territory": {
                "goblin_warrior": {
                    "level_range": (3, 4),
                    "health": (25, 35),
                    "attack": (6, 8),
                    "experience": (8, 12),
                    "spawn_weight": 30,
                    "respawn_delay": 50,
                    "drops": {
                        "common": [("coin", 3, 8, 0.9), ("rusty_sword", 1, 1, 0.2)],
                        "uncommon": [("common_treasure_box", 1, 1, 0.08)]
                    }
                },
                "goblin_archer": {
                    "level_range": (3, 5),
                    "health": (20, 30),
                    "attack": (7, 10),
                    "experience": (9, 14),
                    "spawn_weight": 25,
                    "respawn_delay": 55,
                    "special_attacks": {
                        "ranged": {
                            "chance": 0.4,
                            "damage_mult": 1.5,
                            "message": "The goblin archer fires an arrow from a distance!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 2, 7, 0.8), ("crude_bow", 1, 1, 0.15)],
                        "uncommon": [("uncommon_box_key", 1, 1, 0.1)]
                    }
                },
                "goblin_shaman": {
                    "level_range": (4, 5),
                    "health": (18, 25),
                    "attack": (5, 8),
                    "experience": (10, 15),
                    "spawn_weight": 15,
                    "respawn_delay": 60,
                    "special_attacks": {
                        "magic": {
                            "chance": 0.3,
                            "damage_mult": 1.8,
                            "message": "The goblin shaman casts a painful curse at you!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 5, 12, 0.9), ("mana_crystal", 1, 1, 0.3)],
                        "uncommon": [("shaman_staff", 1, 1, 0.12), ("rare_box_key", 1, 1, 0.05)]
                    }
                },
                "dire_wolf": {
                    "level_range": (4, 5),
                    "health": (30, 40),
                    "attack": (8, 12),
                    "experience": (12, 18),
                    "spawn_weight": 20,
                    "respawn_delay": 65,
                    "special_attacks": {
                        "rend": {
                            "chance": 0.25,
                            "bleed_damage": 2,
                            "bleed_duration": 20,
                            "message": "The dire wolf's fangs tear at your flesh, causing you to bleed!"
                        }
                    },
                    "drops": {
                        "common": [("wolf_pelt", 1, 1, 0.8), ("wolf_fang", 1, 2, 0.6)],
                        "uncommon": [("alpha_pelt", 1, 1, 0.1)]
                    }
                }
            },
            
            # Fungal Grottos (Level 5-7)
            "fungal_grottos": {
                "slime": {
                    "level_range": (5, 6),
                    "health": (35, 45),
                    "attack": (7, 10),
                    "experience": (12, 18),
                    "spawn_weight": 30,
                    "respawn_delay": 35,
                    "special_attacks": {
                        "split": {
                            "chance": 0.2,
                            "health_threshold": 0.3,  # Split at 30% health
                            "message": "The slime splits into two smaller slimes!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 3, 8, 0.7), ("slime_residue", 1, 2, 0.8)],
                        "uncommon": [("reactive_gel", 1, 1, 0.15)]
                    }
                },
                "myconid": {
                    "level_range": (5, 6),
                    "health": (30, 40),
                    "attack": (8, 12),
                    "experience": (15, 20),
                    "spawn_weight": 25,
                    "respawn_delay": 45,
                    "special_attacks": {
                        "spore_cloud": {
                            "chance": 0.3,
                            "damage_mult": 0.8,
                            "confusion_chance": 0.5,
                            "message": "The myconid releases a cloud of disorienting spores!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 4, 10, 0.8), ("mushroom_cap", 1, 2, 0.7)],
                        "uncommon": [("rare_spores", 1, 1, 0.2)]
                    }
                },
                "fungal_shambler": {
                    "level_range": (6, 7),
                    "health": (45, 55),
                    "attack": (10, 14),
                    "experience": (18, 25),
                    "spawn_weight": 20,
                    "respawn_delay": 60,
                    "special_attacks": {
                        "regeneration": {
                            "chance": 0.25,
                            "heal_amount": 5,
                            "message": "The fungal shambler's wounds begin to close rapidly!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 5, 12, 0.9), ("sturdy_fungus", 1, 1, 0.6)],
                        "uncommon": [("regenerative_spores", 1, 1, 0.15)],
                        "rare": [("rare_box_key", 1, 1, 0.08)]
                    }
                }
            },
            
            # Dwarven Ruins (Level 7-10)
            "dwarven_ruins": {
                "animated_armor": {
                    "level_range": (7, 8),
                    "health": (50, 60),
                    "attack": (12, 16),
                    "experience": (20, 28),
                    "spawn_weight": 25,
                    "respawn_delay": 70,
                    "drops": {
                        "common": [("coin", 8, 15, 0.9), ("metal_scrap", 1, 3, 0.7)],
                        "uncommon": [("dwarven_helmet", 1, 1, 0.12)]
                    }
                },
                "stone_guardian": {
                    "level_range": (8, 9),
                    "health": (65, 80),
                    "attack": (14, 18),
                    "experience": (25, 35),
                    "spawn_weight": 20,
                    "respawn_delay": 90,
                    "special_attacks": {
                        "ground_slam": {
                            "chance": 0.3,
                            "damage_mult": 1.4,
                            "stun_chance": 0.4,
                            "message": "The stone guardian slams the ground, sending shockwaves in all directions!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 10, 20, 0.95), ("stone_fragment", 1, 3, 0.8)],
                        "uncommon": [("dwarven_rune", 1, 1, 0.25)],
                        "rare": [("dwarven_shield", 1, 1, 0.08)]
                    }
                },
                "mechanical_construct": {
                    "level_range": (9, 10),
                    "health": (70, 85),
                    "attack": (16, 20),
                    "experience": (30, 40),
                    "spawn_weight": 15,
                    "respawn_delay": 120,
                    "special_attacks": {
                        "gear_throw": {
                            "chance": 0.25,
                            "damage_mult": 1.6,
                            "message": "The mechanical construct launches razor-sharp gears at you!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 15, 25, 0.95), ("gear", 1, 3, 0.7)],
                        "uncommon": [("rare_metal", 1, 1, 0.3)],
                        "rare": [("epic_box_key", 1, 1, 0.05)]
                    }
                }
            },
            
            # Crystal Caverns (Level 10-12)
            "crystal_caverns": {
                "crystal_elemental": {
                    "level_range": (10, 11),
                    "health": (80, 95),
                    "attack": (18, 22),
                    "experience": (35, 45),
                    "spawn_weight": 30,
                    "respawn_delay": 100,
                    "special_attacks": {
                        "crystal_shard": {
                            "chance": 0.35,
                            "damage_mult": 1.5,
                            "message": "The crystal elemental launches deadly shards in all directions!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 15, 30, 0.9), ("crystal_shard", 1, 3, 0.7)],
                        "uncommon": [("energy_crystal", 1, 1, 0.3)],
                        "rare": [("resonating_crystal", 1, 1, 0.08)]
                    }
                },
                "phase_spider": {
                    "level_range": (10, 12),
                    "health": (75, 90),
                    "attack": (20, 25),
                    "experience": (40, 50),
                    "spawn_weight": 25,
                    "respawn_delay": 110,
                    "special_attacks": {
                        "phase_shift": {
                            "chance": 0.3,
                            "dodge_chance": 0.8,
                            "message": "The phase spider briefly shifts out of reality, becoming intangible!"
                        },
                        "poison": {
                            "chance": 0.25,
                            "duration": 45,
                            "strength": 3,
                            "message": "The phase spider's fangs inject a glowing venom into your veins!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 20, 35, 0.9), ("phase_silk", 1, 2, 0.6)],
                        "uncommon": [("phase_crystal", 1, 1, 0.25)],
                        "rare": [("displacement_orb", 1, 1, 0.07)]
                    }
                },
                "crystal_guardian": {
                    "level_range": (11, 12),
                    "health": (100, 120),
                    "attack": (22, 28),
                    "experience": (50, 60),
                    "spawn_weight": 15,
                    "respawn_delay": 150,
                    "special_attacks": {
                        "energy_beam": {
                            "chance": 0.3,
                            "damage_mult": 2.0,
                            "message": "The crystal guardian focuses energy through its core, firing a devastating beam!"
                        },
                        "crystal_armor": {
                            "chance": 0.2,
                            "defense_bonus": 10,
                            "duration": 30,
                            "message": "Crystals form around the guardian, creating a protective shell!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 30, 50, 0.95), ("perfect_crystal", 1, 2, 0.5)],
                        "uncommon": [("energy_core", 1, 1, 0.3)],
                        "rare": [("guardian_crystal", 1, 1, 0.1)],
                        "legendary": [("legendary_box_key", 1, 1, 0.03)]
                    }
                }
            },
            
            # The Abyssal Rift (Level 12-15)
            "abyssal_rift": {
                "void_stalker": {
                    "level_range": (12, 13),
                    "health": (110, 130),
                    "attack": (25, 30),
                    "experience": (55, 70),
                    "spawn_weight": 30,
                    "respawn_delay": 120,
                    "special_attacks": {
                        "reality_tear": {
                            "chance": 0.3,
                            "damage_mult": 1.8,
                            "message": "The void stalker tears a hole in reality, unleashing chaotic energies!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 30, 60, 0.9), ("void_essence", 1, 2, 0.6)],
                        "uncommon": [("rift_stone", 1, 1, 0.3)],
                        "rare": [("reality_shard", 1, 1, 0.1)]
                    }
                },
                "aberration": {
                    "level_range": (13, 14),
                    "health": (130, 150),
                    "attack": (28, 35),
                    "experience": (65, 80),
                    "spawn_weight": 25,
                    "respawn_delay": 150,
                    "special_attacks": {
                        "mind_assault": {
                            "chance": 0.35,
                            "damage_mult": 1.5,
                            "confusion_chance": 0.7,
                            "message": "The aberration assaults your mind with impossible geometries and alien thoughts!"
                        },
                        "tentacle_swipe": {
                            "chance": 0.3,
                            "damage_mult": 1.7,
                            "message": "Multiple tentacles lash out from the aberration, striking from impossible angles!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 40, 70, 0.95), ("aberrant_tissue", 1, 3, 0.7)],
                        "uncommon": [("mutagen_vial", 1, 1, 0.25)],
                        "rare": [("alien_relic", 1, 1, 0.15)],
                        "legendary": [("legendary_box_key", 1, 1, 0.05)]
                    }
                },
                "mind_flayer": {
                    "level_range": (14, 15),
                    "health": (150, 180),
                    "attack": (32, 40),
                    "experience": (80, 100),
                    "spawn_weight": 15,
                    "respawn_delay": 240,
                    "special_attacks": {
                        "psychic_blast": {
                            "chance": 0.3,
                            "damage_mult": 2.2,
                            "message": "The mind flayer releases a devastating psychic blast that tears through your consciousness!"
                        },
                        "mind_control": {
                            "chance": 0.2,
                            "control_chance": 0.5,
                            "control_duration": 10,
                            "message": "The mind flayer attempts to seize control of your mind!"
                        },
                        "life_drain": {
                            "chance": 0.25,
                            "damage_mult": 1.3,
                            "heal_percent": 0.5,
                            "message": "The mind flayer drains your life force, healing itself!"
                        }
                    },
                    "drops": {
                        "common": [("coin", 50, 100, 0.95), ("brain_matter", 1, 2, 0.6)],
                        "uncommon": [("elder_idol", 1, 1, 0.35)],
                        "rare": [("mind_crystal", 1, 1, 0.2), ("forbidden_tome", 1, 1, 0.15)],
                        "legendary": [("reality_warper", 1, 1, 0.08), ("legendary_box_key", 1, 1, 0.1)]
                    }
                }
            }
        }
    
    def set_game_state(self, game_state):
        """Set a reference to the game state"""
        self.game_state = game_state
    
    def spawn_enemy_for_region(self, region_name, room_name):
        """Spawn an enemy appropriate for the specified region and player level"""
        if self.count_active_enemies() >= self.max_active_enemies:
            return None
        
        # Get region-specific enemy templates
        region_enemies = self.regional_enemies.get(region_name, {})
        if not region_enemies:
            return None
        
        # Get player level for level-appropriate spawns
        player_level = self.game_state.player.level if self.game_state else 1
        
        # Filter enemies by level range and create weighted list
        valid_enemies = []
        weights = []
        
        for enemy_type, enemy_data in region_enemies.items():
            level_min, level_max = enemy_data["level_range"]
            
            # Check if enemy is appropriate for player's level
            if level_min <= player_level <= level_max + 2:  # Allow spawning enemies slightly above player level
                valid_enemies.append((enemy_type, enemy_data))
                
                # Calculate weight - higher weight for enemies closer to player level
                level_diff = abs(player_level - (level_min + level_max) / 2)
                adjusted_weight = enemy_data["spawn_weight"] / (1 + level_diff)
                weights.append(adjusted_weight)
        
        if not valid_enemies:
            return None
        
        # Select an enemy type based on weights
        selected_enemy, enemy_data = random.choices(valid_enemies, weights=weights, k=1)[0]
        
        # Scale stats based on player level
        level_factor = min(1.0, player_level / enemy_data["level_range"][1])
        health_range = enemy_data["health"]
        attack_range = enemy_data["attack"]
        exp_range = enemy_data["experience"]
        
        health = int(health_range[0] + (health_range[1] - health_range[0]) * level_factor)
        attack = int(attack_range[0] + (attack_range[1] - attack_range[0]) * level_factor)
        experience = int(exp_range[0] + (exp_range[1] - exp_range[0]) * level_factor)
        
        # Create the enemy
        enemy = Enemy(
            name=selected_enemy,
            description=f"A dangerous {selected_enemy.replace('_', ' ')}.",
            health=health,
            attack=attack,
            defense=0,  # Default defense
            level=int((enemy_data["level_range"][0] + enemy_data["level_range"][1]) / 2)  # Approximate level
        )
        
        # Set experience and respawn delay
        enemy.experience = experience
        enemy.respawn_delay = enemy_data["respawn_delay"]
        
        # Set current room and allowed rooms
        enemy.current_room = room_name
        enemy.allowed_rooms = [room_name]
        
        # Add special attacks if any
        if "special_attacks" in enemy_data:
            enemy.special_attacks = enemy_data["special_attacks"]
        
        # Add drops information
        if "drops" in enemy_data:
            enemy.drops = enemy_data["drops"]
        
        # Add to list and return the new enemy
        self.enemies.append(enemy)
        return enemy
    
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
            base_chance = 0.05  # 5% base chance per check (adjustable)
            modified_chance = min(0.2, base_chance * spawn_rate_modifier)  # Cap at 20%
            
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
    
    def count_active_enemies(self):
        """Count the number of currently active (alive) enemies"""
        return sum(1 for enemy in self.enemies if enemy.is_alive())
    
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
            if name in enemy.name.lower().split('_'):
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
        
        return best_match
    
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
            game_state.add_to_history(f"A {new_enemy.name.replace('_', ' ')} appears!", game_state.ENEMY_COLOR)
    
    def update_existing_enemies(self, game_state):
        """Update all existing enemies (movement, respawn, etc.)"""
        current_time = time.time()
        
        for enemy in self.enemies:
            # Check for enemy respawns
            if not enemy.is_alive():
                if self.check_respawn(enemy, current_time) and enemy.current_room == game_state.current_room:
                    # Only notify if respawn happens in player's room
                    game_state.add_to_history(f"A {enemy.name.replace('_', ' ')} appears!", game_state.ENEMY_COLOR)
                continue
                
            # Check if it's time for this enemy to move
            if self.should_move(enemy, current_time):
                # Calculate movement probability based on enemy type
                # More aggressive enemies move more often
                aggressiveness = 0.5  # Base 50% chance to move
                
                # Adjust based on enemy type
                if "goblin" in enemy.name or "wolf" in enemy.name or "stalker" in enemy.name:
                    aggressiveness += 0.2  # More active
                elif "slime" in enemy.name or "guardian" in enemy.name or "construct" in enemy.name:
                    aggressiveness -= 0.2  # More stationary
                    
                # Region difficulty increases movement chance
                region = game_state.world.get_region_for_room(enemy.current_room)
                if region:
                    aggressiveness += 0.05 * region.difficulty
                
                if random.random() < aggressiveness:  # Check if enemy should move
                    old_room = enemy.current_room
                    
                    # Get the player's room and check if enemy should move toward player
                    player_room = game_state.current_room
                    player_region = game_state.world.get_region_for_room(player_room)
                    enemy_region = game_state.world.get_region_for_room(enemy.current_room)
                    
                    # Enemies that are in same region as player are more likely to move toward player
                    move_toward_player = False
                    if player_region and enemy_region and player_region.name == enemy_region.name:
                        if "goblin" in enemy.name or "wolf" in enemy.name or "stalker" in enemy.name:
                            move_toward_player = random.random() < 0.7  # Aggressive
                        else:
                            move_toward_player = random.random() < 0.4  # Normal
                    
                    if move_toward_player:
                        self.move_toward_player(enemy, player_room, game_state)
                    else:
                        self.move_random(enemy, game_state)
                    
                    # Notify player if enemy leaves or enters their room
                    if old_room == game_state.current_room and enemy.current_room != game_state.current_room:
                        game_state.add_to_history(f"The {enemy.name.replace('_', ' ')} leaves the area.", game_state.ENEMY_COLOR)
                    elif old_room != game_state.current_room and enemy.current_room == game_state.current_room:
                        game_state.add_to_history(f"A {enemy.name.replace('_', ' ')} enters the area!", game_state.ENEMY_COLOR)
                
                # Enemies in the same room as player might attack
                if enemy.current_room == game_state.current_room:
                    # Calculate attack chance based on enemy aggressiveness
                    base_attack_chance = 0.2  # 20% base chance to attack
                    
                    # Adjust based on enemy type and region difficulty
                    attack_modifiers = []
                    
                    if "goblin" in enemy.name or "wolf" in enemy.name or "stalker" in enemy.name:
                        attack_modifiers.append(0.15)  # More aggressive
                    elif "spider" in enemy.name or "archer" in enemy.name or "phase" in enemy.name:
                        attack_modifiers.append(0.1)  # Slightly more aggressive
                    elif "slime" in enemy.name or "guardian" in enemy.name:
                        attack_modifiers.append(-0.1)  # Less aggressive
                    
                    # Region difficulty increases attack chance
                    region = game_state.world.get_region_for_room(enemy.current_room)
                    if region:
                        attack_modifiers.append(0.03 * region.difficulty)
                    
                    # Calculate final attack chance
                    attack_chance = base_attack_chance
                    for modifier in attack_modifiers:
                        attack_chance += modifier
                    
                    # Cap between 10-50%
                    attack_chance = max(0.1, min(0.5, attack_chance))
                    
                    if random.random() < attack_chance:  # Check if enemy attacks
                        self.perform_enemy_attack(enemy, game_state)
            
            # Update last move time
            enemy.last_move_time = current_time
    
    def perform_enemy_attack(self, enemy, game_state):
        """Enemy attacks the player outside of formal combat"""
        # Check if player is in the same room
        if enemy.current_room != game_state.current_room:
            return
        
        # Get environment effects that might affect enemy accuracy
        env_system = game_state.get_current_environment_system()
        env_effects = {}
        if env_system:
            env_effects = env_system.get_effects(game_state.current_room)
        
        # Calculate hit chance (base 70%)
        hit_chance = 0.7
        enemy_accuracy_mod = env_effects.get("enemy_accuracy", 0)
        hit_chance += enemy_accuracy_mod / 10  # Convert to percentage
        hit_chance = max(0.4, min(0.9, hit_chance))  # Clamp between 40% and 90%
        
        # Player dodge chance (base 15%)
        dodge_chance = 0.15
        
        # Roll for hit
        if random.random() < dodge_chance:
            game_state.add_to_history(f"You dodge the {enemy.name.replace('_', ' ')}'s attack!", game_state.COMBAT_COLOR)
            return
            
        if random.random() < hit_chance:
            # Determine if this is a special attack
            special_attack = None
            
            if hasattr(enemy, 'special_attacks') and enemy.special_attacks:
                for effect_name, effect_data in enemy.special_attacks.items():
                    if random.random() < effect_data.get("chance", 0):
                        special_attack = (effect_name, effect_data)
                        break
            
            # Calculate damage
            if special_attack:
                self.perform_special_attack(enemy, special_attack, game_state)
            else:
                self.perform_normal_attack(enemy, game_state)
        else:
            game_state.add_to_history(f"The {enemy.name.replace('_', ' ')} attacks but misses!", game_state.ENEMY_COLOR)
    
    def perform_normal_attack(self, enemy, game_state):
        """Process a normal enemy attack"""
        player = game_state.player
        
        # Calculate base damage
        base_damage = random.randint(
            max(1, enemy.attack - 2),
            enemy.attack + 2
        )
        
        # Apply player defense
        final_damage = max(1, base_damage - player.defense_power())
        actual_damage = player.take_damage(final_damage)
        
        # Display damage message
        game_state.add_to_history(f"The {enemy.name.replace('_', ' ')} attacks you for {actual_damage} damage!", game_state.ENEMY_COLOR)
        game_state.add_to_history(f"Your health: {player.health}/{player.max_health}", game_state.HEALTH_COLOR)
        
        # Check if player died
        if player.health <= 0:
            game_state.add_to_history("You have been defeated! Game over.", game_state.COMBAT_COLOR)
            game_state.game_over = True
    
    def perform_special_attack(self, enemy, special_attack, game_state):
        """Process a special attack from an enemy"""
        player = game_state.player
        attack_name, attack_data = special_attack
        
        # Calculate base damage
        base_damage = random.randint(
            max(1, enemy.attack - 2),
            enemy.attack + 2
        )
        
        # Process based on attack type
        if attack_name == "poison":
            # Apply message first
            message = attack_data.get("message", f"The {enemy.name.replace('_', ' ')} poisons you!")
            game_state.add_to_history(message, (0, 180, 0))
            
            # Create and apply poison effect if status system is available
            if hasattr(game_state, 'status_effect_manager'):
                from systems.status_effects.status_effects import PoisonEffect
                poison = PoisonEffect(
                    duration=attack_data.get("duration", 30),
                    strength=attack_data.get("strength", 1)
                )
                game_state.status_effect_manager.add_effect(poison)
            
            # Apply some direct damage too
            final_damage = max(1, base_damage - player.defense_power())
            actual_damage = player.take_damage(final_damage)
            game_state.add_to_history(f"You take {actual_damage} damage from the attack!", game_state.ENEMY_COLOR)
            
        elif attack_name == "ranged":
            # Ranged attack with damage multiplier
            damage_mult = attack_data.get("damage_mult", 1.2)
            modified_damage = int(base_damage * damage_mult)
            final_damage = max(1, modified_damage - player.defense_power())
            actual_damage = player.take_damage(final_damage)
            
            # Display message
            message = attack_data.get("message", f"The {enemy.name.replace('_', ' ')} attacks from a distance!")
            game_state.add_to_history(message, game_state.ENEMY_COLOR)
            game_state.add_to_history(f"You take {actual_damage} damage!", game_state.ENEMY_COLOR)
            
        elif attack_name == "magic":
            # Magic attack with damage multiplier
            damage_mult = attack_data.get("damage_mult", 1.5)
            modified_damage = int(base_damage * damage_mult)
            final_damage = max(1, modified_damage - player.defense_power())
            actual_damage = player.take_damage(final_damage)
            
            # Display message
            message = attack_data.get("message", f"The {enemy.name.replace('_', ' ')} casts a spell at you!")
            game_state.add_to_history(message, game_state.ENEMY_COLOR)
            game_state.add_to_history(f"You take {actual_damage} damage!", game_state.ENEMY_COLOR)
            
        elif attack_name == "rend":
            # Apply bleeding effect if status system is available
            if hasattr(game_state, 'status_effect_manager'):
                try:
                    # Try to import bleeding effect
                    from systems.status_effects.bleeding_effect import BleedingEffect
                    bleed = BleedingEffect(
                        duration=attack_data.get("bleed_duration", 20),
                        strength=attack_data.get("bleed_damage", 1)
                    )
                    game_state.status_effect_manager.add_effect(bleed)
                except ImportError:
                    # Fallback if specific module not available
                    pass
            
            # Apply some direct damage
            final_damage = max(1, base_damage - player.defense_power())
            actual_damage = player.take_damage(final_damage)
            
            # Display message
            message = attack_data.get("message", f"The {enemy.name.replace('_', ' ')} tears at your flesh!")
            game_state.add_to_history(message, game_state.ENEMY_COLOR)
            game_state.add_to_history(f"You take {actual_damage} damage and start bleeding!", game_state.ENEMY_COLOR)
            
        else:
            # Default for unknown special attacks
            final_damage = max(1, base_damage - player.defense_power())
            actual_damage = player.take_damage(final_damage)
            
            # Display generic message
            message = f"The {enemy.name.replace('_', ' ')} uses a special attack!"
            game_state.add_to_history(message, game_state.ENEMY_COLOR)
            game_state.add_to_history(f"You take {actual_damage} damage!", game_state.ENEMY_COLOR)
        
        # Display health
        game_state.add_to_history(f"Your health: {player.health}/{player.max_health}", game_state.HEALTH_COLOR)
        
        # Check if player died
        if player.health <= 0:
            game_state.add_to_history("You have been defeated! Game over.", game_state.COMBAT_COLOR)
            game_state.game_over = True
    
    def check_respawn(self, enemy, current_time=None):
        """Check if an enemy should respawn"""
        if enemy.is_alive():
            return False
            
        if current_time is None:
            current_time = time.time()
            
        # Check if enough time has passed
        if enemy.death_time is None or current_time - enemy.death_time < enemy.respawn_delay:
            return False
            
        # Reset health and status
        enemy.health = enemy.max_health
        enemy.is_alive_flag = True
        
        return True
    
    def should_move(self, enemy, current_time=None):
        """Check if an enemy should move based on time and type"""
        if not enemy.is_alive():
            return False
            
        if current_time is None:
            current_time = time.time()
            
        # Base move interval depends on enemy type
        interval = 15  # Default interval
        
        # Adjust interval based on enemy type
        if "goblin" in enemy.name or "wolf" in enemy.name or "stalker" in enemy.name:
            interval = 10  # More active
        elif "guardian" in enemy.name or "slime" in enemy.name:
            interval = 20  # More stationary
        
        # Check time since last move
        return (current_time - enemy.last_move_time) >= interval
    
    def move_toward_player(self, enemy, player_room, game_state):
        """Try to move enemy toward the player's room"""
        # This is a simplified implementation. In a full game, you'd use pathfinding.
        # For now, we'll just check if the player's room is directly connected.
        
        current_room = enemy.current_room
        room_data = game_state.world.get_room(current_room)
        
        if not room_data or "exits" not in room_data:
            return False
        
        # Check if any exit leads to player's room
        for direction, destination in room_data["exits"].items():
            if destination == player_room:
                enemy.current_room = player_room
                return True
        
        # If no direct path, move randomly
        return self.move_random(enemy, game_state)
    
    def move_random(self, enemy, game_state):
        """Move enemy to a random connected room"""
        current_room = enemy.current_room
        room_data = game_state.world.get_room(current_room)
        
        if not room_data or "exits" not in room_data:
            return False
        
        # Get available exits
        available_exits = []
        for direction, destination in room_data["exits"].items():
            # Skip locked exits
            dest_room = game_state.world.get_room(destination)
            if dest_room and dest_room.get("locked", False):
                continue
            available_exits.append(destination)
        
        if not available_exits:
            return False
        
        # Pick a random destination
        enemy.current_room = random.choice(available_exits)
        return True
    
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