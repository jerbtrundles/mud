# core/game_state_manager.py
"""
A state machine to manage different game states (exploration, combat, dialogue, etc.).
"""

import random
from enum import Enum, auto

class GameStateType(Enum):
    """Enumeration of possible game states"""
    TITLE_SCREEN = auto()
    MENU = auto()
    EXPLORATION = auto()
    COMBAT = auto()
    DIALOGUE = auto()
    INVENTORY = auto()
    SHOP = auto()
    REST = auto()
    GAME_OVER = auto()

class GameStateManager:
    """
    Manages transitions between different game states and dispatches commands
    to the appropriate handler.
    """
    
    def __init__(self, game_state):
        """
        Initialize the game state manager
        
        Args:
            game_state: The game state object
        """
        self.game_state = game_state
        self.current_state = GameStateType.EXPLORATION
        self.previous_state = None
        self.state_handlers = {
            GameStateType.TITLE_SCREEN: self._handle_title_screen,
            GameStateType.MENU: self._handle_menu,
            GameStateType.EXPLORATION: self._handle_exploration,
            GameStateType.COMBAT: self._handle_combat,
            GameStateType.DIALOGUE: self._handle_dialogue,
            GameStateType.INVENTORY: self._handle_inventory,
            GameStateType.SHOP: self._handle_shop,
            GameStateType.REST: self._handle_rest,
            GameStateType.GAME_OVER: self._handle_game_over
        }
        
        # Command handlers for each state
        self.command_handlers = {
            GameStateType.EXPLORATION: self._handle_exploration_command,
            GameStateType.COMBAT: self._handle_combat_command,
            GameStateType.INVENTORY: self._handle_inventory_command,
            GameStateType.SHOP: self._handle_shop_command,
            GameStateType.DIALOGUE: self._handle_dialogue_command,
            GameStateType.REST: self._handle_rest_command,
            GameStateType.GAME_OVER: self._handle_game_over_command
        }
        
        # Additional state context
        self.state_context = {}
    
    def transition_to(self, state, **context):
        """
        Transition to a new game state
        
        Args:
            state: GameStateType to transition to
            **context: Optional context data for the new state
        """
        if state == self.current_state:
            return
            
        self.previous_state = self.current_state
        self.current_state = state
        self.state_context = context
        
        # Log the transition
        if not isinstance(self.current_state, GameStateType):
            raise ValueError(f"Invalid state type: {self.current_state}")
            
        self.game_state.add_to_history(f"Entering {self.current_state.name.replace('_', ' ').title()} mode.")
        
        # Run the enter handler for the new state
        self.state_handlers[self.current_state]()
    
    def return_to_previous_state(self):
        """Return to the previous game state if available"""
        if self.previous_state:
            temp = self.current_state
            self.current_state = self.previous_state
            self.previous_state = temp
            self.state_handlers[self.current_state]()
        else:
            # Default to exploration if no previous state
            self.transition_to(GameStateType.EXPLORATION)
    
    def process_command(self, command_text):
        """
        Process a command in the current state
        
        Args:
            command_text: The command text to process
            
        Returns:
            str: The result message, or None
        """
        # Get the appropriate command handler for the current state
        if self.current_state in self.command_handlers:
            return self.command_handlers[self.current_state](command_text)
        
        # Default if no handler exists
        return f"Cannot process commands in {self.current_state.name} state."
    
    def update(self):
        """Update the current state - called once per game loop"""
        # Call the current state's handler
        if self.current_state in self.state_handlers:
            self.state_handlers[self.current_state]()
    
    def is_in_state(self, state):
        """Check if currently in a specific state"""
        return self.current_state == state
    
    # State enter/update handlers
    
    def _handle_title_screen(self):
        """Handle title screen state"""
        # Implementation depends on UI system
        pass
    
    def _handle_menu(self):
        """Handle menu state"""
        # Implementation depends on UI system
        pass
    
    def _handle_exploration(self):
        """Handle exploration state updates"""
        # Update enemies, environment, etc.
        if hasattr(self.game_state, 'enemy_manager'):
            self.game_state.enemy_manager.update(self.game_state)
            
        # Update environment
        current_region = self.game_state.world.get_region_for_room(self.game_state.current_room)
        if current_region:
            current_region.update(self.game_state)
            
        # Check for automatic combat
        if hasattr(self.game_state, 'enemy_manager'):
            # If there are enemies in the current room, transition to combat
            enemies = self.game_state.enemy_manager.get_enemies_in_room(self.game_state.current_room)
            if enemies and all(e.is_alive() for e in enemies):
                self.transition_to(GameStateType.COMBAT, enemies=enemies)
    
    def _handle_combat(self):
        """Handle combat state updates"""
        # If combat is no longer active, return to exploration
        if not self.game_state.combat_system.active_combat:
            self.transition_to(GameStateType.EXPLORATION)
            return
            
        # Other combat updates handled by combat system
    
    def _handle_dialogue(self):
        """Handle dialogue state updates"""
        # Implementation depends on dialogue system
        pass
    
    def _handle_inventory(self):
        """Handle inventory state updates"""
        # No updates needed, inventory is static until commands are given
        pass
    
    def _handle_shop(self):
        """Handle shop state updates"""
        # No updates needed, shop is static until commands are given
        pass
    
    def _handle_rest(self):
        """Handle rest state updates"""
        # Implementation depends on rest mechanics
        pass
    
    def _handle_game_over(self):
        """Handle game over state updates"""
        # No updates needed, game over is a terminal state
        pass
    
    # Command handlers for each state
    
    def _handle_exploration_command(self, command_text):
        """
        Handle commands in exploration state
        
        Args:
            command_text: The command text to process
            
        Returns:
            str: Result message or None
        """
        # Split command into parts
        parts = command_text.lower().strip().split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle exploration-specific commands
        if cmd in ["look", "l"]:
            self.game_state.look()
            return None
            
        elif cmd in ["go", "g", "north", "south", "east", "west", "n", "s", "e", "w", "northwest", "nw", "northeast", "ne", "southwest", "sw", "southeast", "se"]:
            # Handle movement
            direction = cmd
            if cmd in ["go", "g"] and args:
                direction = args[0]
                
            # Convert shorthand directions
            if direction == "n": direction = "north"
            elif direction == "s": direction = "south"
            elif direction == "e": direction = "east"
            elif direction == "w": direction = "west"
            elif direction == "sw": direction = "southwest"
            elif direction == "se": direction = "southeast"
            elif direction == "s": direction = "northwest"
            elif direction == "ne": direction = "northeast"
            
            # Try to move
            self.game_state.go(direction)
            return None
            
        elif cmd in ["take", "t"] and args:
            # Handle taking items
            item = " ".join(args)
            self.game_state.take(item)
            return None
            
        elif cmd in ["inventory", "i", "inv"]:
            # Show inventory and optionally transition to inventory state
            self.game_state.show_inventory()
            return None
            
        elif cmd in ["examine", "x"] and args:
            # Examine something in the environment
            target = " ".join(args)
            self.game_state.examine(target)
            return None
            
        elif cmd in ["attack", "a", "kill", "k"] and args:
            # Attack initiates combat if not already in it
            target = " ".join(args)
            enemy = self.game_state.enemy_manager.get_enemy_by_name_in_room(target, self.game_state.current_room)
            
            if enemy and enemy.is_alive():
                # Start combat
                self.transition_to(GameStateType.COMBAT, enemies=[enemy])
                return None
            else:
                return f"There is no {target} here to attack."
                
        elif cmd in ["use", "u"] and args:
            # Use an item
            item_name = " ".join(args)
            item_id = self.game_state.player.find_item(item_name)
            
            if not item_id:
                return f"You don't have a {item_name}."
                
            item = self.game_state.player.get_item(item_id)
            success, message = item.use(self.game_state)
            
            if success and item.type == "consumable":
                self.game_state.player.remove_from_inventory(item_id)
                
            return message
            
        # Fall back to the command parser for other commands
        return self.game_state.command_parser.parse(command_text)
    
    def _handle_combat_command(self, command_text):
        """
        Handle commands in combat state
        
        Args:
            command_text: The command text to process
            
        Returns:
            str: Result message or None
        """
        # Split command into parts
        parts = command_text.lower().strip().split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle combat-specific commands
        if cmd in ["attack", "a", "hit", "strike"] and self.game_state.combat_system.active_combat:
            # Determine target
            if not args and len(self.game_state.combat_system.current_enemies) == 1:
                # Auto-target when only one enemy
                target = self.game_state.combat_system.current_enemies[0]
            elif not args:
                return "Attack which enemy?"
            else:
                # Find target by name
                target_name = " ".join(args)
                for enemy in self.game_state.combat_system.current_enemies:
                    if enemy.name.lower() == target_name or target_name in enemy.name.lower():
                        target = enemy
                        break
                else:
                    return f"There is no {target_name} to attack."
            
            # Execute attack
            success, message = self.game_state.combat_system.player_attack(target)
            return message
            
        elif cmd in ["use", "u"] and args:
            # Use an item in combat
            item_name = " ".join(args)
            item_id = self.game_state.player.find_item(item_name)
            
            if not item_id:
                return f"You don't have a {item_name}."
                
            item = self.game_state.player.get_item(item_id)
            
            # Use item through combat system
            success, message = self.game_state.combat_system.player_use_item(item)
            return message
            
        elif cmd in ["run", "flee", "escape"]:
            # Attempt to flee combat
            success, message = self.game_state.combat_system.player_flee()
            return message
            
        elif cmd in ["skill", "cast", "ability"] and args:
            # Use a skill in combat
            skill_name = " ".join(args)
            
            # Find the skill
            if not hasattr(self.game_state, 'skill_manager'):
                return "You don't have any skills to use."
                
            # Try to find a target if not specified
            target = None
            for enemy in self.game_state.combat_system.current_enemies:
                if enemy.is_alive():
                    target = enemy
                    break
                    
            # Use the skill through the combat system
            success, message = self.game_state.skill_manager.use_skill(skill_name, target)
            return message
            
        elif cmd in ["look", "l"]:
            # Show combat state
            self._display_combat_state()
            return None
            
        elif cmd in ["inventory", "i", "inv"]:
            # Just show inventory without state transition during combat
            self.game_state.show_inventory()
            return None
            
        elif cmd in ["status", "stats"]:
            # Show player status
            self.game_state.show_status()
            return None
            
        return f"Invalid combat command. Try 'attack', 'use [item]', 'flee', or 'look'."
    
    def _display_combat_state(self):
        """Display the current state of combat"""
        self.game_state.add_to_history("Current combat situation:", (255, 255, 100))
        
        # Show enemies
        self.game_state.add_to_history("Enemies:", (255, 100, 100))
        for i, enemy in enumerate(self.game_state.combat_system.current_enemies):
            if enemy.is_alive():
                health_pct = enemy.health / enemy.max_health
                health_bar = self._get_health_bar(health_pct)
                self.game_state.add_to_history(f"{i+1}. {enemy.name}: {enemy.health}/{enemy.max_health} {health_bar}", (255, 100, 100))
        
        # Show player status
        player = self.game_state.player
        health_pct = player.health / player.max_health
        health_bar = self._get_health_bar(health_pct)
        self.game_state.add_to_history(f"Your health: {player.health}/{player.max_health} {health_bar}", (100, 255, 100))
        
        # Show whose turn it is
        current_actor = self.game_state.combat_system.initiative_order[self.game_state.combat_system.current_actor_index]
        if current_actor == self.game_state.player:
            self.game_state.add_to_history("It's your turn to act!", (255, 255, 100))
        else:
            self.game_state.add_to_history(f"It's {current_actor.name}'s turn to act.", (200, 200, 200))
        
        # Show available commands
        self.game_state.add_to_history("\nAvailable commands:", (200, 200, 200))
        self.game_state.add_to_history("attack [enemy] - Attack an enemy", (200, 200, 200))
        self.game_state.add_to_history("use [item] - Use an item", (200, 200, 200))
        self.game_state.add_to_history("skill [skill] - Use a skill", (200, 200, 200))
        self.game_state.add_to_history("flee - Try to escape combat", (200, 200, 200))
        self.game_state.add_to_history("status - Check your status", (200, 200, 200))
    
    def _get_health_bar(self, percentage, length=10):
        """Generate a text-based health bar"""
        filled = int(percentage * length)
        empty = length - filled
        return "[" + "█" * filled + "▒" * empty + "]"
    
    def _handle_inventory_command(self, command_text):
        """
        Handle commands in inventory state
        
        Args:
            command_text: The command text to process
            
        Returns:
            str: Result message or None
        """
        # Split command into parts
        parts = command_text.lower().strip().split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle inventory-specific commands
        if cmd in ["examine", "x", "look", "l"] and args:
            # Examine an item in inventory
            item_name = " ".join(args)
            item_id = self.game_state.player.find_item(item_name)
            
            if not item_id:
                return f"You don't have a {item_name}."
                
            item = self.game_state.player.get_item(item_id)
            self.game_state.add_to_history(f"You examine the {item.display_name()}:", (255, 255, 100))
            self.game_state.add_to_history(item.description)
            
            # Show special properties based on item type
            if item.type == "weapon":
                self.game_state.add_to_history(f"Attack bonus: +{item.attack_bonus}")
            elif item.type == "armor":
                self.game_state.add_to_history(f"Defense bonus: +{item.defense_bonus}")
            elif item.type == "consumable":
                if item.health_restore > 0:
                    self.game_state.add_to_history(f"Restores {item.health_restore} health when consumed.")
            
            self.game_state.add_to_history(f"Value: {item.value} coins")
            return None
            
        elif cmd in ["use", "u"] and args:
            # Use an item from inventory
            item_name = " ".join(args)
            item_id = self.game_state.player.find_item(item_name)
            
            if not item_id:
                return f"You don't have a {item_name}."
                
            item = self.game_state.player.get_item(item_id)
            success, message = item.use(self.game_state)
            
            if success and item.type == "consumable":
                self.game_state.player.remove_from_inventory(item_id)
                
            return message
            
        elif cmd in ["drop", "d"] and args:
            # Drop an item from inventory
            item_name = " ".join(args)
            item_id = self.game_state.player.find_item(item_name)
            
            if not item_id:
                return f"You don't have a {item_name}."
                
            # Get item object for better messaging
            item = self.game_state.player.get_item(item_id)
            
            # Remove from inventory
            self.game_state.player.remove_from_inventory(item_id)
            
            # Add to current room
            room = self.game_state.world.get_room(self.game_state.current_room)
            if "items" not in room:
                room["items"] = []
                
            room["items"].append(item_id)
            
            return f"You drop the {item.display_name()}."
            
        elif cmd in ["equip", "e"] and args:
            # Equip an item
            item_name = " ".join(args)
            self.game_state.equip(item_name)
            return None
            
        elif cmd in ["unequip", "u"] and args:
            # Unequip an item
            slot = args[0].lower()
            
            # Map common terms to slot names
            slot_mapping = {
                "helmet": "head",
                "armor": "chest",
                "gloves": "hands",
                "gauntlets": "hands",
                "leggings": "legs",
                "greaves": "legs",
                "boots": "feet",
                "shoes": "feet",
                "amulet": "neck",
                "necklace": "neck",
                "pendant": "neck",
                "sword": "weapon",
                "blade": "weapon"
            }
            
            if slot in slot_mapping:
                slot = slot_mapping[slot]
                
            success, result = self.game_state.player.unequip_item(slot)
            
            if not success:
                return result
            
            # Item was unequipped successfully
            item = self.game_state.player.get_item(result)
            if item:
                self.game_state.player.add_to_inventory(result)
                self.game_state.add_to_history(f"You unequip the {item.display_name()} and put it in your inventory.")
                
                # Show updated defense if armor was unequipped
                if item.type == "armor":
                    self.game_state.add_to_history(f"Defense decreased to {self.game_state.player.defense_power()}.")
                elif slot == "weapon":
                    self.game_state.add_to_history(f"Attack power decreased to {self.game_state.player.attack_power()}.")
            
            return None
            
        elif cmd in ["sort", "s"] and args:
            # Sort inventory
            sort_by = args[0].lower() if args else "name"
            if sort_by not in ["name", "quantity", "value", "type"]:
                return f"Invalid sort option. Use 'name', 'quantity', 'value', or 'type'."
                
            # Sort inventory and display
            self.game_state.player.inventory.sort_items(sort_by)
            self.game_state.show_inventory()
            return None
            
        elif cmd in ["exit", "back", "close", "done"]:
            # Return to previous state
            self.return_to_previous_state()
            return None
            
        # Fall back to the command parser for other commands
        return self.game_state.command_parser.parse(command_text)
    
    def _handle_shop_command(self, command_text):
        """
        Handle commands in shop state
        
        Args:
            command_text: The command text to process
            
        Returns:
            str: Result message or None
        """
        # Split command into parts
        parts = command_text.lower().strip().split()
        cmd = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        # Handle shop-specific commands
        if cmd in ["list", "l"]:
            # List shop inventory
            self.game_state.shop_system.display_shop_inventory(self.game_state)
            return None
            
        elif cmd in ["buy", "b"] and args:
            # Buy an item
            item = " ".join(args)
            self.game_state.buy(item)
            return None
            
        elif cmd in ["sell", "s"] and args:
            # Sell an item
            item = " ".join(args)
            self.game_state.sell(item)
            return None
            
        elif cmd in ["exit", "leave", "back", "done"]:
            # Return to previous state
            self.return_to_previous_state()
            return None
            
        # Fall back to the command parser for other commands
        return self.game_state.command_parser.parse(command_text)
    
    def _handle_dialogue_command(self, command_text):
        """
        Handle commands in dialogue state
        
        Args:
            command_text: The command text to process
            
        Returns:
            str: Result message or None
        """
        # Implementation depends on dialogue system
        # For now, just return to exploration
        self.return_to_previous_state()
        return "Dialogue ended."
    
    def _handle_rest_command(self, command_text):
        """
        Handle commands in rest state
        
        Args:
            command_text: The command text to process
            
        Returns:
            str: Result message or None
        """
        # Split command into parts
        parts = command_text.lower().strip().split()
        cmd = parts[0] if parts else ""
        
        # Handle rest-specific commands
        if cmd in ["rest", "sleep", "yes", "confirm"]:
            # Perform rest
            room = self.game_state.world.get_room(self.game_state.current_room)
            if not room or not room.get("is_inn", False):
                return "There's no place to rest here."
            
            inn_cost = room.get("inn_cost", 5)
            
            # Check if player has enough coins
            if self.game_state.coins < inn_cost:
                return f"You need {inn_cost} coins to rest here, but you only have {self.game_state.coins}."
            
            # Charge the player and restore health
            self.game_state.coins -= inn_cost
            old_health = self.game_state.player.health
            self.game_state.player.health = self.game_state.player.max_health
            health_restored = self.game_state.player.health - old_health
            
            self.game_state.add_to_history(f"You pay {inn_cost} coins for a comfortable bed and a hot meal.")
            self.game_state.add_to_history(f"After a good night's rest, you feel refreshed.")
            self.game_state.add_to_history(f"Health restored to maximum: {self.game_state.player.health}/{self.game_state.player.max_health} (+{health_restored}).", (100, 255, 100))
            
            # Random inn dialogue
            if "inn_dialogue" in room and room["inn_dialogue"]:
                dialogue = random.choice(room["inn_dialogue"])
                self.game_state.add_to_history(f"\n{dialogue}")
                
            # Return to exploration
            self.transition_to(GameStateType.EXPLORATION)
            return None
            
        elif cmd in ["no", "cancel", "leave", "exit"]:
            # Return to exploration without resting
            self.transition_to(GameStateType.EXPLORATION)
            return "You decide not to rest."
            
        # Fall back to the command parser for other commands
        return self.game_state.command_parser.parse(command_text)
    
    def _handle_game_over_command(self, command_text):
        """
        Handle commands in game over state
        
        Args:
            command_text: The command text to process
            
        Returns:
            str: Result message or None
        """
        # Only allow restart or quit commands
        if command_text.lower() in ["restart", "new", "new game"]:
            # Reset the game state
            # Implementation depends on how game restart is handled
            return "Starting a new game..."
            
        elif command_text.lower() in ["quit", "exit"]:
            # Quit the game
            self.game_state.game_over = True
            return "Thanks for playing!"
            
        return "Game over. Type 'restart' for a new game or 'quit' to exit."