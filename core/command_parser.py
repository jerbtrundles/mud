# command_parser.py
import os
import random
import textwrap

class CommandParser:
    def __init__(self, game_state):
        self.game_state = game_state
        self.aliases = {
            # Movement shortcuts
            "n": "north",
            "s": "south",
            "e": "east",
            "w": "west",
            # Command aliases
            "l": "look",
            "i": "inventory",
            "inv": "inventory",
            "g": "go",
            "t": "take",
            "a": "attack",
            "k": "kill",
            "u": "use",
            "stats": "status",
            "c": "coins",
            "r": "recipes",
            "reg": "region",
            "env": "weather",
            "h": "help",
            "q": "quit",
            "exit": "quit",
            "read": "notices",
            "board": "notices",
            "fix": "repair",
            "herbs": "gather",
            "plants": "gather",
            "cmds": "commands",
            "guide": "tutorial",
            "info": "about",
            "j": "journal",
            "log": "journal",
            "diary": "journal",
            "jq": "journal_quest",
            "jr": "journal_region",
            "js": "journal_stats",
            "ja": "journal_achievements",
            "jc": "journal_combat",
        }
        
        # Command definitions with handlers and help text
        self.commands = {
            "look": {
                "handler": self._cmd_look,
                "help": "Look around the current location",
                "syntax": "look",
                "category": "exploration"
            },
            "go": {
                "handler": self._cmd_go,
                "help": "Move in a direction",
                "syntax": "go [direction]",
                "args": ["direction"],
                "category": "movement"
            },
            "north": {
                "handler": lambda args: self._cmd_go(["north"]),
                "help": "Go north",
                "syntax": "north",
                "category": "movement",
                "hidden": True  # Don't show in help
            },
            "south": {
                "handler": lambda args: self._cmd_go(["south"]),
                "help": "Go south",
                "syntax": "south",
                "category": "movement",
                "hidden": True
            },
            "east": {
                "handler": lambda args: self._cmd_go(["east"]),
                "help": "Go east",
                "syntax": "east",
                "category": "movement",
                "hidden": True
            },
            "west": {
                "handler": lambda args: self._cmd_go(["west"]),
                "help": "Go west",
                "syntax": "west",
                "category": "movement",
                "hidden": True
            },
            "take": {
                "handler": self._cmd_take,
                "help": "Pick up an item",
                "syntax": "take [item]",
                "args": ["item"],
                "category": "items"
            },
            "inventory": {
                "handler": self._cmd_inventory,
                "help": "Show your inventory",
                "syntax": "inventory",
                "category": "items"
            },
            "recipes": {
                "handler": self._cmd_recipes,
                "help": "Show available crafting recipes",
                "syntax": "recipes",
                "category": "crafting"
            },
            "craft": {
                "handler": self._cmd_craft,
                "help": "Craft an item using ingredients in your inventory",
                "syntax": "craft [item]",
                "args": ["item"],
                "category": "crafting"
            },
            "use": {
                "handler": self._cmd_use,
                "help": "Use an item",
                "syntax": "use [item]",
                "args": ["item"],
                "category": "items"
            },
            "equip": {
                "handler": self._cmd_equip,
                "help": "Equip a weapon or armor",
                "syntax": "equip [item]",
                "args": ["item"],
                "category": "combat"
            },
            "attack": {
                "handler": self._cmd_attack,
                "help": "Attack an enemy",
                "syntax": "attack [enemy]",
                "args": ["enemy"],
                "category": "combat"
            },
            "kill": {
                "handler": self._cmd_attack,  # Same handler as attack
                "help": "Attack an enemy",
                "syntax": "kill [enemy]",
                "args": ["enemy"],
                "category": "combat",
                "hidden": True
            },
            "status": {
                "handler": self._cmd_status,
                "help": "Show player stats",
                "syntax": "status",
                "category": "player"
            },
            "coins": {
                "handler": self._cmd_coins,
                "help": "Check how many coins you have",
                "syntax": "coins",
                "category": "player"
            },
            "list": {
                "handler": self._cmd_shop_list,
                "help": "View the shop inventory",
                "syntax": "list",
                "category": "shop"
            },
            "buy": {
                "handler": self._cmd_buy,
                "help": "Purchase an item from a shop",
                "syntax": "buy [item]",
                "args": ["item"],
                "category": "shop"
            },
            "sell": {
                "handler": self._cmd_sell,
                "help": "Sell an item to a shop",
                "syntax": "sell [item]",
                "args": ["item"],
                "category": "shop"
            },
            "region": {
                "handler": self._cmd_region,
                "help": "Check information about the current region",
                "syntax": "region",
                "category": "exploration"
            },
            "regions": {
                "handler": self._cmd_regions_list,
                "help": "List all discovered regions",
                "syntax": "regions",
                "category": "exploration"
            },
            "weather": {
                "handler": self._cmd_weather,
                "help": "Check current environmental conditions and effects",
                "syntax": "weather",
                "category": "exploration"
            },
            "help": {
                "handler": self._cmd_help,
                "help": "Show help for commands",
                "syntax": "help [command]",
                "args": ["command"],
                "optional_args": True,
                "category": "system"
            },
            "commands": {
                "handler": self._cmd_commands,
                "help": "Show a compact list of all commands",
                "syntax": "commands",
                "category": "system"
            },
            "quit": {
                "handler": self._cmd_quit,
                "help": "Exit the game",
                "syntax": "quit",
                "category": "system"
            },
            "examine": {
                "handler": self._cmd_examine,
                "help": "Examine an item or enemy in detail",
                "syntax": "examine [target]",
                "args": ["target"],
                "category": "exploration"
            },
            "drop": {
                "handler": self._cmd_drop,
                "help": "Drop an item from your inventory",
                "syntax": "drop [item]",
                "args": ["item"],
                "category": "items"
            },
            "autosave": {
                "handler": self._cmd_autosave,
                "help": "Toggle automatic saving on/off",
                "syntax": "autosave [on/off]",
                "args": ["setting"],
                "optional_args": True,
                "category": "system"
            },
            "save": {
                "handler": self._cmd_save,
                "help": "Save your game",
                "syntax": "save [filename]",
                "args": ["filename"],
                "optional_args": True,
                "category": "system"
            },
            "load": {
                "handler": self._cmd_load,
                "help": "Load a saved game",
                "syntax": "load [filename]",
                "args": ["filename"],
                "optional_args": True,
                "category": "system"
            },
            "saves": {
                "handler": self._cmd_saves,
                "help": "List all available save files",
                "syntax": "saves",
                "category": "system"
            },
            "deletesave": {
                "handler": self._cmd_deletesave,
                "help": "Delete a save file",
                "syntax": "deletesave [filename]",
                "args": ["filename"],
                "category": "system"
            },
            "saveslot": {
                "handler": self._cmd_saveslot,
                "help": "Save to a numbered slot (1-5)",
                "syntax": "saveslot [slot_number]",
                "args": ["slot_number"],
                "category": "system"
            },
            "loadslot": {
                "handler": self._cmd_loadslot,
                "help": "Load from a numbered slot (1-5)",
                "syntax": "loadslot [slot_number]",
                "args": ["slot_number"],
                "category": "system"
            },
            "quests": {
                "handler": self._cmd_quests,
                "help": "Show all quests",
                "syntax": "quests",
                "category": "quests"
            },
            "quest": {
                "handler": self._cmd_quest_detail,
                "help": "Show details for a specific quest",
                "syntax": "quest [quest_id]",
                "args": ["quest_id"],
                "category": "quests"
            },
            "quest_start": {
                "handler": self._cmd_quest_start,
                "help": "Start a quest",
                "syntax": "quest start [quest_id]",
                "args": ["quest_id"],
                "category": "quests"
            },
            "quest_complete": {
                "handler": self._cmd_quest_complete,
                "help": "Complete a quest to get rewards",
                "syntax": "quest complete [quest_id]",
                "args": ["quest_id"],
                "category": "quests"
            },
            "rest": {
                "handler": self._cmd_rest,
                "help": "Rest at an inn to recover health",
                "syntax": "rest",
                "category": "town"
            },
            "notices": {
                "handler": self._cmd_read_notices,
                "help": "Read notices on a notice board",
                "syntax": "notices",
                "category": "town"
            },
            "repair": {
                "handler": self._cmd_repair,
                "help": "Repair a damaged weapon or armor",
                "syntax": "repair [item]",
                "args": ["item"],
                "category": "town"
            },
            "pray": {
                "handler": self._cmd_pray,
                "help": "Pray at a chapel for blessing or healing",
                "syntax": "pray [blessing/healing]",
                "args": ["prayer_type"],
                "optional_args": True,
                "category": "town"
            },
            "gather": {
                "handler": self._cmd_gather,
                "help": "Gather herbs or plants from a garden",
                "syntax": "gather",
                "category": "town"
            },
            "tutorial": {
                "handler": self._cmd_tutorial,
                "help": "Display a beginner's guide to playing MiniMUD",
                "syntax": "tutorial",
                "category": "system"
            },
            "about": {
                "handler": self._cmd_about,
                "help": "Display information about MiniMUD",
                "syntax": "about",
                "category": "system"
            },
            "journal": {
                "handler": self._cmd_journal,
                "help": "View your adventure journal",
                "syntax": "journal [section]",
                "args": ["section"],
                "optional_args": True,
                "category": "journal"
            },
            "journal_quest": {
                "handler": self._cmd_journal_quest,
                "help": "View detailed information about a quest in your journal",
                "syntax": "journal quest [quest_id]",
                "args": ["quest_id"],
                "category": "journal"
            },
            "journal_region": {
                "handler": self._cmd_journal_region,
                "help": "View detailed information about a region in your journal",
                "syntax": "journal region [region_name]",
                "args": ["region_name"],
                "category": "journal"
            },
            "journal_stats": {
                "handler": self._cmd_journal_stats,
                "help": "View your adventure statistics",
                "syntax": "journal stats",
                "category": "journal"
            },
            "journal_achievements": {
                "handler": self._cmd_journal_achievements,
                "help": "View your achievements",
                "syntax": "journal achievements",
                "category": "journal"
            },
            "journal_combat": {
                "handler": self._cmd_journal_combat,
                "help": "View detailed combat statistics",
                "syntax": "journal combat",
                "category": "journal"
            },
            "note": {
                "handler": self._cmd_note,
                "help": "Add a note to your journal",
                "syntax": "note [text]",
                "args": ["text"],
                "category": "journal"
            },
            "quest_note": {
                "handler": self._cmd_quest_note,
                "help": "Add a note about a specific quest",
                "syntax": "quest note [quest_id] [text]",
                "args": ["quest_id", "text"],
                "category": "journal"
            },
            "region_note": {
                "handler": self._cmd_region_note,
                "help": "Add a note about a specific region",
                "syntax": "region note [region_name] [text]",
                "args": ["region_name", "text"],
                "category": "journal"
            },
        }

    def parse(self, command_text):
        """
        Parse and execute a command.
        
        Args:
            command_text (str): The command text to parse
            
        Returns:
            str: The result of the command, or an error message
        """
        command_text = command_text.lower().strip()
        if not command_text:
            return "What would you like to do?"
        
        # Split into parts
        parts = command_text.split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Check for command aliases
        if cmd in self.aliases:
            cmd = self.aliases[cmd]
        
        # Execute the command if it exists
        if cmd in self.commands:
            command_info = self.commands[cmd]
            
            # Check if command requires arguments
            if "args" in command_info and not command_info.get("optional_args", False) and not args:
                arg_name = command_info["args"][0]
                return f"{cmd.capitalize()} what? Please specify a {arg_name}."
            
            # Call the handler with arguments
            return command_info["handler"](args)
        else:
            return f"I don't understand '{command_text}'."
    
    # Command handler methods
    
    def _cmd_look(self, args):
        self.game_state.look()
        return None
    
    def _cmd_go(self, args):
        if not args:
            return "Go where? Please specify a direction."
        
        direction = args[0].lower()
        self.game_state.go(direction)
        return None
    
    def _cmd_take(self, args):
        if not args:
            return "Take what?"
        
        item = " ".join(args)
        self.game_state.take(item)
        return None
    
    def _cmd_inventory(self, args):
        self.game_state.show_inventory()
        return None
    
    def _cmd_recipes(self, args):
        self.game_state.show_recipes()
        return None
    
    def _cmd_craft(self, args):
        if not args:
            return "Craft what?"
        
        item = " ".join(args)
        self.game_state.craft(item)
        return None
    
    def _cmd_use(self, args):
        if not args:
            return "Use what?"
        
        item = " ".join(args)
        # Note: game_state.use method needs to be implemented
        # This would find the item in inventory and call its use method
        item_name = self.game_state.player.find_item(item)
        if not item_name:
            return f"You don't have a {item}."
            
        item_obj = self.game_state.player.get_item(item_name)
        success, message = item_obj.use(self.game_state)
        if success and item_obj.type == "consumable":
            self.game_state.player.remove_from_inventory(item_name)
        self.game_state.add_to_history(message)
        return None
    
    def _cmd_equip(self, args):
        if not args:
            return "Equip what?"
        
        item = " ".join(args)
        self.game_state.equip(item)
        return None
    
    def _cmd_attack(self, args):
        if not args:
            return "Attack what?"
        
        target = " ".join(args)
        enemy = self.game_state.enemy_manager.get_enemy_by_name_in_room(target, self.game_state.current_room)
        if enemy:
            return self.game_state.combat(enemy)
        return f"There is no {target} here to attack."
    
    def _cmd_status(self, args):
        self.game_state.show_status()
        return None
    
    def _cmd_coins(self, args):
        self.game_state.check_coins()
        return None
    
    def _cmd_shop_list(self, args):
        room = self.game_state.world.get_room(self.game_state.current_room)
        if room and room.get("is_shop", False):
            self.game_state.shop_system.display_shop_inventory(self.game_state)
        else:
            return "There's no shop here to list items from."
        return None
    
    def _cmd_buy(self, args):
        if not args:
            return "Buy what?"
        
        item = " ".join(args)
        self.game_state.buy(item)
        return None
    
    def _cmd_sell(self, args):
        if not args:
            return "Sell what?"
        
        item = " ".join(args)
        self.game_state.sell(item)
        return None
    
    def _cmd_region(self, args):
        self.game_state.check_region()
        return None
    
    def _cmd_regions_list(self, args):
        """Command to show all discovered regions"""
        discovered_regions = []
        for region in self.game_state.world.get_all_regions():
            if region.discovered:
                discovered_regions.append(region.display_name)
        
        if discovered_regions:
            self.game_state.add_to_history("Discovered regions:", (180, 180, 255))
            for region_name in discovered_regions:
                self.game_state.add_to_history(f"- {region_name}")
        else:
            self.game_state.add_to_history("You haven't discovered any notable regions yet.")
        return None
    
    def _cmd_weather(self, args):
        """Command to show current weather and effects"""
        current_region = self.game_state.world.get_region_for_room(self.game_state.current_room)
        if current_region:
            weather = current_region.environment_system.get_weather(self.game_state.current_room)
            effects = current_region.environment_system.get_effects(self.game_state.current_room)
            
            self.game_state.add_to_history(f"Current environment: {weather.capitalize()}", (100, 200, 255))
            self.game_state.add_to_history(current_region.environment_system.get_weather_description(self.game_state.current_room), (100, 200, 255))
            
            if effects:
                self.game_state.add_to_history("\nEnvironmental effects:", (100, 200, 255))
                for effect, value in effects.items():
                    if effect == "enemy_accuracy" and value < 0:
                        self.game_state.add_to_history("- Reduced enemy accuracy")
                    elif effect == "player_attack" and value < 0:
                        self.game_state.add_to_history("- Reduced attack effectiveness")
                    elif effect == "enemy_spawn_rate" and value > 1:
                        self.game_state.add_to_history("- Increased enemy activity")
                    elif effect == "healing_bonus" and value > 1:
                        self.game_state.add_to_history("- Enhanced healing effects")
            else:
                self.game_state.add_to_history("No special environmental effects.")
        else:
            self.game_state.add_to_history("Cannot determine the current environment.")
        return None

    def _cmd_help(self, args):
        """Display help for commands with improved formatting and organization"""
        if args:
            # Help for a specific command
            cmd = args[0].lower()
            if cmd in self.aliases:
                cmd = self.aliases[cmd]
                    
            if cmd in self.commands:
                cmd_info = self.commands[cmd]
                self.game_state.add_to_history(f"┏━━━ Command: {cmd} ━━━┓", self.game_state.TITLE_COLOR)
                self.game_state.add_to_history(f"┃ Syntax: {cmd_info['syntax']}")
                self.game_state.add_to_history(f"┃ Description: {cmd_info['help']}")
                
                # Show additional examples or details for specific commands
                if cmd in ["save", "load", "saves", "saveslot", "loadslot", "deletesave", "autosave"]:
                    self._show_detailed_save_help(cmd)
                elif cmd == "repair":
                    self.game_state.add_to_history("\nRepairs damaged weapons and armor to full durability.")
                    self.game_state.add_to_history("Cost: 30% of the item's value in coins.")
                    self.game_state.add_to_history("Only available at the blacksmith in town.")
                elif cmd == "rest":
                    self.game_state.add_to_history("\nRestores your health to maximum.")
                    self.game_state.add_to_history("Cost: 5 coins")
                    self.game_state.add_to_history("Only available at the inn in town.")
                elif cmd == "pray":
                    self.game_state.add_to_history("\nOptions:")
                    self.game_state.add_to_history("  pray blessing - Temporary +2 to attack and defense (10 coins)")
                    self.game_state.add_to_history("  pray healing - Full health restoration (15 coins)")
                    self.game_state.add_to_history("Only available at the chapel in town.")
                elif cmd == "gather":
                    self.game_state.add_to_history("\nCollect herbs and plants from the garden.")
                    self.game_state.add_to_history("Plants regrow over time.")
                    self.game_state.add_to_history("Only available in the garden area.")
                elif cmd == "quests":
                    self.game_state.add_to_history("\nShows your active, available, and completed quests.")
                    self.game_state.add_to_history("Use 'quest [quest_id]' to see details of a specific quest.")
                    self.game_state.add_to_history("Use 'quest start [quest_id]' to begin a quest.")
                    self.game_state.add_to_history("Use 'quest complete [quest_id]' to turn in a completed quest.")
                
                # Show aliases for this command
                cmd_aliases = [alias for alias, target in self.aliases.items() if target == cmd]
                if cmd_aliases:
                    self.game_state.add_to_history(f"┃ Aliases: {', '.join(cmd_aliases)}")
                
                self.game_state.add_to_history(f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
            else:
                self.game_state.add_to_history(f"No help available for '{cmd}'.")
        else:
            # Show categorized help for all commands
            self.game_state.add_to_history("┏━━━━━━━━━━━━━━━ MINIMUD HELP ━━━━━━━━━━━━━━━┓", self.game_state.TITLE_COLOR)
            self.game_state.add_to_history("┃ Type 'help [command]' for detailed information ┃", self.game_state.TITLE_COLOR)
            self.game_state.add_to_history("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛", self.game_state.TITLE_COLOR)
            
            # Define category order and descriptions
            categories = {
                "movement": "Commands for moving around the world",
                "exploration": "Commands for examining your surroundings",
                "items": "Commands for managing items",
                "combat": "Commands for fighting enemies",
                "player": "Commands related to your character",
                "quests": "Commands for managing quests and missions",
                "town": "Town-specific services and interactions",
                "shop": "Commands for buying and selling items",
                "crafting": "Commands for creating items",
                "system": "Game control and save/load commands",
                "other": "Miscellaneous commands"
            }
            
            # Improved display format
            display_format = "  {:<15} - {}"
            
            # Group commands by category
            category_commands = {}
            for cmd, info in self.commands.items():
                if info.get("hidden", False):
                    continue
                    
                category = info.get("category", "other")
                if category not in category_commands:
                    category_commands[category] = []
                category_commands[category].append((cmd, info["help"], info["syntax"]))
            
            # Display commands by category in the defined order
            for category in categories.keys():
                if category in category_commands:
                    self.game_state.add_to_history(f"\n┏━━━ {category.upper()} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓", self.game_state.TITLE_COLOR)
                    self.game_state.add_to_history(f"┃ {categories[category]}", self.game_state.TITLE_COLOR)
                    self.game_state.add_to_history(f"┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛", self.game_state.TITLE_COLOR)
                    
                    for cmd, help_text, syntax in sorted(category_commands[category]):
                        command_display = cmd if len(cmd) <= 15 else cmd[:12] + "..."
                        self.game_state.add_to_history(display_format.format(command_display, help_text))
            
            # Add quick tips at the end
            self.game_state.add_to_history("\n┏━━━ QUICK TIPS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓", self.game_state.TITLE_COLOR)
            self.game_state.add_to_history("┃ • Direction shortcuts: n, s, e, w                ┃")
            self.game_state.add_to_history("┃ • Common shortcuts: l (look), i (inventory)      ┃")
            self.game_state.add_to_history("┃ • Visit the town for shops, rest, and services   ┃")
            self.game_state.add_to_history("┃ • Check 'quests' regularly for new objectives    ┃")
            self.game_state.add_to_history("┃ • Use 'save' often to preserve your progress     ┃")
            self.game_state.add_to_history("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛", self.game_state.TITLE_COLOR)
        
        return None
    
    def _cmd_commands(self, args):
        """Display a compact list of all available commands"""
        self.game_state.add_to_history("┏━━━ AVAILABLE COMMANDS ━━━┓", self.game_state.TITLE_COLOR)
        
        # Group commands by category
        commands_by_category = {}
        for cmd, info in self.commands.items():
            if info.get("hidden", False):
                continue
                
            category = info.get("category", "other")
            if category not in commands_by_category:
                commands_by_category[category] = []
            commands_by_category[category].append(cmd)
        
        # Display commands by category
        for category, cmds in sorted(commands_by_category.items()):
            # Format commands in columns
            command_list = ", ".join(sorted(cmds))
            wrapped_commands = textwrap.wrap(command_list, width=60)
            
            self.game_state.add_to_history(f"┃ {category.upper()}: ", self.game_state.TITLE_COLOR)
            for line in wrapped_commands:
                self.game_state.add_to_history(f"┃   {line}")
        
        self.game_state.add_to_history("┗━━━━━━━━━━━━━━━━━━━━━━━━━┛", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("Type 'help [command]' for details on any command.")
        
        return None

    def _cmd_quit(self, args):
        self.game_state.add_to_history("Thank you for playing MiniMUD!")
        self.game_state.game_over = True
        return None
    
    def _cmd_examine(self, args):
        """Examine an item or enemy in detail"""
        if not args:
            return "Examine what?"
            
        target = " ".join(args)
        
        # First check if it's an item in inventory
        item_name = self.game_state.player.find_item(target)
        if item_name:
            item = self.game_state.player.get_item(item_name)
            self.game_state.add_to_history(f"You examine the {item.display_name()}:", self.game_state.TITLE_COLOR)
            self.game_state.add_to_history(item.description)
            
            # Show special properties based on item type
            if item.type == "weapon":
                self.game_state.add_to_history(f"Attack bonus: +{item.attack_bonus}")
                if item.requirements:
                    self.game_state.add_to_history(f"Requirements: Level {item.requirements.get('level', 1)}")
            elif item.type == "armor":
                self.game_state.add_to_history(f"Defense bonus: +{item.defense_bonus}")
                if item.requirements:
                    self.game_state.add_to_history(f"Requirements: Level {item.requirements.get('level', 1)}")
            elif item.type == "consumable":
                if item.health_restore > 0:
                    self.game_state.add_to_history(f"Restores {item.health_restore} health when consumed.")
                for effect, value in item.effects.items():
                    if effect == "strength":
                        self.game_state.add_to_history(f"Temporarily increases attack by {value}.")
            
            self.game_state.add_to_history(f"Value: {item.value} coins")
            return None
        
        # Check if it's an enemy in the room
        enemy = self.game_state.enemy_manager.get_enemy_by_name_in_room(target, self.game_state.current_room)
        if enemy:
            self.game_state.add_to_history(f"You examine the {enemy.name}:", self.game_state.ENEMY_COLOR)
            self.game_state.add_to_history(f"Health: {enemy.health}/{enemy.max_health}")
            self.game_state.add_to_history(f"Attack power: {enemy.attack}")
            self.game_state.add_to_history(f"Experience value: {enemy.experience}")
            return None
            
        # Check if it's an item in the room
        room = self.game_state.world.get_room(self.game_state.current_room)
        if room and "items" in room:
            for item_name in room["items"]:
                item = self.game_state.ItemFactory.get_item(item_name)
                if item and (target in item.display_name().lower() or any(target in alias.lower() for alias in item.aliases)):
                    self.game_state.add_to_history(f"You examine the {item.display_name()}:", self.game_state.TITLE_COLOR)
                    self.game_state.add_to_history(item.description)
                    return None
        
        return f"You don't see any {target} to examine."
    
    def _cmd_rest(self, args):
        """Rest at an inn to restore health"""
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
        self.game_state.add_to_history(f"Health restored to maximum: {self.game_state.player.health}/{self.game_state.player.max_health} (+{health_restored}).", self.game_state.HEALTH_COLOR)
        
        # Random inn dialogue
        if "inn_dialogue" in room and room["inn_dialogue"]:
            dialogue = random.choice(room["inn_dialogue"])
            self.game_state.add_to_history(f"\n{dialogue}")
        
        return None

    def _cmd_read_notices(self, args):
        """Read notices on a notice board, including available quests"""
        room = self.game_state.world.get_room(self.game_state.current_room)
        if not room or not room.get("is_notice_board", False):
            return "There's no notice board here."
        
        # First show the static notices
        notices = room.get("notices", [])
        if notices:
            self.game_state.add_to_history("You read the posted notices:", self.game_state.TITLE_COLOR)
            for i, notice in enumerate(notices):
                self.game_state.add_to_history(f"{i+1}. {notice}")
            
            self.game_state.add_to_history("")  # Add spacing
        
        # Then show available quests as special notices using the new method
        available_quests = self.game_state.quest_manager.get_quests_for_location(self.game_state.current_room)
        if available_quests:
            self.game_state.add_to_history("You also see some quest postings:", (255, 220, 0))
            
            for quest_id in available_quests:
                quest = self.game_state.quest_manager.get_quest(quest_id)
                if quest:
                    self.game_state.add_to_history(f"• {quest.name}", (255, 220, 0))
                    # Show brief description
                    short_desc = quest.description if len(quest.description) < 80 else quest.description[:77] + "..."
                    self.game_state.add_to_history(f"  {short_desc}")
                    self.game_state.add_to_history(f"  (Type 'quest start {quest_id}' to accept this quest)")
            
            self.game_state.add_to_history("\nType 'quests' to see your current quest log.")
        elif not notices:
            self.game_state.add_to_history("The notice board is empty.")
        
        return None

    def _cmd_repair(self, args):
        """Repair a damaged weapon or armor"""
        if not args:
            return "Repair what?"
        
        room = self.game_state.world.get_room(self.game_state.current_room)
        if not room or not room.get("is_repair", False):
            return "There's nobody here who can repair items."
        
        item_text = " ".join(args).lower()
        
        # Check if player has the item
        item_name = self.game_state.player.find_item(item_text)
        if not item_name:
            return f"You don't have a {item_text} to repair."
        
        item = self.game_state.player.get_item(item_name)
        if not item:
            return f"You can't repair {item_text}."
        
        # Check if item is repairable (has durability)
        if not hasattr(item, 'durability') or item.durability is None:
            return f"The {item.display_name()} doesn't need repairs."
        
        # Check if item is already at max durability
        if item.durability >= item.max_durability:
            return f"The {item.display_name()} is already in perfect condition."
        
        # Calculate repair cost
        repair_cost_multiplier = room.get("repair_cost_multiplier", 0.3)
        repair_cost = max(1, int(item.value * repair_cost_multiplier))
        
        # Check if player has enough coins
        if self.game_state.coins < repair_cost:
            return f"You need {repair_cost} coins to repair the {item.display_name()}, but you only have {self.game_state.coins}."
        
        # Perform the repair
        self.game_state.coins -= repair_cost
        old_durability = item.durability
        item.durability = item.max_durability
        durability_restored = item.durability - old_durability
        
        self.game_state.add_to_history(f"You pay {repair_cost} coins to repair your {item.display_name()}.")
        self.game_state.add_to_history(f"The blacksmith carefully works on your item, restoring it to perfect condition.")
        self.game_state.add_to_history(f"Durability restored: {item.durability}/{item.max_durability} (+{durability_restored}).")
        
        # Random smith dialogue
        if "smith_dialogue" in room and room["smith_dialogue"]:
            dialogue = random.choice(room["smith_dialogue"])
            self.game_state.add_to_history(f"\n{dialogue}")
        
        return None

    def _cmd_pray(self, args):
        """Pray at the chapel for blessing or healing"""
        room = self.game_state.world.get_room(self.game_state.current_room)
        if not room or not room.get("is_chapel", False):
            return "This isn't a place of worship."
        
        if not args:
            self.game_state.add_to_history("You bow your head in prayer, feeling a moment of peace.")
            if "cleric_dialogue" in room and room["cleric_dialogue"]:
                dialogue = random.choice(room["cleric_dialogue"])
                self.game_state.add_to_history(f"\n{dialogue}")
            self.game_state.add_to_history("\nType 'pray blessing' for a temporary stat boost (10 coins).")
            self.game_state.add_to_history("Type 'pray healing' for complete health restoration (15 coins).")
            return None
        
        prayer_type = args[0].lower()
        
        if prayer_type == "blessing":
            blessing_cost = room.get("blessing_cost", 10)
            
            # Check if player has enough coins
            if self.game_state.coins < blessing_cost:
                return f"You need {blessing_cost} coins for a blessing, but you only have {self.game_state.coins}."
            
            # Apply blessing
            self.game_state.coins -= blessing_cost
            self.game_state.player.temp_attack_bonus += 2
            self.game_state.player.temp_defense_bonus += 2
            self.game_state.player.temp_buff_end_time = self.game_state.get_game_time() + 300  # 5 minute blessing
            
            self.game_state.add_to_history(f"You offer {blessing_cost} coins and receive a blessing.")
            self.game_state.add_to_history("You feel divine energy flowing through you, enhancing your abilities.")
            self.game_state.add_to_history("Attack +2, Defense +2 for 5 minutes.", self.game_state.HEALTH_COLOR)
            
        elif prayer_type == "healing":
            healing_cost = room.get("healing_cost", 15)
            
            # Check if player has enough coins
            if self.game_state.coins < healing_cost:
                return f"You need {healing_cost} coins for healing, but you only have {self.game_state.coins}."
            
            # Check if player is already at max health
            if self.game_state.player.health >= self.game_state.player.max_health:
                return "You are already at full health."
            
            # Perform healing
            self.game_state.coins -= healing_cost
            old_health = self.game_state.player.health
            self.game_state.player.health = self.game_state.player.max_health
            health_restored = self.game_state.player.health - old_health
            
            self.game_state.add_to_history(f"You offer {healing_cost} coins for healing prayers.")
            self.game_state.add_to_history("The cleric places his hands on your shoulders, channeling divine energy.")
            self.game_state.add_to_history(f"You feel your wounds closing and your strength returning.")
            self.game_state.add_to_history(f"Health restored to maximum: {self.game_state.player.health}/{self.game_state.player.max_health} (+{health_restored}).", self.game_state.HEALTH_COLOR)
            
        else:
            return f"You can't pray for '{prayer_type}'. Try 'blessing' or 'healing'."
        
        return None

    def _cmd_gather(self, args):
        """Gather herbs or plants from a garden"""
        room = self.game_state.world.get_room(self.game_state.current_room)
        if not room or not room.get("is_garden", False):
            return "There's nothing here to gather."
        
        # Check if garden has any items
        if not room.get("items", []):
            self.game_state.add_to_history("You've already gathered everything that's currently available.")
            self.game_state.add_to_history("The plants need time to regrow.")
            return None
        
        # Get a random herb from the garden
        available_herbs = room.get("items", [])
        if not available_herbs:
            return "There's nothing here to gather."
        
        herb_name = random.choice(available_herbs)
        room["items"].remove(herb_name)
        self.game_state.player.add_to_inventory(herb_name)
        
        # Get the herb object for better messages
        from items.item_factory import ItemFactory
        herb = ItemFactory.get_item(herb_name)
        if herb:
            self.game_state.add_to_history(f"You carefully gather some {herb.display_name()}.")
        else:
            self.game_state.add_to_history(f"You carefully gather some {herb_name.replace('_', ' ')}.")
        
        # Random gardener dialogue
        if "gardener_dialogue" in room and room["gardener_dialogue"]:
            if random.random() < 0.3:  # 30% chance for dialogue
                dialogue = random.choice(room["gardener_dialogue"])
                self.game_state.add_to_history(f"\n{dialogue}")
        
        # Check if garden is now empty
        if not room.get("items", []):
            self.game_state.add_to_history("You've gathered all available plants. They'll need time to regrow.")
            
            # Schedule regrowth
            regrowth_time = room.get("regrowth_time", 300)  # Default 5 minutes
            
            # In a more advanced implementation, you'd use a timer system
            # For now, we'll just set a fixed time and players will need to wait
            self.game_state.add_to_history(f"Check back in a few minutes.")
        
        return None

    def _cmd_drop(self, args):
        """Drop an item from inventory to the current room"""
        if not args:
            return "Drop what?"
            
        item_text = " ".join(args)
        
        # Find item in inventory
        item_name = self.game_state.player.find_item(item_text)
        if not item_name:
            return f"You don't have a {item_text} to drop."
            
        # Get item object for better messaging
        item = self.game_state.player.get_item(item_name)
        
        # Remove from inventory
        self.game_state.player.remove_from_inventory(item_name)
        
        # Add to current room
        room = self.game_state.world.get_room(self.game_state.current_room)
        if "items" not in room:
            room["items"] = []
            
        room["items"].append(item_name)
        
        self.game_state.add_to_history(f"You drop the {item.display_name()}.")
        return None
    
    def _cmd_quests(self, args):
        """Command to show all quests"""
        active = self.game_state.quest_manager.get_active_quests()
        completed = self.game_state.quest_manager.get_completed_quests()
        available = self.game_state.quest_manager.get_available_quests()
        
        if not active and not completed and not available:
            self.game_state.add_to_history("You don't have any quests yet.")
            return None
            
        # Show active quests
        if active:
            self.game_state.add_to_history("Active Quests:", self.game_state.TITLE_COLOR)
            for quest in active:
                self.game_state.add_to_history(f"- {quest.name}", (220, 220, 100))
                
                # Show task progress
                for task_line in quest.get_task_progress():
                    self.game_state.add_to_history(f"  {task_line}")
                    
                # Show quest ready to turn in if completed
                if quest.completed:
                    self.game_state.add_to_history("  COMPLETED - Ready to turn in!", (100, 255, 100))
        
        # Show completed quests
        if completed:
            if active or available:  # Add spacing
                self.game_state.add_to_history("")
                
            self.game_state.add_to_history("Completed Quests:", self.game_state.TITLE_COLOR)
            for quest in completed:
                self.game_state.add_to_history(f"- {quest.name}", (150, 150, 150))
        
        return None

    def _cmd_quest_detail(self, args):
        """Show details about a specific quest"""
        if not args:
            return "Please specify a quest ID or use 'quests' to see all quests."
        
        quest_id = args[0].lower()
        quest = self.game_state.quest_manager.get_quest(quest_id)
        
        if not quest:
            return f"No quest found with ID '{quest_id}'."
        
        self.game_state.add_to_history(f"Quest: {quest.name}", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history(f"Status: {quest.get_status().capitalize()}")
        self.game_state.add_to_history(f"\nDescription: {quest.description}")
        
        # Show tasks
        self.game_state.add_to_history("\nTasks:")
        for task_line in quest.get_task_progress():
            self.game_state.add_to_history(f"- {task_line}")
        
        # Show rewards
        self.game_state.add_to_history("\nRewards:")
        reward_texts = quest.get_rewards_text()
        if reward_texts:
            for reward in reward_texts:
                self.game_state.add_to_history(f"- {reward}")
        else:
            self.game_state.add_to_history("- None")
        
        # Show prerequisites if any
        if quest.prereqs:
            prereq_names = []
            for prereq_id in quest.prereqs:
                prereq = self.game_state.quest_manager.get_quest(prereq_id)
                if prereq:
                    prereq_names.append(prereq.name)
            
            if prereq_names:
                self.game_state.add_to_history("\nRequires completion of:")
                for name in prereq_names:
                    self.game_state.add_to_history(f"- {name}")
        
        return None

    def _cmd_quest_start(self, args):
        """Start a quest"""
        if not args:
            return "Please specify a quest ID to start."
        
        quest_id = args[0].lower()
        success, message = self.game_state.quest_manager.activate_quest(quest_id)
        self.game_state.add_to_history(message)
        
        if success:
            # Show quest details to the player
            self._cmd_quest_detail([quest_id])
            
        return None

    def _cmd_quest_complete(self, args):
        """Complete a quest to get rewards"""
        if not args:
            return "Please specify a quest ID to complete."
        
        quest_id = args[0].lower()
        success, message = self.game_state.quest_manager.complete_quest(quest_id)
        
        if success:
            self.game_state.add_to_history(message, (255, 220, 0))
        else:
            self.game_state.add_to_history(message)
            
        return None

    def _cmd_saveslot(self, args):
        """Save to a numbered slot for quick access"""
        if not args or not args[0].isdigit() or int(args[0]) < 1 or int(args[0]) > 5:
            return "Please specify a slot number between 1 and 5."
        
        slot = int(args[0])
        filename = f"quicksave_slot_{slot}.json"
        
        from datetime import datetime
        import os
        
        # Import the save_game function
        from core.save_load import save_game
        
        result = save_game(self.game_state, filename)
        self.game_state.add_to_history(result)
        return None

    def _cmd_loadslot(self, args):
        """Load from a numbered slot"""
        if not args or not args[0].isdigit() or int(args[0]) < 1 or int(args[0]) > 5:
            return "Please specify a slot number between 1 and 5."
        
        slot = int(args[0])
        filename = f"quicksave_slot_{slot}.json"
        
        # Import the load_game function
        from core.save_load import load_game
        
        success, message = load_game(self.game_state, filename)
        if not success:
            self.game_state.add_to_history(message)
        
        return None

    def _cmd_save(self, args):
        """Command to save the game"""
        # Import needed modules
        import os
        
        # Import the save_game function and utilities
        from core.save_load import save_game
        from core.utils import get_timestamp, ensure_dir_exists
        
        if args:
            filename = args[0]
            if not filename.endswith(".json"):
                filename += ".json"
        else:
            # Generate default filename with timestamp
            timestamp = get_timestamp()
            filename = f"minimud_save_{timestamp}.json"
        
        result = save_game(self.game_state, filename)
        self.game_state.add_to_history(result)
        return None

    def _cmd_load(self, args):
        """Command to load a saved game"""
        # Import the load_game and list_saves functions
        from core.save_load import load_game, list_saves
        
        if not args:
            # If no filename provided, list available saves
            saves = list_saves()
            if not saves:
                self.game_state.add_to_history("No save files found.")
                return None
            
            self.game_state.add_to_history("Available save files:", self.game_state.TITLE_COLOR)
            for i, save in enumerate(saves):
                self.game_state.add_to_history(f"{i+1}. {save['filename']} - Level {save['level']} at {save['location']} ({save['date']})")
            self.game_state.add_to_history("\nUse 'load [filename]' to load a specific save file.")
            return None
        
        filename = args[0]
        if not filename.endswith(".json"):
            filename += ".json"
            
        success, message = load_game(self.game_state, filename)
        if not success:
            self.game_state.add_to_history(message)
        
        return None

    def _cmd_saves(self, args):
        """Command to list available save files"""
        # Import the list_saves function
        from core.save_load import list_saves
        
        saves = list_saves()
        if not saves:
            self.game_state.add_to_history("No save files found.")
            return None
        
        self.game_state.add_to_history("Available save files:", self.game_state.TITLE_COLOR)
        for i, save in enumerate(saves):
            self.game_state.add_to_history(f"{i+1}. {save['filename']} - Level {save['level']} at {save['location']} ({save['date']})")
        
        self.game_state.add_to_history("\nUse 'load [filename]' to load a save, or 'deletesave [filename]' to delete.")
        return None

    def _cmd_deletesave(self, args):
        """Command to delete a save file"""
        # Import the delete_save function
        from core.save_load import delete_save, list_saves
        
        if not args:
            self.game_state.add_to_history("Please specify a save file to delete.")
            self.game_state.add_to_history("Use 'saves' to list available save files.")
            return None
        
        filename = args[0]
        if not filename.endswith(".json"):
            filename += ".json"
            
        success, message = delete_save(filename)
        self.game_state.add_to_history(message)
        
        return None

    def _cmd_autosave(self, args):
        """Toggle automatic saving on/off or adjust autosave settings"""
        # Import the AutosaveSettings class
        from core.save_load import AutosaveSettings
        
        if not args:
            # Display current status
            status = AutosaveSettings.get_status()
            
            self.game_state.add_to_history(f"Auto-save is currently {'enabled' if status['enabled'] else 'disabled'}.", self.game_state.TITLE_COLOR)
            
            # Show more details if enabled
            if status['enabled']:
                self.game_state.add_to_history(f"Interval: {status['interval_text']}")
                self.game_state.add_to_history(f"Next autosave in: {status['time_until_next_text']}")
                self.game_state.add_to_history(f"Using slot: {status['next_slot']} of {AutosaveSettings.max_slots}")
            
            self.game_state.add_to_history("\nCommands:")
            self.game_state.add_to_history("  autosave on - Enable automatic saving")
            self.game_state.add_to_history("  autosave off - Disable automatic saving")
            self.game_state.add_to_history("  autosave interval [minutes] - Set the autosave interval")
            return None
        
        # Process commands
        command = args[0].lower()
        
        if command in ["on", "true", "yes", "enable", "enabled"]:
            AutosaveSettings.toggle(True)
            self.game_state.add_to_history("Auto-save enabled. Game will save automatically when safe.")
            
        elif command in ["off", "false", "no", "disable", "disabled"]:
            AutosaveSettings.toggle(False)
            self.game_state.add_to_history("Auto-save disabled. Use 'save' command to save manually.")
            
        elif command == "interval" and len(args) > 1:
            try:
                minutes = int(args[1])
                if minutes < 1:
                    self.game_state.add_to_history("Interval must be at least 1 minute.")
                elif minutes > 60:
                    self.game_state.add_to_history("Interval cannot be more than 60 minutes.")
                else:
                    AutosaveSettings.set_interval(minutes)
                    self.game_state.add_to_history(f"Autosave interval set to {minutes} minutes.")
            except ValueError:
                self.game_state.add_to_history(f"Invalid interval: '{args[1]}'. Please use a number of minutes.")
                
        elif command == "slots" and len(args) > 1:
            try:
                slots = int(args[1])
                if slots < 1:
                    self.game_state.add_to_history("Must have at least 1 autosave slot.")
                elif slots > 10:
                    self.game_state.add_to_history("Cannot have more than 10 autosave slots.")
                else:
                    AutosaveSettings.max_slots = slots
                    self.game_state.add_to_history(f"Autosave slots set to {slots}.")
            except ValueError:
                self.game_state.add_to_history(f"Invalid slot count: '{args[1]}'. Please use a number.")
                
        elif command == "now":
            # Force an immediate autosave
            from core.save_load import save_game
            
            # Make sure autosave directory exists
            from core.utils import ensure_dir_exists
            ensure_dir_exists(AutosaveSettings.autosave_dir)
            
            # Get the autosave filename
            autosave_path = AutosaveSettings.get_autosave_filename()
            
            # Do the save
            save_game(self.game_state, autosave_path)
            
            # Mark the save time
            AutosaveSettings.mark_saved()

            self.game_state.add_to_history(f"Game saved to {os.path.basename(autosave_path)}")
            
        else:
            # Show help for invalid commands
            self.game_state.add_to_history("Invalid command. Use one of:")
            self.game_state.add_to_history("  autosave - Show current status")
            self.game_state.add_to_history("  autosave on/off - Enable/disable automatic saving")
            self.game_state.add_to_history("  autosave interval [minutes] - Set the autosave interval")
            self.game_state.add_to_history("  autosave slots [number] - Set number of autosave slots")
            self.game_state.add_to_history("  autosave now - Force an immediate autosave")
        
        return None

    def _show_detailed_save_help(self, cmd):
        """Show detailed help for save/load commands with improved formatting"""
        if cmd == "save":
            self.game_state.add_to_history("\nUsage examples:")
            self.game_state.add_to_history("  • save - Creates a save file with timestamp")
            self.game_state.add_to_history("    Example: minimud_save_20250317_123045.json")
            self.game_state.add_to_history("  • save mygame - Creates a save file named 'mygame.json'")
            self.game_state.add_to_history("\nSave files are stored in the 'saves' directory.")
            
        elif cmd == "load":
            self.game_state.add_to_history("\nUsage examples:")
            self.game_state.add_to_history("  • load - Lists all available save files")
            self.game_state.add_to_history("  • load mygame - Loads 'mygame.json'")
            self.game_state.add_to_history("\nIf the file isn't found, check the 'saves' directory.")
            
        elif cmd == "saves":
            self.game_state.add_to_history("\nLists all available save files with details:")
            self.game_state.add_to_history("  • Filename")
            self.game_state.add_to_history("  • Character level")
            self.game_state.add_to_history("  • Current location")
            self.game_state.add_to_history("  • Save date and time")
            
        elif cmd == "saveslot":
            self.game_state.add_to_history("\nQuick-save to numbered slots (1-5):")
            self.game_state.add_to_history("  • saveslot 1 - Saves to slot 1 (quicksave_slot_1.json)")
            self.game_state.add_to_history("  • saveslot 3 - Saves to slot 3 (quicksave_slot_3.json)")
            self.game_state.add_to_history("\nUseful for creating multiple save points.")
            
        elif cmd == "loadslot":
            self.game_state.add_to_history("\nQuick-load from numbered slots (1-5):")
            self.game_state.add_to_history("  • loadslot 1 - Loads from slot 1 (quicksave_slot_1.json)")
            self.game_state.add_to_history("  • loadslot 3 - Loads from slot 3 (quicksave_slot_3.json)")
            
        elif cmd == "deletesave":
            self.game_state.add_to_history("\nDeletes a save file permanently:")
            self.game_state.add_to_history("  • deletesave mygame - Deletes 'mygame.json'")
            self.game_state.add_to_history("\nUse with caution - deleted saves cannot be recovered!")
            
        elif cmd == "autosave":
            self.game_state.add_to_history("\nControls automatic saving of your game:")
            self.game_state.add_to_history("  • autosave - Shows current autosave status")
            self.game_state.add_to_history("  • autosave on - Enables automatic saving")
            self.game_state.add_to_history("  • autosave off - Disables automatic saving")
            self.game_state.add_to_history("\nWhen enabled, the game automatically saves every 5 minutes.")

    # Add a new tutorial command for new players
    def _cmd_tutorial(self, args):
        """Display a basic tutorial for new players"""
        self.game_state.add_to_history("┏━━━━━━━━━━━━━━━ MINIMUD TUTORIAL ━━━━━━━━━━━━━━━┓", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("┃ Welcome to MiniMUD! Here's how to get started:  ┃", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛", self.game_state.TITLE_COLOR)
        
        # Basic movement
        self.game_state.add_to_history("\n┏━━━ MOVEMENT ━━━┓", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("• Type direction commands to move: north, south, east, west")
        self.game_state.add_to_history("• Shortcuts: n, s, e, w")
        self.game_state.add_to_history("• Example: 'north' or 'n' to go north")
        self.game_state.add_to_history("• Use 'look' or 'l' to see your surroundings")
        
        # Basic interaction
        self.game_state.add_to_history("\n┏━━━ INTERACTION ━━━┓", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("• Use 'take [item]' to pick up objects")
        self.game_state.add_to_history("• Use 'inventory' or 'i' to see what you're carrying")
        self.game_state.add_to_history("• Use 'examine [item]' to look at something in detail")
        self.game_state.add_to_history("• Use 'drop [item]' to discard unwanted items")
        
        # Combat
        self.game_state.add_to_history("\n┏━━━ COMBAT ━━━┓", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("• Use 'attack [enemy]' or 'a [enemy]' to fight")
        self.game_state.add_to_history("• Equip weapons and armor with 'equip [item]'")
        self.game_state.add_to_history("• Use healing potions with 'use healing_potion'")
        self.game_state.add_to_history("• Check your stats with 'status' or 'stats'")
        
        # Town
        self.game_state.add_to_history("\n┏━━━ TOWN SERVICES ━━━┓", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("• Shop: Buy/sell items with 'buy [item]' and 'sell [item]'")
        self.game_state.add_to_history("• Inn: Restore health with 'rest'")
        self.game_state.add_to_history("• Blacksmith: Repair equipment with 'repair [item]'")
        self.game_state.add_to_history("• Chapel: Get buffs with 'pray blessing' or healing with 'pray healing'")
        self.game_state.add_to_history("• Garden: Collect crafting ingredients with 'gather'")
        
        # Quests
        self.game_state.add_to_history("\n┏━━━ QUESTS ━━━┓", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("• Check available quests with 'quests'")
        self.game_state.add_to_history("• View details with 'quest [quest_id]'")
        self.game_state.add_to_history("• Start a quest with 'quest start [quest_id]'")
        self.game_state.add_to_history("• Complete a quest with 'quest complete [quest_id]'")
        
        # Saving/Loading
        self.game_state.add_to_history("\n┏━━━ SAVING & LOADING ━━━┓", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("• Save your game with 'save [filename]'")
        self.game_state.add_to_history("• Load a saved game with 'load [filename]'")
        self.game_state.add_to_history("• Quick slots: 'saveslot 1' and 'loadslot 1'")
        
        # Final tips
        self.game_state.add_to_history("\n┏━━━ FINAL TIPS ━━━┓", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("• Use 'help' to see all available commands")
        self.game_state.add_to_history("• Use 'help [command]' for specific command help")
        self.game_state.add_to_history("• Save often to avoid losing progress")
        self.game_state.add_to_history("• Explore widely - there are many secrets to discover!")
        self.game_state.add_to_history("• Have fun adventuring in MiniMUD!")
        
        return None

    def _cmd_about(self, args):
        """Display information about MiniMUD"""
        self.game_state.add_to_history("┏━━━━━━━━━━━━━━━ ABOUT MINIMUD ━━━━━━━━━━━━━━━┓", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("┃ A text-based RPG adventure in a mysterious cave ┃", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛", self.game_state.TITLE_COLOR)
        
        self.game_state.add_to_history("\nMiniMUD is a text-based role-playing game where you explore")
        self.game_state.add_to_history("a mysterious cave system, fight enemies, collect treasure,")
        self.game_state.add_to_history("and complete quests in a classic dungeon adventure.")
        
        self.game_state.add_to_history("\nFeatures:")
        self.game_state.add_to_history("• Interactive text-based world exploration")
        self.game_state.add_to_history("• Combat system with various enemies")
        self.game_state.add_to_history("• Equipment system with weapons and armor")
        self.game_state.add_to_history("• Item collection and inventory management")
        self.game_state.add_to_history("• Town with shops and services")
        self.game_state.add_to_history("• Quest system with rewards")
        self.game_state.add_to_history("• Environmental effects and dynamic weather")
        self.game_state.add_to_history("• Save/load system for game progression")
        
        import datetime
        current_year = datetime.datetime.now().year
        
        self.game_state.add_to_history(f"\nMiniMUD © {current_year} - All Rights Reserved")
        self.game_state.add_to_history("Created with ♥ for text adventure gaming")
        
        return None

    def _cmd_journal(self, args):
        """Display the player's journal"""
        if not args:
            # Show main journal menu
            self.game_state.add_to_history("ADVENTURE JOURNAL", self.game_state.TITLE_COLOR)
            self.game_state.add_to_history("Select a section to view:", self.game_state.TITLE_COLOR)
            self.game_state.add_to_history("  journal entries - View recent journal entries")
            self.game_state.add_to_history("  journal quests - View your quest log")
            self.game_state.add_to_history("  journal regions - View discovered regions")
            self.game_state.add_to_history("  journal stats - View your adventure statistics")
            self.game_state.add_to_history("  journal achievements - View your achievements")
            self.game_state.add_to_history("  journal combat - View detailed combat statistics")
            self.game_state.add_to_history("")
            self.game_state.add_to_history("Use 'note [text]' to add a general note to your journal")
            self.game_state.add_to_history("Use 'quest note [quest_id] [text]' to add a note about a quest")
            self.game_state.add_to_history("Use 'region note [region_name] [text]' to add a note about a region")
            return None
        
        section = args[0].lower()
        
        if section == "entries":
            # Show recent journal entries
            entries = self.game_state.journal.get_recent_entries(10)
            
            if not entries:
                self.game_state.add_to_history("Your journal is empty. Start your adventure!")
                return None
            
            self.game_state.add_to_history("RECENT JOURNAL ENTRIES", self.game_state.TITLE_COLOR)
            for entry in entries:
                timestamp = entry.get("timestamp", "")
                text = entry.get("text", "")
                category = entry.get("category", "general")
                
                category_display = f"[{category.capitalize()}]" if category != "general" else ""
                self.game_state.add_to_history(f"{timestamp} {category_display}")
                self.game_state.add_to_history(f"  {text}")
                self.game_state.add_to_history("")
        
        elif section == "quests":
            # Show quest log
            quest_log = self.game_state.journal.get_quest_log()
            
            active_quests = quest_log.get("active", [])
            completed_quests = quest_log.get("completed", [])
            
            if not active_quests and not completed_quests:
                self.game_state.add_to_history("You haven't accepted any quests yet.")
                return None
            
            self.game_state.add_to_history("QUEST LOG", self.game_state.TITLE_COLOR)
            
            # Show active quests
            if active_quests:
                self.game_state.add_to_history("Active Quests:", self.game_state.TITLE_COLOR)
                for quest in active_quests:
                    status = "(Ready to turn in!)" if quest.get("completed", False) else ""
                    self.game_state.add_to_history(f"• {quest['name']} [{quest['id']}] {status}")
                    
                    # Show progress
                    progress = quest.get("progress", [])
                    if progress:
                        for task in progress:
                            self.game_state.add_to_history(f"  {task}")
                    
                    # Show notes count
                    notes = quest.get("notes", [])
                    if notes:
                        self.game_state.add_to_history(f"  Notes: {len(notes)} (Use 'journal quest {quest['id']}' to view)")
                    
                    self.game_state.add_to_history("")
            
            # Show completed quests
            if completed_quests:
                self.game_state.add_to_history("Completed Quests:", self.game_state.TITLE_COLOR)
                for quest in completed_quests:
                    self.game_state.add_to_history(f"• {quest['name']} [{quest['id']}] (Completed)")
                    
                    # Show notes count
                    notes = quest.get("notes", [])
                    if notes:
                        self.game_state.add_to_history(f"  Notes: {len(notes)} (Use 'journal quest {quest['id']}' to view)")
                
                self.game_state.add_to_history("")
            
            self.game_state.add_to_history("Use 'journal quest [quest_id]' to view details for a specific quest")
        
        elif section == "regions":
            # Show region log
            region_log = self.game_state.journal.get_region_log()
            
            if not region_log:
                self.game_state.add_to_history("You haven't discovered any regions yet.")
                return None
            
            self.game_state.add_to_history("DISCOVERED REGIONS", self.game_state.TITLE_COLOR)
            
            for region_name, region in region_log.items():
                self.game_state.add_to_history(f"• {region['display_name']} [{region_name}]")
                
                # Show number of rooms visited
                rooms_visited = len(region.get("rooms_visited", []))
                total_rooms = len(self.game_state.world.get_region(region_name).get_all_room_names())
                self.game_state.add_to_history(f"  Exploration: {rooms_visited}/{total_rooms} areas")
                
                # Show notes count
                notes = region.get("notes", [])
                if notes:
                    self.game_state.add_to_history(f"  Notes: {len(notes)} (Use 'journal region {region_name}' to view)")
                
                self.game_state.add_to_history("")
            
            self.game_state.add_to_history("Use 'journal region [region_name]' to view details for a specific region")
        
        elif section == "stats":
            return self._cmd_journal_stats([])
        
        elif section == "achievements":
            return self._cmd_journal_achievements([])
        
        else:
            self.game_state.add_to_history(f"Unknown journal section: '{section}'")
            self.game_state.add_to_history("Valid sections: entries, quests, regions, stats, achievements")
        
        return None

    def _cmd_journal_quest(self, args):
        """Show detailed information about a specific quest"""
        if not args:
            self.game_state.add_to_history("Please specify a quest ID.")
            self.game_state.add_to_history("Use 'journal quests' to view all quests.")
            return None
        
        quest_id = args[0].lower()
        quest = self.game_state.quest_manager.get_quest(quest_id)
        
        if not quest:
            self.game_state.add_to_history(f"No quest found with ID '{quest_id}'.")
            return None
        
        # Get quest notes
        quest_notes = self.game_state.journal.quest_notes.get(quest_id, [])
        
        # Show quest details
        self.game_state.add_to_history(f"QUEST: {quest.name}", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history(f"Status: {quest.get_status().capitalize()}")
        
        # Quest description
        self.game_state.add_to_history("\nDescription:")
        desc_lines = textwrap.wrap(quest.description, width=60)
        for line in desc_lines:
            self.game_state.add_to_history(f"  {line}")
        
        # Quest progress/tasks
        if quest.active and not quest.completed:
            self.game_state.add_to_history("\nTasks:")
            for task in quest.get_task_progress():
                self.game_state.add_to_history(f"  {task}")
        
        # Quest rewards
        self.game_state.add_to_history("\nRewards:")
        reward_texts = quest.get_rewards_text()
        if reward_texts:
            for reward in reward_texts:
                self.game_state.add_to_history(f"  - {reward}")
        else:
            self.game_state.add_to_history("  None")
        
        # Quest notes
        if quest_notes:
            self.game_state.add_to_history("\nYour Notes:")
            for note in quest_notes:
                timestamp = note.get("timestamp", "")
                text = note.get("text", "")
                self.game_state.add_to_history(f"  {timestamp}: {text}")
        
        return None

    def _cmd_journal_region(self, args):
        """Show detailed information about a specific region"""
        if not args:
            self.game_state.add_to_history("Please specify a region name.")
            self.game_state.add_to_history("Use 'journal regions' to view all regions.")
            return None
        
        region_name = args[0].lower()
        region = self.game_state.world.get_region(region_name)
        
        if not region or not region.discovered:
            self.game_state.add_to_history(f"No discovered region found with name '{region_name}'.")
            return None
        
        # Get region notes
        region_notes = self.game_state.journal.region_notes.get(region_name, [])
        
        # Show region details
        self.game_state.add_to_history(f"REGION: {region.display_name}", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history(f"Type: {region.region_type.replace('_', ' ').title()}")
        
        # Region description
        self.game_state.add_to_history("\nDescription:")
        desc_lines = textwrap.wrap(region.description, width=60)
        for line in desc_lines:
            self.game_state.add_to_history(f"  {line}")
        
        # Discovered rooms
        self.game_state.add_to_history("\nDiscovered Areas:")
        for room_name in region.get_all_room_names():
            # We don't track room discovery directly, so assume all rooms in discovered regions are known
            room_desc = self.game_state.world.get_room(room_name).get("description", "")
            short_desc = room_desc[:40] + "..." if len(room_desc) > 40 else room_desc
            self.game_state.add_to_history(f"  • {room_name.replace('_', ' ').title()} - {short_desc}")
        
        # Environment tendencies
        env_bias = region.get_environment_bias()
        if env_bias:
            self.game_state.add_to_history("\nEnvironmental Tendencies:")
            for weather, bias in env_bias.items():
                if bias > 1.0:
                    self.game_state.add_to_history(f"  • {weather.capitalize()} conditions are common here")
        
        # Region notes
        if region_notes:
            self.game_state.add_to_history("\nYour Notes:")
            for note in region_notes:
                timestamp = note.get("timestamp", "")
                text = note.get("text", "")
                self.game_state.add_to_history(f"  {timestamp}: {text}")
        
        return None

    def _cmd_journal_stats(self, args):
        """Show player statistics"""
        stats = self.game_state.journal.get_stats_summary()
        
        self.game_state.add_to_history("ADVENTURE STATISTICS", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history(f"Play Time: {stats['play_time']}")
        self.game_state.add_to_history(f"Coins Earned: {stats['coins_earned']}")
        self.game_state.add_to_history(f"Distance Traveled: {stats['distance_traveled']} areas")
        self.game_state.add_to_history(f"Regions Discovered: {stats['regions_discovered']}")
        self.game_state.add_to_history(f"Quests Completed: {stats['quests_completed']}")
        
        # Enemy statistics
        self.game_state.add_to_history(f"\nEnemies Defeated: {stats['enemies_killed']}")
        if stats['enemies_by_type']:
            for enemy_type, count in stats['enemies_by_type'].items():
                self.game_state.add_to_history(f"  • {enemy_type.capitalize()}: {count}")
        
        # Item statistics
        self.game_state.add_to_history(f"\nItems Collected: {stats['items_collected']}")
        if stats['items_by_type']:
            item_types = sorted(stats['items_by_type'].items(), key=lambda x: x[1], reverse=True)
            for item_type, count in item_types[:5]:  # Show top 5 items
                item_display = item_type.replace('_', ' ').title()
                self.game_state.add_to_history(f"  • {item_display}: {count}")
            
            if len(item_types) > 5:
                self.game_state.add_to_history(f"  • ... and {len(item_types) - 5} more item types")
        
        return None

    def _cmd_journal_achievements(self, args):
        """Show player achievements"""
        achievements = self.game_state.journal.achievements
        
        if not achievements:
            self.game_state.add_to_history("You haven't earned any achievements yet. Keep exploring!")
            return None
        
        self.game_state.add_to_history("ACHIEVEMENTS", self.game_state.TITLE_COLOR)
        
        for achievement in achievements:
            timestamp = achievement.get("timestamp", "")
            title = achievement.get("title", "")
            description = achievement.get("description", "")
            
            self.game_state.add_to_history(f"• {title} - {timestamp}")
            self.game_state.add_to_history(f"  {description}")
        
        return None

    def _cmd_note(self, args):
        """Add a general note to the journal"""
        if not args:
            self.game_state.add_to_history("What would you like to note? Please provide some text.")
            return None
        
        note_text = " ".join(args)
        entry = self.game_state.journal.add_entry(note_text)
        self.game_state.add_to_history(f"Note added to your journal at {entry['timestamp']}.")
        return None

    def _cmd_quest_note(self, args):
        """Add a note about a specific quest"""
        if len(args) < 2:
            self.game_state.add_to_history("Please specify a quest ID and note text.")
            self.game_state.add_to_history("Usage: quest note [quest_id] [text]")
            return None
        
        quest_id = args[0].lower()
        note_text = " ".join(args[1:])
        
        quest = self.game_state.quest_manager.get_quest(quest_id)
        if not quest:
            self.game_state.add_to_history(f"No quest found with ID '{quest_id}'.")
            return None
        
        entry = self.game_state.journal.add_quest_note(quest_id, note_text)
        self.game_state.add_to_history(f"Note added to quest '{quest.name}' at {entry['timestamp']}.")
        return None

    def _cmd_region_note(self, args):
        """Add a note about a specific region"""
        if len(args) < 2:
            self.game_state.add_to_history("Please specify a region name and note text.")
            self.game_state.add_to_history("Usage: region note [region_name] [text]")
            return None
        
        region_name = args[0].lower()
        note_text = " ".join(args[1:])
        
        region = self.game_state.world.get_region(region_name)
        if not region or not region.discovered:
            self.game_state.add_to_history(f"No discovered region found with name '{region_name}'.")
            return None
        
        entry = self.game_state.journal.add_region_note(region_name, note_text)
        self.game_state.add_to_history(f"Note added to region '{region.display_name}' at {entry['timestamp']}.")
        return None

    def _cmd_journal_combat(self, args):
        """Display detailed combat statistics"""
        combat_stats = self.game_state.journal.get_combat_stats()
        
        self.game_state.add_to_history("COMBAT STATISTICS", self.game_state.TITLE_COLOR)
        self.game_state.add_to_history(f"Total Battles: {combat_stats['total_battles']}")
        self.game_state.add_to_history(f"Victories: {combat_stats['victories']}")
        self.game_state.add_to_history(f"Defeats: {combat_stats['defeats']}")
        self.game_state.add_to_history(f"Win Rate: {combat_stats['win_rate']}")
        
        self.game_state.add_to_history("\nCombat Performance:")
        self.game_state.add_to_history(f"Total Damage Dealt: {combat_stats['damage_dealt']}")
        self.game_state.add_to_history(f"Total Damage Taken: {combat_stats['damage_taken']}")
        self.game_state.add_to_history(f"Critical Hits: {combat_stats['critical_hits']}")
        self.game_state.add_to_history(f"Near Death Escapes: {combat_stats['near_death_escapes']}")
        
        if combat_stats['top_enemies']:
            self.game_state.add_to_history("\nMost Encountered Enemies:", self.game_state.ENEMY_COLOR)
            for enemy in combat_stats['top_enemies']:
                self.game_state.add_to_history(f"• {enemy['name'].capitalize()}:")
                self.game_state.add_to_history(f"  Battles: {enemy['battles']}, Victories: {enemy['victories']} ({enemy['win_rate']})")
                self.game_state.add_to_history(f"  Damage Dealt: {enemy['damage_dealt']}, Damage Taken: {enemy['damage_taken']}")
        
        return None
