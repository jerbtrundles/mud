# game_state.py
import textwrap
import random
import time
from systems.shop import ShopSystem
from items.item_factory import ItemFactory
from systems.crafting import CraftingSystem
from core.utils import get_weather_description, get_environment_effect_description, dice_roll, calculate_chance, clamp
from systems.journal import Journal
from systems.bestiary import Bestiary
from systems.status_effects.status_effect_manager import StatusEffectManager

# Colors for text
TEXT_COLOR = (200, 200, 200)
TITLE_COLOR = (255, 255, 100)
ENEMY_COLOR = (255, 100, 100)
COMBAT_COLOR = (255, 165, 0)
HEALTH_COLOR = (100, 255, 100)
INPUT_COLOR = (100, 255, 100)

class GameState:
    def __init__(self, world, player):
        self.world = world
        self.player = player
        self.current_room = "entrance"
        self.game_history = []
        self.game_over = False
        self.coins = 0
        self.shop_system = ShopSystem()
        self.crafting_system = CraftingSystem()
        self.game_time = time.time()
        self.enemy_manager = None
        self.journal = Journal(self)
        self.bestiary = Bestiary(self)
        self.status_effect_manager = StatusEffectManager(self)

        # Add public access to colors for enemy manager
        self.TITLE_COLOR = TITLE_COLOR
        self.ENEMY_COLOR = ENEMY_COLOR
        self.COMBAT_COLOR = COMBAT_COLOR
        self.HEALTH_COLOR = HEALTH_COLOR
        
        # Add game introduction
        self.add_to_history("MINIMUD: A TEXT RPG ADVENTURE", TITLE_COLOR)
        self.add_to_history("Type 'help' to see available commands.", INPUT_COLOR)
        self.add_to_history("")

        from systems.quest_manager import QuestManager
        self.quest_manager = QuestManager(self)
    
    def get_game_time(self):
        """Get the current game time"""
        return time.time()
    
    def add_to_history(self, text, color=TEXT_COLOR):
        # Split text into wrapped lines for display
        if text:
            wrapped_lines = textwrap.wrap(text, width=70)
            for line in wrapped_lines:
                self.game_history.append((line, color))
        else:
            self.game_history.append(("", color))  # Empty line
    
    def set_enemy_manager(self, enemy_manager):
        self.enemy_manager = enemy_manager

    def craft(self, item_name):
        """Craft an item using available ingredients"""
        success, message = self.crafting_system.craft_item(self, item_name)
        self.add_to_history(message)
        return success

    def debug_crafting(self):
        """Debug the crafting system"""
        self.crafting_system.debug_items(self)

    def show_recipes(self):
        """Display available crafting recipes"""
        self.crafting_system.display_recipes(self)

    def look(self):
        room = self.world.get_room(self.current_room)
        if not room:
            self.add_to_history("Something went wrong. You're in a void.")
            return
        
        # Get region information
        region = self.world.get_region_for_room(self.current_room)
        
        location_display = "["
        
        if region:
            location_display += f"{region.display_name} - "

        location_display += f"{self.current_room.replace('_', ' ').title()}]"

        self.add_to_history(location_display, TITLE_COLOR)
        self.add_to_history(room["description"])
        
        # Discover the region if this is the first visit
        if region and not region.discovered:
            region.discover()
            self.add_to_history(f"\nYou've discovered a new region: {region.display_name}!", (180, 180, 255))
            self.add_to_history(f"{region.description}", (180, 180, 255))
        
        # Environment description - get from the region's environment system
        if region:
            weather_desc = region.environment_system.get_weather_description(self.current_room)
            self.add_to_history(weather_desc, (100, 200, 255))
        
        # List exits
        exits = room.get("exits", {})
        if exits:
            exit_list = ", ".join(exits.keys())
            self.add_to_history(f"Exits: {exit_list}")
        else:
            self.add_to_history("There are no visible exits.")
        
        # Check if this is a shop
        if room.get("is_shop", False):
            self.shop_system.display_shop(self)
            return
        
        # List items
        items = room.get("items", [])
        if items:
            item_descriptions = []
            for item_name in items:
                item = ItemFactory.get_item(item_name)
                if item:
                    item_descriptions.append(item.display_name())
                else:
                    # Fallback for items not yet converted to the new system
                    item_descriptions.append(item_name.replace('_', ' '))
            
            item_list = ", ".join(item_descriptions)
            self.add_to_history(f"You see: {item_list}")
        
        # Check for enemies in the room
        if self.enemy_manager:
            enemies_in_room = self.enemy_manager.get_enemies_in_room(self.current_room)
            if enemies_in_room:
                self.add_to_history("\nCreatures in the area:", self.ENEMY_COLOR)
                for enemy in enemies_in_room:
                    self.add_to_history(f"- {enemy.name.capitalize()} (HP: {enemy.health}/{enemy.max_health})", self.ENEMY_COLOR)

    def go(self, direction):
        room = self.world.get_room(self.current_room)
        if not room:
            self.add_to_history("You can't go anywhere from the void.")
            return
        
        exits = room.get("exits", {})
        if direction not in exits:
            self.add_to_history(f"You can't go {direction} from here.")
            return
        
        # Check if the destination room is locked
        destination = exits[direction]
        dest_room = self.world.get_room(destination)
        
        if dest_room.get("locked", False):
            key_item = dest_room.get("key_item")
            if key_item and not self.player.has_item(key_item):
                self.add_to_history(f"The way is locked. You need something to unlock it.")
                return
            else:
                self.add_to_history(f"You use the {key_item.replace('_', ' ')} to unlock the way.")
        
        # Store previous room for region change checking
        previous_room = self.current_room
        previous_region = self.world.get_region_for_room(previous_room)
        
        # Update current room
        self.current_room = destination
        self.add_to_history(f"You go {direction}.")
        
        # Update quest progress for visiting locations
        self.quest_manager.update_quest_progress("visit", destination)
        
        # Update travel stats in journal
        self.journal.update_stats("distance_traveled")
        
        # Check if player entered a new region
        current_region = self.world.get_region_for_room(self.current_room)
        if current_region and current_region != previous_region:
            # Add journal entry about region transition
            if previous_region:
                self.journal.add_entry(
                    f"Left {previous_region.display_name} and entered {current_region.display_name}.", 
                    "travel"
                )
        
        # Look at the new room
        self.look()
    
    def buy(self, item_name):
        self.shop_system.process_buy(self, item_name)
    
    def sell(self, item_name):
        self.shop_system.process_sell(self, item_name)
    
    def check_coins(self):
        self.add_to_history(f"You have {self.coins} coins.")
        
    def take(self, item_text):
        """Take an item from the current room with improved partial matching"""
        # Convert to lowercase for case-insensitive matching
        item_text = item_text.lower()
        
        room = self.world.get_room(self.current_room)
        if not room:
            self.add_to_history("There's nothing to take in the void.")
            return
        
        # Special case for coins
        if item_text in ["coin", "coins", "money", "gold"]:
            self._take_coins(room)
            return
        
        # Match item to a real item in the room
        items = room.get("items", [])
        
        # Try to find which item the player wants
        if not items:
            self.add_to_history(f"There's nothing here to take.")
            return
            
        # Find the best matching item in the room
        found_item = None
        best_score = float('inf')  # Lower is better
        
        # First check for exact match on item name
        for item_name in items:
            if item_name.replace('_', ' ') == item_text:
                found_item = item_name
                break
                
        # If no exact match, try aliases and partial matches
        if not found_item:
            for item_name in items:
                item_obj = ItemFactory.get_item(item_name)
                if not item_obj:
                    continue
                    
                # Check for exact alias match
                for alias in item_obj.aliases:
                    if alias.lower() == item_text:
                        found_item = item_name
                        break
                        
                if found_item:
                    break
                    
            # If still no match, try partial matches on names and aliases
            if not found_item:
                for item_name in items:
                    item_obj = ItemFactory.get_item(item_name)
                    if not item_obj:
                        continue
                        
                    # Check partial match on name
                    if item_text in item_name.replace('_', ' '):
                        score = len(item_name) - len(item_text)
                        if score < best_score:
                            found_item = item_name
                            best_score = score
                            
                    # Check partial matches on aliases
                    for alias in item_obj.aliases:
                        if item_text in alias.lower():
                            score = len(alias) - len(item_text)
                            if score < best_score:
                                found_item = item_name
                                best_score = score
        
        # If found, take the item
        if found_item:
            self.player.add_to_inventory(found_item)
            items.remove(found_item)
            
            # Get the item object for a better message
            item_obj = ItemFactory.get_item(found_item)
            if item_obj:
                self.add_to_history(f"You take the {item_obj.display_name()}.")
            else:
                self.add_to_history(f"You take the {found_item.replace('_', ' ')}.")

            # Update quest progress for collecting items
            self.quest_manager.update_quest_progress("collect", found_item, self.current_room)
        else:
            self.add_to_history(f"There's no {item_text} here.")
    
    def _take_coins(self, room):
        """Helper method to handle taking coins"""
        items = room.get("items", [])
        coin_count = items.count("coin")
        
        if coin_count > 0:
            # Remove all coins from the room
            while "coin" in items:
                items.remove("coin")
                
            # Add coins to player's money
            random_bonus = random.randint(1, 3) if coin_count > 1 else 0
            total_coins = coin_count + random_bonus
            self.coins += total_coins
            
            if coin_count == 1:
                self.add_to_history(f"You picked up a coin. You now have {self.coins} coins.")
            else:
                self.add_to_history(f"You picked up {coin_count} coins. You now have {self.coins} coins.")
        else:
            self.add_to_history("There are no coins here.")
    
    def show_inventory(self):
        inventory_list = self.player.get_inventory_list()
        if not inventory_list:
            self.add_to_history("Your inventory is empty.")
        else:
            items = ", ".join(inventory_list)
            self.add_to_history(f"Inventory: {items}")
    
    # Update the use method in consumable.py to work with region-specific environment effects

    def use(self, game_state):
        """Use/consume the item with region-specific environment effects"""
        player = game_state.player
        message = []
        
        # Get the current region and its environment effects
        current_region = game_state.world.get_region_for_room(game_state.current_room)
        
        if current_region:
            # Get environmental effects from the region's environment system
            env_effects = current_region.environment_system.get_effects(game_state.current_room)
            healing_bonus = env_effects.get("healing_bonus", 1.0)  # Default multiplier of 1.0
        else:
            healing_bonus = 1.0  # No effects if no region found
        
        # Restore health if applicable, with environment bonus
        if self.health_restore > 0:
            base_heal = self.health_restore
            modified_heal = int(base_heal * healing_bonus)
            actual_heal = player.heal(modified_heal)
            
            # Mention the environmental bonus if significant
            if healing_bonus > 1.1:  # More than 10% bonus
                if current_region:
                    weather = current_region.environment_system.get_weather(game_state.current_room)
                    message.append(f"You consume the {self.display_name()} and recover {actual_heal} health points.")
                    message.append(f"The {weather} environment enhances the healing effect!")
                else:
                    message.append(f"You consume the {self.display_name()} and recover {actual_heal} health points.")
            else:
                message.append(f"You consume the {self.display_name()} and recover {actual_heal} health points.")
                
            message.append(f"Health: {player.health}/{player.max_health}")
        else:
            message.append(f"You consume the {self.display_name()}.")
        
        # Apply additional effects
        for effect, value in self.effects.items():
            if effect == "strength":
                # Example temp buff implementation
                player.temp_attack_bonus = value
                player.temp_buff_end_time = game_state.get_game_time() + self.effects.get("duration", 60)
                message.append(f"You feel stronger! +{value} to attack for {self.effects.get('duration', 60)} seconds.")
        
        return True, "\n".join(message)

    def equip(self, item_name):
        """Equip an item by name, supporting partial matches and aliases"""
        # Convert to lowercase for case-insensitive matching
        item_text = item_name.lower()
        
        # First, check directly in player's inventory
        best_match = None
        best_score = float('inf')  # Lower is better
        
        for inv_item in self.player.inventory:
            item = ItemFactory.get_item(inv_item)
            if not item:
                continue
                
            # Check exact name match
            if item.name.replace('_', ' ') == item_text:
                best_match = item.name
                break
                
            # Check alias matches
            if any(alias.lower() == item_text for alias in item.aliases):
                best_match = item.name
                break
                
            # Check partial name match
            if item_text in item.name.replace('_', ' '):
                score = len(item.name) - len(item_text)
                if score < best_score:
                    best_match = item.name
                    best_score = score
                    
            # Check partial alias matches
            for alias in item.aliases:
                if item_text in alias.lower():
                    score = len(alias) - len(item_text)
                    if score < best_score:
                        best_match = item.name
                        best_score = score
        
        actual_item_name = best_match
        
        # If still not found or player doesn't have the item
        if not actual_item_name or not self.player.has_item(actual_item_name):
            self.add_to_history(f"You don't have a {item_text}.")
            return
        
        item = ItemFactory.get_item(actual_item_name)
        if not item:
            self.add_to_history(f"You can't equip the {item_text}.")
            return
        
        # Try to equip as weapon
        if item.type == "weapon" and self.player.equip_weapon(actual_item_name):
            self.add_to_history(f"You equip the {item.display_name()} as your weapon.")
            self.add_to_history(f"Attack power increased to {self.player.attack_power()}.")
            return
        
        # Try to equip as armor
        if item.type == "armor" and self.player.equip_armor(actual_item_name):
            self.add_to_history(f"You equip the {item.display_name()} as your armor.")
            self.add_to_history(f"Defense increased to {self.player.defense_power()}.")
            return
        
        # If we get here, item can't be equipped
        if item.type in ["weapon", "armor"]:
            self.add_to_history(f"You don't meet the requirements to equip the {item.display_name()}.")
        else:
            self.add_to_history(f"You can't equip the {item.display_name()}.")    
    
    def check_environment(self):
        """Display detailed information about the current environment"""
        environment_system = self.get_current_environment_system()
        if not environment_system:
            self.add_to_history("You can't determine anything special about the environment.")
            return
                
        weather = environment_system.get_weather(self.current_room)
        weather_data = environment_system.weather_types.get(weather)
        
        if not weather_data:
            self.add_to_history("You can't determine anything special about the environment.")
            return
                
        self.add_to_history("Environment Analysis:", (100, 200, 255))
        
        # Get weather intensity (you could track this in the environment system)
        weather_intensity = 1.0
        region = self.world.get_region_for_room(self.current_room)
        if region:
            weather_bias = region.get_environment_bias()
            if weather in weather_bias:
                weather_intensity = weather_bias[weather]
        
        # Use utility function to generate weather description
        weather_desc = get_weather_description(weather, weather_intensity)
        self.add_to_history(weather_desc, (100, 200, 255))
        
        # Describe effects based on character knowledge/perception
        effects = weather_data["effects"]
        if not effects:
            self.add_to_history("This environment doesn't seem to have any notable effects.")
        else:
            self.add_to_history("You notice:", (100, 200, 255))
            
            for effect_name, value in effects.items():
                effect_desc = get_environment_effect_description(effect_name, value)
                if effect_desc:
                    self.add_to_history(f"- {effect_desc}")

        def combat(self, enemy):
            """
            Enhanced combat system with critical hits, dodging, and special attacks
            
            Args:
                enemy: The enemy being fought
                
            Returns:
                str: Combat result message or None
            """
            if not enemy.is_alive():
                return f"The {enemy.name} is already defeated."
            
            # Get the current region and its environment effects
            current_region = self.world.get_region_for_room(self.current_room)
            
            if current_region:
                # Get environmental effects from the region's environment system
                env_effects = current_region.environment_system.get_effects(self.current_room)
            else:
                env_effects = {}  # No effects if no region found
            
            # Track combat stats
            total_damage_dealt = 0
            total_damage_taken = 0
            critical_hits = 0
            dodges = 0
            
            # Store original health percentage (for drop calculation)
            original_health_pct = enemy.health / enemy.max_health if enemy.max_health > 0 else 0
            
            # === PLAYER ATTACK PHASE ===
            
            # Calculate base hit chance (default 90%)
            player_hit_chance = 0.9
            
            # Apply modifiers from equipment and environment
            # Equipment could add to hit chance (not implemented yet)
            # Environmental effects can reduce hit chance 
            if "player_accuracy" in env_effects:
                player_hit_chance += env_effects["player_accuracy"] / 10  # Convert to percentage modifier
                
            # Cap hit chance between 50% and 99%
            player_hit_chance = max(0.5, min(0.99, player_hit_chance))
            
            # Roll to hit
            if random.random() < player_hit_chance:
                # Hit succeeded! Now determine if it's a critical hit
                crit_chance = 0.05  # Base 5% chance
                
                # Crit chance could be modified by equipment, skills, etc.
                
                is_critical = random.random() < crit_chance
                
                # Calculate base damage
                base_damage = random.randint(
                    max(1, self.player.attack_power() - 2),
                    self.player.attack_power() + 3
                )
                
                # Apply critical hit bonus if applicable
                if is_critical:
                    critical_hits += 1
                    base_damage = int(base_damage * 1.5)  # 50% more damage on crits
                    
                # Apply environmental modifiers to damage
                attack_modifier = env_effects.get("player_attack", 0)
                actual_damage = max(1, base_damage + attack_modifier)
                
                # Apply damage to enemy
                enemy.take_damage(actual_damage)
                total_damage_dealt += actual_damage
                
                # Generate hit message
                if is_critical:
                    self.add_to_history(f"You land a critical hit on the {enemy.name} for {actual_damage} damage!", (255, 100, 0))  # Bright orange for crits
                else:
                    self.add_to_history(f"You hit the {enemy.name} for {actual_damage} damage!", self.COMBAT_COLOR)
            else:
                # Player missed
                self.add_to_history(f"You swing at the {enemy.name} but miss!", self.COMBAT_COLOR)
            
            # Check if enemy was defeated
            if enemy.health <= 0:
                # Enemy defeated
                exp_gained = enemy.experience
                self.add_to_history(f"You have defeated the {enemy.name}!", self.COMBAT_COLOR)
                
                # Award experience
                leveled_up = self.player.gain_experience(exp_gained)
                self.add_to_history(f"You gain {exp_gained} experience points.", self.COMBAT_COLOR)

                if leveled_up:
                    self.add_to_history(f"You leveled up! You are now level {self.player.level}!", self.COMBAT_COLOR)
                    self.add_to_history(f"Your health has been restored to {self.player.health}.", self.HEALTH_COLOR)
                    
                    # Add journal entry for level up
                    self.journal.add_entry(f"Leveled up to level {self.player.level}!", "milestone")
                    
                    # Check for level-based achievements
                    if self.player.level == 5:
                        self.journal.add_achievement(
                            "Apprentice Adventurer", 
                            "Reached level 5 on your adventure."
                        )
                    elif self.player.level == 10:
                        self.journal.add_achievement(
                            "Veteran Explorer", 
                            "Reached level 10 on your adventure."
                        )
                    elif self.player.level == 15:
                        self.journal.add_achievement(
                            "Master Delver", 
                            "Reached level 15 on your adventure."
                        )

                # Handle enemy drops with enhanced system
                from systems.enemy_drops import process_enemy_drops, display_drops
                drops = process_enemy_drops(enemy, self.player.level)
                display_drops(self, enemy.name, drops)
                
                # Add drops to player inventory or room
                for item_name, quantity in drops.items():
                    if item_name == "coin":
                        self.coins += quantity
                    else:
                        for _ in range(quantity):
                            self.player.add_to_inventory(item_name)

                # Update quest progress for killing enemies
                self.quest_manager.update_quest_progress("kill", enemy.name, self.current_room)
                
                # Update journal stats for enemy defeat
                self.journal.update_stats("enemies_killed", 1, enemy.name)
                
                # Add journal entry for significant enemies
                if enemy.name in ["goblin_shaman", "dire_wolf", "stone_golem", "crystal_guardian", "mind_flayer"]:
                    location = self.current_room.replace("_", " ").title()
                    self.journal.add_entry(f"Defeated a {enemy.name} in {location}.", "combat")
                
                # Track combat in journal with victory
                self.journal.track_combat(enemy.name, total_damage_dealt, total_damage_taken, True, 
                                        critical_hits=critical_hits, dodges=dodges)
                
                # Update bestiary with this enemy defeat
                self.bestiary.record_encounter(
                    enemy.name, 
                    killed=True, 
                    damage_dealt=total_damage_dealt, 
                    damage_taken=total_damage_taken, 
                    location=self.current_room
                )
                
                return None
            
            # === ENEMY ATTACK PHASE ===
            
            # Calculate enemy hit chance (base 80%)
            enemy_hit_chance = 0.8
            
            # Apply environmental accuracy modifiers
            enemy_accuracy_mod = env_effects.get("enemy_accuracy", 0)
            enemy_hit_chance += enemy_accuracy_mod / 10  # Convert to percentage
            
            # Apply dodge chance from player skills/equipment (could be implemented)
            player_dodge_chance = 0.1  # Base 10% dodge chance
            
            # Cap hit and dodge chances
            enemy_hit_chance = max(0.5, min(0.95, enemy_hit_chance))
            player_dodge_chance = max(0.05, min(0.3, player_dodge_chance))
            
            # Check if player dodges
            if random.random() < player_dodge_chance:
                dodges += 1
                self.add_to_history(f"You nimbly dodge the {enemy.name}'s attack!", self.COMBAT_COLOR)
            elif random.random() < enemy_hit_chance:
                # Enemy hit succeeded!
                
                # Check for special attacks
                special_attack = None
                if hasattr(enemy, 'special_attacks') and enemy.special_attacks:
                    for effect_name, effect_data in enemy.special_attacks.items():
                        # Roll for effect chance
                        if random.random() < effect_data.get("chance", 0):
                            special_attack = (effect_name, effect_data)
                            break
                
                # Calculate damage
                if special_attack:
                    attack_name, attack_data = special_attack
                    
                    if attack_name == "poison":
                        # Normal damage + poison effect
                        base_damage = random.randint(
                            max(1, enemy.attack - 3),
                            enemy.attack + 1
                        )
                        
                        # Create and apply poison effect
                        from systems.status_effects.status_effects import PoisonEffect
                        poison = PoisonEffect(
                            duration=attack_data.get("duration", 30),
                            strength=attack_data.get("strength", 1)
                        )
                        self.status_effect_manager.add_effect(poison)
                        
                        # Display message
                        message = attack_data.get("message", f"The {enemy.name} poisons you!")
                        self.add_to_history(message, (0, 180, 0))
                        
                    elif attack_name == "ranged":
                        # Ranged attack with damage multiplier
                        base_damage = random.randint(
                            max(1, enemy.attack - 3),
                            enemy.attack + 1
                        )
                        damage_mult = attack_data.get("damage_mult", 1.2)
                        base_damage = int(base_damage * damage_mult)
                        
                        # Display message
                        message = attack_data.get("message", f"The {enemy.name} attacks from a distance!")
                        self.add_to_history(message, self.ENEMY_COLOR)
                        
                    elif attack_name == "magic":
                        # Magic attack with damage multiplier
                        base_damage = random.randint(
                            max(1, enemy.attack - 2),
                            enemy.attack + 2
                        )
                        damage_mult = attack_data.get("damage_mult", 1.5)
                        base_damage = int(base_damage * damage_mult)
                        
                        # Display message
                        message = attack_data.get("message", f"The {enemy.name} casts a spell at you!")
                        self.add_to_history(message, self.ENEMY_COLOR)
                        
                    elif attack_name == "rend":
                        # Physical attack + bleeding effect
                        base_damage = random.randint(
                            max(1, enemy.attack - 3),
                            enemy.attack + 1
                        )
                        
                        # Apply bleeding status effect
                        from systems.status_effects.bleeding_effect import apply_bleeding_effect
                        bleed = apply_bleeding_effect(
                            self,
                            duration=attack_data.get("bleed_duration", 20),
                            strength=attack_data.get("bleed_damage", 1)
                        )
                        
                        # Display message
                        message = attack_data.get("message", f"The {enemy.name} tears at your flesh!")
                        self.add_to_history(message, self.ENEMY_COLOR)
                        
                    elif attack_name == "split":
                        # Special ability for slimes - split when low on health
                        # This would need to be implemented to actually spawn a new enemy
                        base_damage = random.randint(
                            max(1, enemy.attack - 4),
                            enemy.attack
                        )
                        
                        message = attack_data.get("message", f"The {enemy.name} splits into two!")
                        self.add_to_history(message, self.ENEMY_COLOR)
                        
                        # TODO: Implement actual enemy splitting
                        
                    else:
                        # Default for unknown special attacks
                        base_damage = random.randint(
                            max(1, enemy.attack - 2),
                            enemy.attack + 2
                        )
                        
                        message = f"The {enemy.name} uses an unknown special attack!"
                        self.add_to_history(message, self.ENEMY_COLOR)
                else:
                    # Normal attack
                    base_damage = random.randint(
                        max(1, enemy.attack - 2),
                        enemy.attack + 2
                    )
                    
                # Apply player defense
                final_damage = max(1, base_damage - self.player.defense_power())
                actual_damage = self.player.take_damage(final_damage)
                total_damage_taken += actual_damage
                
                # Display damage message if not already shown by special attack
                if not special_attack or special_attack[0] not in ["poison", "ranged", "magic", "rend", "split"]:
                    self.add_to_history(f"The {enemy.name} hits you for {actual_damage} damage!", self.ENEMY_COLOR)
                
                # Display current health
                self.add_to_history(f"Your health: {self.player.health}/{self.player.max_health}", self.HEALTH_COLOR)
                
            else:
                # Enemy missed
                self.add_to_history(f"The {enemy.name} attacks but misses you!", self.ENEMY_COLOR)
            
            # Check if player died
            if self.player.health <= 0:
                self.add_to_history("You have been defeated! Game over.", self.COMBAT_COLOR)
                self.game_over = True
                
                # Add journal entry for player defeat
                self.journal.add_entry(f"Defeated by a {enemy.name} in {self.current_room.replace('_', ' ')}.", "death")
                
                # Track combat in journal with defeat
                self.journal.track_combat(enemy.name, total_damage_dealt, total_damage_taken, False,
                                        critical_hits=critical_hits, dodges=dodges)
                
                # Update bestiary for the encounter
                self.bestiary.record_encounter(
                    enemy.name,
                    killed=False,
                    damage_dealt=total_damage_dealt, 
                    damage_taken=total_damage_taken,
                    location=self.current_room
                )
            else:
                # Track ongoing combat (not a victory or defeat yet)
                self.journal.track_combat(enemy.name, total_damage_dealt, total_damage_taken, None,
                                        critical_hits=critical_hits, dodges=dodges)
                
                # Update bestiary for the encounter (not killed)
                self.bestiary.record_encounter(
                    enemy.name,
                    killed=False,
                    damage_dealt=total_damage_dealt, 
                    damage_taken=total_damage_taken,
                    location=self.current_room
                )
                
            return f"The {enemy.name} has {enemy.health}/{enemy.max_health} health remaining."    

    def process_enemy_drops(enemy, player_level, player_luck=0):
        """
        Generate drops when an enemy is defeated, using the enhanced drop system
        
        Args:
            enemy (Enemy): The defeated enemy object
            player_level (int): Current player level
            player_luck (int): Player's luck stat modifier (if implemented)
            
        Returns:
            dict: Dictionary of {item_name: quantity} representing drops
        """
        drops = {}
        
        # First check if enemy has specific drop data
        if hasattr(enemy, 'drops') and enemy.drops:
            enemy_drops = enemy.drops
            
            # Process common drops (higher chance)
            if "common" in enemy_drops:
                for drop_info in enemy_drops["common"]:
                    item_name, min_qty, max_qty, base_chance = drop_info
                    
                    # Apply luck modifier to chance
                    modified_chance = base_chance * (1 + (player_luck * 0.05))
                    
                    if random.random() < modified_chance:
                        quantity = random.randint(min_qty, max_qty)
                        if item_name in drops:
                            drops[item_name] += quantity
                        else:
                            drops[item_name] = quantity
            
            # Process uncommon drops (lower chance)
            if "uncommon" in enemy_drops:
                for drop_info in enemy_drops["uncommon"]:
                    item_name, min_qty, max_qty, base_chance = drop_info
                    
                    # Apply luck and level modifiers to chance
                    # Higher level enemies have better chances for uncommon drops
                    level_factor = min(1.5, enemy.experience / 10)  # Experience as a proxy for enemy level
                    modified_chance = base_chance * level_factor * (1 + (player_luck * 0.1))
                    
                    if random.random() < modified_chance:
                        quantity = random.randint(min_qty, max_qty)
                        if item_name in drops:
                            drops[item_name] += quantity
                        else:
                            drops[item_name] = quantity
            
            # Process rare drops (very low chance)
            if "rare" in enemy_drops:
                for drop_info in enemy_drops["rare"]:
                    item_name, min_qty, max_qty, base_chance = drop_info
                    
                    # Apply significant luck and level modifiers to chance
                    level_factor = min(2.0, enemy.experience / 8)  # Experience as a proxy for enemy level
                    modified_chance = base_chance * level_factor * (1 + (player_luck * 0.15))
                    
                    if random.random() < modified_chance:
                        quantity = random.randint(min_qty, max_qty)
                        if item_name in drops:
                            drops[item_name] += quantity
                        else:
                            drops[item_name] = quantity
        
        # Fall back to generic drops if no specific drops or as a supplement
        if not drops or random.random() < 0.3:  # 30% chance to add generic drops in addition
            # Get enemy "level" based on experience or health
            enemy_level = max(1, enemy.experience // 5)  # Crude approximation
            
            # Coins almost always drop
            if random.random() < 0.9:  # 90% chance
                base_coins = enemy_level * 2
                coin_amount = max(1, int(base_coins * random.uniform(0.7, 1.3)))  # ±30% variation
                if "coin" in drops:
                    drops["coin"] += coin_amount
                else:
                    drops["coin"] = coin_amount
            
            # Generic item drops
            generic_drops = {
                "common": [
                    ("healing_potion", 0.15),
                    ("bread", 0.1),
                    ("torch", 0.05)
                ],
                "uncommon": [
                    ("strong_healing_potion", 0.05),
                    ("common_box_key", 0.08),
                    ("gem", 0.07)
                ],
                "rare": [
                    ("uncommon_box_key", 0.03),
                    ("stamina_potion", 0.04),
                    ("rare_box_key", 0.01)
                ]
            }
            
            # Process generic common drops
            for item_name, chance in generic_drops["common"]:
                if random.random() < chance * (1 + (player_luck * 0.05)):
                    drops[item_name] = drops.get(item_name, 0) + 1
            
            # Process generic uncommon drops - affected by enemy level
            for item_name, chance in generic_drops["uncommon"]:
                level_factor = min(1.5, enemy_level / player_level)
                if random.random() < chance * level_factor * (1 + (player_luck * 0.1)):
                    drops[item_name] = drops.get(item_name, 0) + 1
            
            # Process generic rare drops - significantly affected by enemy level
            for item_name, chance in generic_drops["rare"]:
                level_factor = min(2.0, enemy_level / player_level)
                if random.random() < chance * level_factor * (1 + (player_luck * 0.15)):
                    drops[item_name] = drops.get(item_name, 0) + 1
        
        return drops


    def check_region(self):
        """Display information about the current region"""
        region = self.world.get_region_for_room(self.current_room)
        
        if not region:
            self.add_to_history("You are not in any notable region.")
            return
        
        # Only show detailed info if the region has been discovered
        if not region.discovered:
            self.add_to_history("You haven't fully explored this region yet.")
            return
        
        # Display region summary
        summary = region.get_summary()
        
        self.add_to_history("Region Information:", (180, 180, 255))
        for line in summary:
            self.add_to_history(line)
            
        # List known rooms in this region
        known_rooms = []
        for room_name in region.get_all_room_names():
            known_rooms.append(room_name.replace('_', ' ').title())
        
        if known_rooms:
            self.add_to_history(f"\nAreas in this region: {', '.join(known_rooms)}")
        
        # Show environment bias
        env_bias = region.get_environment_bias()
        if env_bias:
            self.add_to_history("\nEnvironmental tendencies:")
            for weather, bias in env_bias.items():
                if bias > 1.0:
                    self.add_to_history(f"- {weather.capitalize()} conditions are common here")

    # Add a method to get the current region's environment system
    def get_current_environment_system(self):
        """Get the environment system for the current region"""
        region = self.world.get_region_for_room(self.current_room)
        if region:
            return region.environment_system
        return None

    def show_status(self):
        self.add_to_history("Player Status:", TITLE_COLOR)
        self.add_to_history(f"Health: {self.player.health}/{self.player.max_health}", HEALTH_COLOR)
        self.add_to_history(f"Level: {self.player.level} (EXP: {self.player.experience}/{self.player.exp_to_next_level})")
        self.add_to_history(f"Attack: {self.player.attack_power()} (Base: {self.player.attack})")
        self.add_to_history(f"Defense: {self.player.defense_power()} (Base: {self.player.defense})")
        self.add_to_history(f"Coins: {self.coins}")
        
        # Show status effects if any are active
        status_text = self.status_effect_manager.get_status_text()
        if status_text:
            self.add_to_history(f"Status Effects: {status_text}", (255, 165, 0))  # COMBAT_COLOR
        
        # Show all equipped items using the equipment slots
        self.add_to_history("\nEquipment:", TITLE_COLOR)
        
        # Get list of all equipped items
        equipment_list = self.player.get_equipment_list()
        
        if not equipment_list:
            self.add_to_history("  Nothing equipped")
        else:
            for item in equipment_list:
                self.add_to_history(f"  {item}")
        
        # Show combat stats summary
        self.add_to_history(f"\nTotal Stats:")
        self.add_to_history(f"  Attack: {self.player.attack_power()}")
        self.add_to_history(f"  Defense: {self.player.defense_power()}")
    
    def show_help(self):
        self.add_to_history("Available Commands:", TITLE_COLOR)
        
        # Movement commands
        self.add_to_history("\nMOVEMENT:", TITLE_COLOR)
        self.add_to_history("  go [direction] (g) - Move in a direction (north, south, east, west)")
        self.add_to_history("  [direction] - Just type a direction (north, south, east, west, n, s, e, w)")
        
        # Exploration commands
        self.add_to_history("\nEXPLORATION:", TITLE_COLOR)
        self.add_to_history("  look (l) - Look around the current location")
        self.add_to_history("  examine [item/enemy] - Examine something in detail")
        self.add_to_history("  region (reg) - Check information about the current region")
        self.add_to_history("  regions - List all discovered regions")
        self.add_to_history("  weather (env) - Check current environmental conditions and effects")
        
        # Item commands
        self.add_to_history("\nITEMS:", TITLE_COLOR)
        self.add_to_history("  take [item] (t) - Pick up an item")
        self.add_to_history("  drop [item] - Drop an item from your inventory")
        self.add_to_history("  inventory (i, inv) - Show your inventory")
        self.add_to_history("  use [item] (u) - Use an item")
        self.add_to_history("  equip [item] (e) - Equip a weapon or armor")
        
        # Combat commands
        self.add_to_history("\nCOMBAT:", TITLE_COLOR)
        self.add_to_history("  attack [enemy] (a) - Attack an enemy")
        self.add_to_history("  kill [enemy] (k) - Another way to attack an enemy")
        
        # Player commands
        self.add_to_history("\nPLAYER:", TITLE_COLOR)
        self.add_to_history("  status (s, stats) - Show player stats")
        self.add_to_history("  coins (c) - Check how many coins you have")
        
        # Shop commands
        self.add_to_history("\nSHOP:", TITLE_COLOR)
        self.add_to_history("  list - View the shop inventory")
        self.add_to_history("  buy [item] - Purchase an item from a shop")
        self.add_to_history("  sell [item] - Sell an item to a shop")
        
        # Crafting commands
        self.add_to_history("\nCRAFTING:", TITLE_COLOR)
        self.add_to_history("  recipes (r) - Show available crafting recipes")
        self.add_to_history("  craft [item] - Craft an item using ingredients in your inventory")
        
        # Save/Load commands
        self.add_to_history("\nSAVE & LOAD:", TITLE_COLOR)
        self.add_to_history("  save [filename] - Save your game progress")
        self.add_to_history("  load [filename] - Load a saved game")
        self.add_to_history("  saves - List all available save files")
        self.add_to_history("  saveslot [1-5] - Save to a numbered slot")
        self.add_to_history("  loadslot [1-5] - Load from a numbered slot")
        self.add_to_history("  deletesave [filename] - Delete a save file")
        self.add_to_history("  autosave [on/off] - Toggle automatic saving")
        
        # System commands
        self.add_to_history("\nSYSTEM:", TITLE_COLOR)
        self.add_to_history("  help (h) - Show this help message or 'help [command]' for details")
        self.add_to_history("  quit (q, exit) - Exit the game")

    def display_drops(game_state, enemy_name, drops):
        """Format and display drops to the player in an appealing way"""
        if not drops:
            game_state.add_to_history(f"The {enemy_name} didn't drop anything.")
            return
        
        # Categorize drops for better presentation
        coins = drops.get("coin", 0)
        equipment = []
        consumables = []
        keys = []
        other = []
        
        from items.item_factory import ItemFactory
        
        # Sort drops into categories
        for item_name, quantity in drops.items():
            if item_name == "coin":
                continue  # Handled separately
                
            item = ItemFactory.get_item(item_name)
            if not item:
                other.append((item_name.replace('_', ' '), quantity))
                continue
                
            if item.type in ["weapon", "armor"]:
                equipment.append((item.display_name(), quantity))
            elif item.type in ["consumable", "food", "drink"]:
                consumables.append((item.display_name(), quantity))
            elif "key" in item_name:
                keys.append((item.display_name(), quantity))
            else:
                other.append((item.display_name(), quantity))
        
        # Create the drop message
        game_state.add_to_history(f"The {enemy_name} dropped:", (100, 220, 100))
        
        # Show coins first if any
        if coins > 0:
            game_state.add_to_history(f"• {coins} coins", (255, 215, 0))  # Gold color
        
        # Show equipment with special highlighting
        for name, qty in equipment:
            if qty > 1:
                game_state.add_to_history(f"• {qty}x {name}", (220, 150, 150))  # Light red for equipment
            else:
                game_state.add_to_history(f"• {name}", (220, 150, 150))
        
        # Show keys with special highlighting
        for name, qty in keys:
            if qty > 1:
                game_state.add_to_history(f"• {qty}x {name}", (150, 150, 220))  # Light blue for keys
            else:
                game_state.add_to_history(f"• {name}", (150, 150, 220))
        
        # Show consumables
        for name, qty in consumables:
            if qty > 1:
                game_state.add_to_history(f"• {qty}x {name}", (150, 220, 150))  # Light green for consumables
            else:
                game_state.add_to_history(f"• {name}", (150, 220, 150))
        
        # Show other items
        for name, qty in other:
            if qty > 1:
                game_state.add_to_history(f"• {qty}x {name}")
            else:
                game_state.add_to_history(f"• {name}")
        
        return
