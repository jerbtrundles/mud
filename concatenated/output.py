#!/usr/bin/env python3
# main.py - Main entry point for MiniMUD game

import sys
import traceback

from core.game_init import initialize_game
from core.game_loop import GameLoop

def main():
    """Main entry point for the game"""
    try:
        # Initialize all game components
        world, player, game_state, command_parser, enemy_manager = initialize_game()
        
        # Create and run the game loop
        game_loop = GameLoop(game_state, command_parser, enemy_manager, world)
        game_loop.run()
        
    except Exception as e:
        # Handle unexpected errors gracefully
        print("An error occurred:")
        print(str(e))
        traceback.print_exc()
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())

# autosave.py
# AutosaveSettings for save_load.py
import time
import os
from core.utils import ensure_dir_exists, format_time_delta

class AutosaveSettings:
    """Global settings for autosave functionality"""
    last_autosave_time = time.time()
    autosave_interval = 300  # 5 minutes (in seconds)
    backup_interval = 3600   # 1 hour (in seconds)
    enabled = True
    max_slots = 3
    autosave_dir = "saves/autosaves"
    
    @classmethod
    def initialize(cls):
        """Initialize autosave system, creating necessary directories"""
        ensure_dir_exists(cls.autosave_dir)
        return cls
    
    @classmethod
    def toggle(cls, enable=None):
        """
        Toggle or set autosave functionality
        
        Args:
            enable (bool, optional): If provided, set to this value; if None, toggle current value
            
        Returns:
            bool: The new enabled state
        """
        if enable is None:
            cls.enabled = not cls.enabled
        else:
            cls.enabled = bool(enable)
        return cls.enabled
    
    @classmethod
    def set_interval(cls, minutes):
        """
        Set autosave interval in minutes
        
        Args:
            minutes (int): Minutes between autosaves
            
        Returns:
            int: The new interval in seconds
        """
        # Limit to reasonable values
        if minutes < 1:
            minutes = 1
        elif minutes > 60:
            minutes = 60
            
        cls.autosave_interval = minutes * 60
        return cls.autosave_interval
    
    @classmethod
    def get_next_slot(cls):
        """
        Get the next autosave slot number
        
        Returns:
            int: Slot number (1 to max_slots)
        """
        slot = int((time.time() // cls.autosave_interval) % cls.max_slots) + 1
        return slot
    
    @classmethod
    def get_autosave_filename(cls, slot=None):
        """
        Get the filename for an autosave slot
        
        Args:
            slot (int, optional): Slot number, or None for next slot
            
        Returns:
            str: Autosave filename
        """
        if slot is None:
            slot = cls.get_next_slot()
            
        return os.path.join(cls.autosave_dir, f"autosave_{slot}.json")
    
    @classmethod
    def get_backup_filename(cls):
        """
        Get a unique backup filename with timestamp
        
        Returns:
            str: Backup filename
        """
        from core.utils import get_timestamp
        return os.path.join(cls.autosave_dir, f"backup_{get_timestamp()}.json")
    
    @classmethod
    def should_autosave(cls, current_time=None):
        """
        Check if it's time to perform an autosave
        
        Args:
            current_time (float, optional): Current time, or None to use time.time()
            
        Returns:
            bool: True if autosave should be performed
        """
        if not cls.enabled:
            return False
            
        if current_time is None:
            current_time = time.time()
            
        return (current_time - cls.last_autosave_time) >= cls.autosave_interval
    
    @classmethod
    def should_backup(cls, current_time=None):
        """
        Check if it's time to perform a backup
        
        Args:
            current_time (float, optional): Current time, or None to use time.time()
            
        Returns:
            bool: True if backup should be performed
        """
        if not cls.enabled:
            return False
            
        if current_time is None:
            current_time = time.time()
            
        return (current_time - cls.last_autosave_time) >= cls.backup_interval
    
    @classmethod
    def mark_saved(cls, current_time=None):
        """
        Mark the current time as the last autosave time
        
        Args:
            current_time (float, optional): Current time, or None to use time.time()
        """
        if current_time is None:
            current_time = time.time()
            
        cls.last_autosave_time = current_time
    
    @classmethod
    def get_status(cls):
        """
        Get the current status of autosave functionality
        
        Returns:
            dict: Status information
        """
        current_time = time.time()
        next_save_time = cls.last_autosave_time + cls.autosave_interval if cls.enabled else None
        time_until_next = max(0, next_save_time - current_time) if next_save_time else None
        
        return {
            "enabled": cls.enabled,
            "interval_seconds": cls.autosave_interval,
            "interval_text": format_time_delta(cls.autosave_interval),
            "next_save_time": next_save_time,
            "time_until_next": time_until_next,
            "time_until_next_text": format_time_delta(time_until_next) if time_until_next else "N/A",
            "last_save_time": cls.last_autosave_time,
            "next_slot": cls.get_next_slot()
        }

# config.py
class GameConfig:
    """Centralized game configuration settings"""
    # Display settings
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 650
    BG_COLOR = (0, 0, 0)
    
    # Text colors
    TEXT_COLOR = (200, 200, 200)
    TITLE_COLOR = (255, 255, 100)
    ENEMY_COLOR = (255, 100, 100)
    COMBAT_COLOR = (255, 165, 0)
    HEALTH_COLOR = (100, 255, 100)
    INPUT_COLOR = (100, 255, 100)

    # Game balance
    MAX_ENEMIES = 1
    ENEMY_MOVE_INTERVAL = 15  # seconds
    RESPAWN_DELAY = 60  # seconds
    
    # Enemy spawn chances
    BASE_SPAWN_CHANCE = 0.7
    MAX_SPAWN_CHANCE = 0.95

    # Other constants
    FONT_SIZE = 20
    LINE_SPACING = 5
    MARGIN = 20
    INPUT_MARKER = "> "
    MAX_LINES_DISPLAYED = 22
    SCROLL_AMOUNT = 5
    INPUT_AREA_HEIGHT = 40

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

# game_init.py
import pygame

from entities.player import Player
from core.game_state import GameState
from world.world import GameWorld
from entities.enemy_manager import EnemyManager
from core.command_parser import CommandParser

def initialize_items():
    """Pre-initialize all item classes to ensure they're ready for use"""
    from items.weapon import WEAPONS
    from items.armor import ARMORS
    from items.consumable import CONSUMABLES
    from items.treasure import GEMS, QUEST_ITEMS, KEYS, TOOLS
    
    # Just access each dictionary to ensure all classes are loaded
    print(f"Game loaded with {len(WEAPONS)} weapons, {len(ARMORS)} armor types, " 
          f"{len(CONSUMABLES)} consumables, and {len(GEMS) + len(QUEST_ITEMS) + len(KEYS) + len(TOOLS)} special items.")

def initialize_game():
    """Initialize all game components and return them"""
    # Initialize pygame
    pygame.init()
    
    # Initialize item system
    initialize_items()
    
    # Create world
    world = GameWorld()
    
    # Create player
    player = Player()
    
    # Create game state
    game_state = GameState(world, player)

    # Create command parser
    command_parser = CommandParser(game_state)
    
    # Create enemy manager
    enemy_manager = EnemyManager(world)
    enemy_manager.set_game_state(game_state)
    game_state.set_enemy_manager(enemy_manager)
    
    return world, player, game_state, command_parser, enemy_manager

# game_loop.py
import pygame
import sys
import time
import os
from config.config import GameConfig
from core.save_load import save_game
from config.autosave import AutosaveSettings
from core.utils import get_timestamp, ensure_dir_exists, format_time_delta

class GameLoop:
    def __init__(self, game_state, command_parser, enemy_manager, world):
        """Initialize the game loop with all necessary components"""
        self.game_state = game_state
        self.command_parser = command_parser
        self.enemy_manager = enemy_manager
        self.world = world
        
        # Initialize pygame components
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        pygame.display.set_caption("MiniMUD - Text RPG Adventure")
        self.clock = pygame.time.Clock()
        
        # Load fonts
        self.font = pygame.font.SysFont("Courier New", GameConfig.FONT_SIZE)
        self.title_font = pygame.font.SysFont("Courier New", GameConfig.FONT_SIZE + 10, bold=True)
        
        # User input tracking
        self.user_input = ""
        self.input_active = True
        self.scroll_offset = 0  # Track scrolling position
    
    def process_command(self, command):
        """Process a player command"""
        return self.command_parser.parse(command)
    
    def update_enemies(self):
        """Update all enemies in the game"""
        self.enemy_manager.update(self.game_state)
    
    def draw_separator_line(self, y_position):
        """Draw a subtle separator line above the input area"""
        line_color = (60, 60, 60)  # Darker gray, subtle line
        pygame.draw.line(
            self.screen, 
            line_color, 
            (GameConfig.MARGIN, y_position), 
            (GameConfig.SCREEN_WIDTH - GameConfig.MARGIN, y_position), 
            1  # Line thickness
        )
    
    def handle_autosave(self):
        """Handle automatic saving of the game"""
        current_time = time.time()
        
        # Check if it's time to autosave
        if AutosaveSettings.should_autosave(current_time):
            # Only auto-save if player is not in combat (to avoid saving in a bad state)
            enemies_in_room = self.enemy_manager.get_enemies_in_room(self.game_state.current_room)
            safe_to_save = len([e for e in enemies_in_room if e.is_alive()]) == 0
            
            if safe_to_save and not self.game_state.game_over:
                # Make sure autosave directory exists
                ensure_dir_exists(AutosaveSettings.autosave_dir)
                
                # Get the autosave filename
                autosave_path = AutosaveSettings.get_autosave_filename()
                
                # Do the save
                save_game(self.game_state, autosave_path)
                
                # Check for backup
                if AutosaveSettings.should_backup(current_time):
                    backup_path = AutosaveSettings.get_backup_filename()
                    save_game(self.game_state, backup_path)
                    
                    # Log backup save (subtle)
                    backup_text = f"Backup save created: {os.path.basename(backup_path)}"
                    backup_surface = self.font.render(backup_text, True, (100, 100, 100))
                    self.screen.blit(backup_surface, (GameConfig.MARGIN, 
                                    GameConfig.SCREEN_HEIGHT - GameConfig.MARGIN*3 - GameConfig.FONT_SIZE*3))
                
                # Mark the save time
                AutosaveSettings.mark_saved(current_time)
    
    def run(self):
        """Run the main game loop"""
        # Look at the initial room to start the game
        self.game_state.look()
        
        while True:
            current_time = time.time()
            self.screen.fill(GameConfig.BG_COLOR)
            
            # Update enemies periodically
            self.update_enemies()

            # Update regions
            self.world.update_regions(self.game_state)
            
            # Check for ambient environmental messages
            current_region = self.world.get_region_for_room(self.game_state.current_room)
            if current_region:
                ambient_msg = current_region.environment_system.get_random_ambient_message(self.game_state)
                if ambient_msg:
                    self.game_state.add_to_history(ambient_msg, (100, 200, 255))

            # Handle autosave
            self.handle_autosave()

            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                # Handle mouse wheel scrolling
                elif event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:  # Scroll up
                        self.scroll_offset = min(self.scroll_offset + GameConfig.SCROLL_AMOUNT, 
                                             len(self.game_state.game_history) - GameConfig.MAX_LINES_DISPLAYED)
                    elif event.y < 0:  # Scroll down
                        self.scroll_offset = max(0, self.scroll_offset - GameConfig.SCROLL_AMOUNT)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.input_active:
                        # Process the command
                        self.game_state.add_to_history(GameConfig.INPUT_MARKER + self.user_input, GameConfig.INPUT_COLOR)
                        result = self.process_command(self.user_input)
                        if result:
                            self.game_state.add_to_history(result)
                                            
                        self.game_state.add_to_history("")  # Add a blank line for readability
                        self.user_input = ""
                        # Reset scroll to see the latest text
                        self.scroll_offset = 0
                    
                    elif event.key == pygame.K_BACKSPACE and self.input_active:
                        self.user_input = self.user_input[:-1]
                    
                    # Page Up/Down for scrolling
                    elif event.key == pygame.K_PAGEUP:
                        self.scroll_offset = min(self.scroll_offset + GameConfig.MAX_LINES_DISPLAYED//2, 
                                            len(self.game_state.game_history) - GameConfig.MAX_LINES_DISPLAYED)
                    elif event.key == pygame.K_PAGEDOWN:
                        self.scroll_offset = max(0, self.scroll_offset - GameConfig.MAX_LINES_DISPLAYED//2)
                    
                    elif self.input_active and not self.game_state.game_over:
                        # Only add printable characters
                        if event.unicode.isprintable():
                            self.user_input += event.unicode
            
            # Display game history with scrolling
            self.render_game_history()
            
            # Display input area
            self.render_input_area()
            
            pygame.display.flip()
            self.clock.tick(30)
            
            if self.game_state.game_over:
                pygame.time.wait(3000)  # Wait 3 seconds before quitting
                pygame.quit()
                sys.exit()
    
    def render_game_history(self):
        """Render the game history text with scrolling"""
        y_offset = GameConfig.MARGIN
        
        # Calculate the range of lines to display with scrolling
        history_len = len(self.game_state.game_history)
        display_start = max(0, history_len - GameConfig.MAX_LINES_DISPLAYED - self.scroll_offset)
        display_end = min(history_len, display_start + GameConfig.MAX_LINES_DISPLAYED)
        
        # Draw scrollbar indicator (simple version)
        if history_len > GameConfig.MAX_LINES_DISPLAYED:
            # Draw scrollbar background
            scrollbar_height = GameConfig.SCREEN_HEIGHT - 2*GameConfig.MARGIN - GameConfig.FONT_SIZE
            pygame.draw.rect(self.screen, (50, 50, 50), 
                           (GameConfig.SCREEN_WIDTH - 15, GameConfig.MARGIN, 10, scrollbar_height))
            
            # Draw scrollbar handle
            visible_ratio = GameConfig.MAX_LINES_DISPLAYED / history_len
            handle_height = max(20, scrollbar_height * visible_ratio)
            handle_pos = GameConfig.MARGIN + (scrollbar_height - handle_height) * (1 - (self.scroll_offset / max(1, history_len - GameConfig.MAX_LINES_DISPLAYED)))
            pygame.draw.rect(self.screen, (150, 150, 150), 
                           (GameConfig.SCREEN_WIDTH - 15, handle_pos, 10, handle_height))
        
        for i in range(display_start, display_end):
            line, color = self.game_state.game_history[i]
            text_surface = self.font.render(line, True, color)
            self.screen.blit(text_surface, (GameConfig.MARGIN, y_offset))
            y_offset += GameConfig.FONT_SIZE + GameConfig.LINE_SPACING
    
    def render_input_area(self):
        """Render the input area and status information"""
        input_area_y = GameConfig.SCREEN_HEIGHT - GameConfig.MARGIN - GameConfig.FONT_SIZE - 20
        self.draw_separator_line(input_area_y - 10)
        
        # Display current input
        if not self.game_state.game_over:
            input_text = GameConfig.INPUT_MARKER + self.user_input
            input_surface = self.font.render(input_text, True, GameConfig.INPUT_COLOR)
            self.screen.blit(input_surface, (GameConfig.MARGIN, GameConfig.SCREEN_HEIGHT - GameConfig.MARGIN - GameConfig.FONT_SIZE))
            
            # Display health bar and level
            health_text = f"HP: {self.game_state.player.health}/{self.game_state.player.max_health} | LVL: {self.game_state.player.level}"
            health_surface = self.font.render(health_text, True, GameConfig.HEALTH_COLOR)
            self.screen.blit(health_surface, (GameConfig.SCREEN_WIDTH - GameConfig.MARGIN - health_surface.get_width(), 
                             GameConfig.SCREEN_HEIGHT - GameConfig.MARGIN - GameConfig.FONT_SIZE))
            
            # Display scroll indicator if scrolled up
            if self.scroll_offset > 0:
                scroll_text = f"[SCROLLED UP: PgUp/PgDn or Mouse Wheel to navigate]"
                scroll_surface = self.font.render(scroll_text, True, (150, 150, 150))
                self.screen.blit(scroll_surface, (GameConfig.MARGIN, GameConfig.SCREEN_HEIGHT - GameConfig.MARGIN - GameConfig.FONT_SIZE*2 - 5))

# game_state.py
import textwrap
import random
import time
from systems.shop import ShopSystem
from items.item_factory import ItemFactory
from systems.crafting import CraftingSystem
from core.utils import get_weather_description, get_environment_effect_description, dice_roll, calculate_chance, clamp
from systems.journal import Journal

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
        
        # Display room and region information
        self.add_to_history(f"Location: {self.current_room.replace('_', ' ').title()}", TITLE_COLOR)
        
        if region and region.discovered:
            self.add_to_history(f"Region: {region.display_name}", (180, 180, 255))
        
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
        
        # Store original health percentage (for drop calculation)
        original_health_pct = enemy.health / enemy.max_health if enemy.max_health > 0 else 0
        
        # Player attacks enemy with environmental modifiers
        attack_modifier = env_effects.get("player_attack", 0)
        
        # Use dice_roll for attack damage (more interesting variance)
        base_damage = dice_roll(2, 6, self.player.attack_power())  # 2d6 + attack power
        actual_damage = clamp(base_damage + attack_modifier, 1, 999)  # Ensure at least 1 damage
        
        enemy.take_damage(actual_damage)
        total_damage_dealt += actual_damage
        
        self.add_to_history(f"You attack the {enemy.name} for {actual_damage} damage!", self.COMBAT_COLOR)
        
        if enemy.health <= 0:
            # Enemy defeated code
            exp_gained = enemy.experience
            self.add_to_history(f"You have defeated the {enemy.name}!", self.COMBAT_COLOR)
            
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

            # Handle enemy drops
            self._process_enemy_drops(enemy.name, original_health_pct)

            # Update quest progress for killing enemies
            self.quest_manager.update_quest_progress("kill", enemy.name, self.current_room)
            
            # Update journal stats for enemy defeat
            self.journal.update_stats("enemies_killed", 1, enemy.name)
            
            # Add journal entry for significant enemies
            if enemy.name in ["goblin", "troll", "orc", "ghost"]:
                location = self.current_room.replace("_", " ").title()
                self.journal.add_entry(f"Defeated a {enemy.name} in {location}.", "combat")
            
            # Track combat in journal with victory
            self.journal.track_combat(enemy.name, total_damage_dealt, total_damage_taken, True)
            
            return None
    
        # Enemy counterattacks with environmental accuracy modifiers
        enemy_accuracy_mod = env_effects.get("enemy_accuracy", 0)
        
        # Use calculate_chance for hit probability
        base_hit_chance = 0.8  # 80% base chance to hit
        hit_chance = calculate_chance(base_hit_chance, [enemy_accuracy_mod / 10])
        
        # If accuracy check fails, enemy misses
        if not dice_roll(1, 100, 0) <= hit_chance * 100:
            weather = current_region.environment_system.get_weather(self.current_room) if current_region else "current"
            self.add_to_history(f"The {enemy.name} attacks but misses you in the {weather} conditions!", self.ENEMY_COLOR)
        else:
            # Enemy hits with modified damage
            counter_damage = dice_roll(1, 8, enemy.attack - 4)  # 1d8 + (attack - 4)
            counter_damage = clamp(counter_damage, 1, 999)  # Ensure at least 1 damage
            actual_damage = self.player.take_damage(counter_damage)
            total_damage_taken += actual_damage
            
            self.add_to_history(f"The {enemy.name} counterattacks for {actual_damage} damage!", self.ENEMY_COLOR)
            self.add_to_history(f"Your health: {self.player.health}/{self.player.max_health}", self.HEALTH_COLOR)
            
            # Add journal entry for significant damage
            if actual_damage > self.player.max_health // 4:  # More than 25% of max health
                self.journal.add_entry(f"Took {actual_damage} damage from a {enemy.name}! Health critical!", "combat")
            
            # Check for near-death situation
            if self.player.health < self.player.max_health // 5:  # Less than 20% health
                self.journal.add_entry(f"Barely survived combat with a {enemy.name}. Health dangerously low!", "combat")
                
                # Increment near-death counter in combat stats
                if "combat_stats" in self.journal.stats:
                    self.journal.stats["combat_stats"]["near_death_escapes"] += 1
        
        if self.player.health <= 0:
            self.add_to_history("You have been defeated! Game over.", self.COMBAT_COLOR)
            self.game_over = True
            
            # Add journal entry for player defeat
            self.journal.add_entry(f"Defeated by a {enemy.name} in {self.current_room.replace('_', ' ')}.", "death")
            
            # Track combat in journal with defeat
            self.journal.track_combat(enemy.name, total_damage_dealt, total_damage_taken, False)
        else:
            # Track ongoing combat (not a victory or defeat yet)
            self.journal.track_combat(enemy.name, total_damage_dealt, total_damage_taken, None)
            
        return f"The {enemy.name} has {enemy.health}/{enemy.max_health} health remaining."

    def _process_enemy_drops(self, enemy_name, health_percentage):
        """Process drops from a defeated enemy"""
        # Import the enemy_drops module
        from systems.enemy_drops import get_enemy_drops
        
        # Get drops based on enemy type, strength, and player level
        drops = get_enemy_drops(enemy_name, health_percentage, self.player.level)
        
        if not drops:
            return  # No drops
        
        # Process the drops
        drop_messages = []
        
        # First add coins directly
        if "coin" in drops:
            coin_amount = drops["coin"]
            self.coins += coin_amount
            drop_messages.append(f"{coin_amount} coins")
            
        # Add other items to the room
        current_room = self.world.get_room(self.current_room)
        
        if "items" not in current_room:
            current_room["items"] = []
        
        # Process non-coin items
        from items.item_factory import ItemFactory
        
        for item_name, quantity in drops.items():
            if item_name == "coin":
                continue  # Already handled coins
                
            # Add item to the room
            for _ in range(quantity):
                current_room["items"].append(item_name)
                
            # Get item display name for the message
            item_obj = ItemFactory.get_item(item_name)
            if item_obj:
                if quantity > 1:
                    drop_messages.append(f"{quantity}x {item_obj.display_name()}")
                else:
                    drop_messages.append(item_obj.display_name())
            else:
                if quantity > 1:
                    drop_messages.append(f"{quantity}x {item_name.replace('_', ' ')}")
                else:
                    drop_messages.append(item_name.replace('_', ' '))
        
        # Create message about the drops
        if drop_messages:
            drop_list = ", ".join(drop_messages)
            self.add_to_history(f"The {enemy_name} dropped: {drop_list}!", (100, 220, 100))  # Light green color

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
        
        if self.player.weapon:
            weapon = ItemFactory.get_item(self.player.weapon)
            if weapon:
                self.add_to_history(f"Weapon: {weapon.display_name()} (+{weapon.attack_bonus} attack)")
            else:
                self.add_to_history(f"Weapon: {self.player.weapon.replace('_', ' ')}")
        else:
            self.add_to_history("Weapon: None")
            
        if self.player.armor:
            armor = ItemFactory.get_item(self.player.armor)
            if armor:
                self.add_to_history(f"Armor: {armor.display_name()} (+{armor.defense_bonus} defense)")
            else:
                self.add_to_history(f"Armor: {self.player.armor.replace('_', ' ')}")
        else:
            self.add_to_history("Armor: None")
    
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

# save_load.py
import json
import os
import time
from datetime import datetime
from core.utils import get_timestamp, ensure_dir_exists

def save_game(game_state, filename="savegame.json"):
    """
    Save the current game state to a file
    
    Args:
        game_state (GameState): The current game state
        filename (str): The filename to save to (default: savegame.json)
        
    Returns:
        str: Success message or error message
    """
    try:
        # Create save directory if it doesn't exist
        save_dir = ensure_dir_exists("saves")
        
        # Add directory to filename if not already there
        if not os.path.dirname(filename):
            filename = os.path.join(save_dir, filename)
            
        # Add .json extension if not present
        if not filename.endswith(".json"):
            filename += ".json"
        
        # Prepare save data
        save_data = {
            # Save metadata
            "metadata": {
                "save_time": time.time(),
                "save_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "game_version": "1.0.0",  # Add versioning for future compatibility
                "timestamp": get_timestamp()
            },
            
            # Player data
            "player": {
                "health": game_state.player.health,
                "max_health": game_state.player.max_health,
                "attack": game_state.player.attack,
                "defense": game_state.player.defense,
                "level": game_state.player.level,
                "experience": game_state.player.experience,
                "exp_to_next_level": game_state.player.exp_to_next_level,
                "weapon": game_state.player.weapon,
                "armor": game_state.player.armor,
                "inventory": game_state.player.inventory,
                "temp_attack_bonus": game_state.player.temp_attack_bonus,
                "temp_defense_bonus": game_state.player.temp_defense_bonus,
                "temp_buff_end_time": game_state.player.temp_buff_end_time
            },
            
            # Game state
            "current_room": game_state.current_room,
            "coins": game_state.coins,
            
            # World state (room modifications)
            "world": {
                "room_changes": {}
            },
            
            # Region data
            "regions": {},
            
            # Enemy data
            "enemies": []
        }
        
        # Save room modifications (items added/removed, locks changed)
        for region_name, region in game_state.world.regions.items():
            region_data = {
                "discovered": region.discovered,
                "danger_level": region.danger_level,
                "rooms": {}
            }
            
            for room_name, room in region.rooms.items():
                # Only save rooms that have changed from initial state
                # Here we're assuming items might have changed
                if "items" in room:
                    region_data["rooms"][room_name] = {
                        "items": room["items"]
                    }
                
                # Save unlocked state for locked rooms
                if "locked" in room:
                    if room_name not in region_data["rooms"]:
                        region_data["rooms"][room_name] = {}
                    region_data["rooms"][room_name]["locked"] = room["locked"]
            
            # Only add region if it has changes
            if region.discovered or region_data["rooms"]:
                save_data["regions"][region_name] = region_data
        
        # Save enemy data
        if game_state.enemy_manager:
            for enemy in game_state.enemy_manager.enemies:
                enemy_data = {
                    "name": enemy.name,
                    "health": enemy.health,
                    "max_health": enemy.max_health,
                    "attack": enemy.attack,
                    "experience": enemy.experience,
                    "current_room": enemy.current_room,
                    "last_move_time": enemy.last_move_time,
                    "death_time": enemy.death_time,
                    "respawn_delay": enemy.respawn_delay
                }
                save_data["enemies"].append(enemy_data)
        
        # Save game history (last 20 messages)
        save_data["history"] = game_state.game_history[-20:] if len(game_state.game_history) > 20 else game_state.game_history
        save_data["journal"] = game_state.journal.save_to_dict()

        # Write the save file
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        return f"Game saved to {filename}."
        
    except Exception as e:
        return f"Error saving game: {str(e)}"


def load_game(game_state, filename="savegame.json"):
    """
    Load game from a save file
    
    Args:
        game_state (GameState): The current game state to modify
        filename (str): The filename to load from (default: savegame.json)
        
    Returns:
        tuple: (bool, str) Success flag and message
    """
    try:
        # Add directory to filename if not already there
        save_dir = "saves"
        if not os.path.dirname(filename):
            filename = os.path.join(save_dir, filename)
            
        # Add .json extension if not present
        if not filename.endswith(".json"):
            filename += ".json"
        
        # Check if the file exists
        if not os.path.exists(filename):
            return False, f"Save file not found: {filename}"
        
        # Load the save file
        with open(filename, 'r') as f:
            save_data = json.load(f)
        
        # Check version compatibility (simple check for now)
        if "metadata" in save_data and "game_version" in save_data["metadata"]:
            save_version = save_data["metadata"]["game_version"]
            if save_version != "1.0.0":  # Current version
                game_state.add_to_history(f"Warning: Save file version ({save_version}) may not be fully compatible with the current game version.")
        
        # Load player data
        player_data = save_data["player"]
        game_state.player.health = player_data["health"]
        game_state.player.max_health = player_data["max_health"]
        game_state.player.attack = player_data["attack"]
        game_state.player.defense = player_data["defense"]
        game_state.player.level = player_data["level"]
        game_state.player.experience = player_data["experience"]
        game_state.player.exp_to_next_level = player_data["exp_to_next_level"]
        game_state.player.weapon = player_data["weapon"]
        game_state.player.armor = player_data["armor"]
        game_state.player.inventory = player_data["inventory"]
        
        # Load temp buffs if they exist in the save
        if "temp_attack_bonus" in player_data:
            game_state.player.temp_attack_bonus = player_data["temp_attack_bonus"]
        if "temp_defense_bonus" in player_data:
            game_state.player.temp_defense_bonus = player_data["temp_defense_bonus"]
        if "temp_buff_end_time" in player_data:
            game_state.player.temp_buff_end_time = player_data["temp_buff_end_time"]
        
        # Load game state
        game_state.current_room = save_data["current_room"]
        game_state.coins = save_data["coins"]
        
        # Load region data
        if "regions" in save_data:
            for region_name, region_data in save_data["regions"].items():
                region = game_state.world.get_region(region_name)
                if region:
                    # Load region state
                    region.discovered = region_data.get("discovered", False)
                    region.danger_level = region_data.get("danger_level", region.difficulty)
                    
                    # Load room changes
                    if "rooms" in region_data:
                        for room_name, room_changes in region_data["rooms"].items():
                            room = region.get_room(room_name)
                            if room:
                                # Update items
                                if "items" in room_changes:
                                    room["items"] = room_changes["items"]
                                
                                # Update locked state
                                if "locked" in room_changes:
                                    room["locked"] = room_changes["locked"]
        
        # Load enemy data
        if "enemies" in save_data and game_state.enemy_manager:
            # Clear existing enemies
            game_state.enemy_manager.enemies = []
            
            # Load saved enemies
            from entities.enemy import Enemy
            for enemy_data in save_data["enemies"]:
                enemy = Enemy(
                    name=enemy_data["name"],
                    health=enemy_data["max_health"],  # Initialize with max health
                    attack=enemy_data["attack"],
                    experience=enemy_data["experience"],
                    allowed_rooms=[enemy_data["current_room"]],  # Minimal allowed rooms
                    respawn_delay=enemy_data.get("respawn_delay", 60)  # Default if missing
                )
                
                # Update specific enemy state
                enemy.health = enemy_data["health"]
                enemy.current_room = enemy_data["current_room"]
                enemy.last_move_time = enemy_data.get("last_move_time", time.time())
                enemy.death_time = enemy_data.get("death_time", None)
                
                # Add to enemy manager
                game_state.enemy_manager.enemies.append(enemy)
        
        # Load game history if available
        if "history" in save_data:
            # Clear current history and add a few separator lines
            game_state.game_history = []
            game_state.add_to_history("=" * 40)
            game_state.add_to_history("LOADING SAVED GAME")
            game_state.add_to_history("=" * 40)
            
            # Add saved history items
            for line, color in save_data["history"]:
                game_state.add_to_history(line, tuple(color) if isinstance(color, list) else color)
            
            game_state.add_to_history("=" * 40)
        
        if "journal" in save_data:
            game_state.journal.load_from_dict(save_data["journal"])

        # Add success message to history
        game_state.add_to_history("Game loaded successfully!")
        
        # Show save metadata if available
        if "metadata" in save_data and "save_date" in save_data["metadata"]:
            save_date = save_data["metadata"]["save_date"]
            game_state.add_to_history(f"Save created on: {save_date}")
        
        # Look at the current room to refresh the display
        game_state.look()
        
        return True, "Game loaded successfully."
        
    except Exception as e:
        return False, f"Error loading game: {str(e)}"


def list_saves():
    """
    List all available save files
    
    Returns:
        list: List of save files with metadata
    """
    save_dir = "saves"
    if not os.path.exists(save_dir):
        return []
    
    save_files = []
    for filename in os.listdir(save_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(save_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    save_data = json.load(f)
                
                # Extract metadata
                metadata = save_data.get("metadata", {})
                save_date = metadata.get("save_date", "Unknown date")
                
                # Player info
                player_data = save_data.get("player", {})
                player_level = player_data.get("level", 1)
                current_room = save_data.get("current_room", "Unknown")
                
                save_files.append({
                    "filename": filename,
                    "date": save_date,
                    "level": player_level,
                    "location": current_room.replace("_", " ").title(),
                    "size": os.path.getsize(filepath)
                })
            except:
                # If we can't read the file, just add basic info
                save_files.append({
                    "filename": filename,
                    "date": "Error reading save",
                    "level": 0,
                    "location": "Unknown",
                    "size": os.path.getsize(filepath)
                })
    
    # Sort by date (newest first)
    save_files.sort(key=lambda x: x["date"], reverse=True)
    return save_files


def delete_save(filename):
    """
    Delete a save file
    
    Args:
        filename (str): The filename to delete
        
    Returns:
        tuple: (bool, str) Success flag and message
    """
    save_dir = "saves"
    if not os.path.dirname(filename):
        filename = os.path.join(save_dir, filename)
        
    if not filename.endswith(".json"):
        filename += ".json"
    
    try:
        if os.path.exists(filename):
            os.remove(filename)
            return True, f"Save file '{os.path.basename(filename)}' deleted."
        else:
            return False, f"Save file '{os.path.basename(filename)}' not found."
    except Exception as e:
        return False, f"Error deleting save file: {str(e)}"

# utils.py
import os
import time
import random
from datetime import datetime

def get_timestamp():
    """Get a formatted timestamp for filenames"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def ensure_dir_exists(directory):
    """Ensure a directory exists, creating it if necessary"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def format_time_delta(seconds):
    """Format a time delta in a human-readable way"""
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours} hours, {minutes} minutes"

def get_random_element(collection, weights=None):
    """Get a random element from a collection, optionally with weights"""
    if not collection:
        return None
    
    if weights:
        # Normalize weights if needed
        if len(weights) != len(collection):
            weights = None
    
    if weights:
        return random.choices(collection, weights=weights, k=1)[0]
    else:
        return random.choice(collection)

def clamp(value, min_value, max_value):
    """Clamp a value between a minimum and maximum"""
    return max(min_value, min(value, max_value))

def dice_roll(num_dice, sides, modifier=0):
    """Roll dice with the format NdS+M (N dice with S sides, plus modifier M)"""
    result = sum(random.randint(1, sides) for _ in range(num_dice)) + modifier
    return result

def calculate_chance(base_chance, modifiers=None):
    """Calculate a chance with modifiers"""
    final_chance = base_chance
    
    if modifiers:
        for modifier in modifiers:
            if isinstance(modifier, (int, float)):
                # Additive modifier
                final_chance += modifier
            elif isinstance(modifier, tuple) and len(modifier) == 2:
                # Multiplicative modifier (name, value)
                final_chance *= modifier[1]
    
    # Clamp between 0 and 1
    return clamp(final_chance, 0, 1)

def parse_duration(duration_str):
    """Parse a duration string into seconds"""
    if not duration_str:
        return 0
        
    duration_str = duration_str.lower()
    total_seconds = 0
    
    # Parse formats like "1h30m", "45s", "2d", etc.
    parts = []
    current_num = ""
    
    for char in duration_str:
        if char.isdigit():
            current_num += char
        elif char in "dhms":
            if current_num:
                parts.append((int(current_num), char))
                current_num = ""
    
    # Add any trailing number without a unit as seconds
    if current_num:
        parts.append((int(current_num), "s"))
    
    # Calculate total seconds
    for value, unit in parts:
        if unit == "d":
            total_seconds += value * 86400  # days
        elif unit == "h":
            total_seconds += value * 3600   # hours
        elif unit == "m":
            total_seconds += value * 60     # minutes
        elif unit == "s":
            total_seconds += value          # seconds
    
    return total_seconds

def get_weather_description(weather_type, intensity=1.0):
    """Generate a weather description based on type and intensity"""
    base_descriptions = {
        "clear": [
            "The air is still and clear.",
            "Visibility is excellent in these conditions.",
            "The atmosphere is calm and serene."
        ],
        "misty": [
            "A light mist hangs in the air.",
            "Wisps of fog curl around your ankles.",
            "The mist limits visibility somewhat."
        ],
        "humid": [
            "The air is damp and humid.",
            "Moisture clings to every surface.",
            "The humid air feels heavy to breathe."
        ],
        "stormy": [
            "Distant rumblings can be heard.",
            "The air crackles with energy.",
            "Occasional tremors shake the ground."
        ],
        "magical": [
            "The air shimmers with strange energy.",
            "Tiny motes of light dance in the air.",
            "You feel a tingling sensation on your skin."
        ]
    }
    
    # Get base description
    if weather_type not in base_descriptions:
        weather_type = "clear"
        
    descriptions = base_descriptions[weather_type]
    base_desc = get_random_element(descriptions)
    
    # Add intensity modifiers
    if intensity < 0.5:
        intensity_desc = "very mild"
    elif intensity < 0.8:
        intensity_desc = "mild"
    elif intensity < 1.2:
        intensity_desc = "moderate"
    elif intensity < 1.5:
        intensity_desc = "strong"
    else:
        intensity_desc = "extreme"
    
    # For very mild effects, don't mention intensity
    if intensity >= 0.8:
        return f"{base_desc} The {intensity_desc} {weather_type} conditions affect the environment."
    else:
        return base_desc

def get_environment_effect_description(effect_name, value):
    """Generate a description of an environmental effect"""
    effect_descriptions = {
        "enemy_accuracy": {
            "positive": "The clear conditions give enemies better accuracy.",
            "negative": "The poor visibility makes it harder for enemies to hit you."
        },
        "player_attack": {
            "positive": "The conditions enhance your attacks.",
            "negative": "The conditions make it harder to move and attack effectively."
        },
        "enemy_spawn_rate": {
            "positive": "The environment seems peaceful; creatures are less likely to appear.",
            "negative": "The disturbances seem to be attracting more creatures to this area."
        },
        "healing_bonus": {
            "positive": "There's a restorative quality to the air here.",
            "negative": "The oppressive atmosphere makes recovery more difficult."
        }
    }
    
    if effect_name not in effect_descriptions:
        return ""
    
    if effect_name == "enemy_accuracy" or effect_name == "player_attack":
        return effect_descriptions[effect_name]["negative"] if value < 0 else effect_descriptions[effect_name]["positive"]
    elif effect_name == "enemy_spawn_rate":
        return effect_descriptions[effect_name]["negative"] if value > 1 else effect_descriptions[effect_name]["positive"]
    elif effect_name == "healing_bonus":
        return effect_descriptions[effect_name]["positive"] if value > 1 else effect_descriptions[effect_name]["negative"]
    
    return ""

# enemy.py
import random
import time

class Enemy:
    def __init__(self, name, health, attack, experience, allowed_rooms, respawn_delay=60):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.experience = experience
        self.allowed_rooms = allowed_rooms
        self.current_room = random.choice(allowed_rooms)
        self.last_move_time = time.time()
        self.death_time = None
        self.respawn_delay = respawn_delay  # seconds until respawn after death
    
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health == 0 and self.death_time is None:
            self.death_time = time.time()
        return amount
    
    def is_alive(self):
        return self.health > 0
    
    def move(self):
        """Move enemy to a random room within its allowed rooms"""
        if len(self.allowed_rooms) > 1 and self.is_alive():
            # Choose a different room than the current one
            new_room = random.choice([room for room in self.allowed_rooms if room != self.current_room])
            self.current_room = new_room
            return True
        return False
    
    def check_respawn(self):
        """Check if it's time to respawn this enemy"""
        if not self.is_alive() and self.death_time is not None:
            current_time = time.time()
            if current_time - self.death_time >= self.respawn_delay:
                self.respawn()
                return True
        return False
    
    def respawn(self):
        """Respawn the enemy"""
        self.health = self.max_health
        self.current_room = random.choice(self.allowed_rooms)
        self.death_time = None
        return True

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

# player.py
import time
from items.item_factory import ItemFactory

class Player:
    def __init__(self):
        self.name = "Adventurer"
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.defense = 5
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 20
        
        # Equipment slots
        self.weapon = None  # Equipped weapon name
        self.armor = None   # Equipped armor name
        
        # Temporary stat buffs
        self.temp_attack_bonus = 0
        self.temp_defense_bonus = 0
        self.temp_buff_end_time = 0
        
        # Inventory storage (use a dict for stacking)
        self.inventory = {}  # Format: {item_name: quantity}
    
    def take_damage(self, amount):
        """Take damage with defense reduction"""
        actual_damage = max(1, amount - self.defense_power())
        self.health = max(0, self.health - actual_damage)
        return actual_damage
    
    def heal(self, amount):
        """Heal the player"""
        self.health = min(self.max_health, self.health + amount)
        return amount
    
    def attack_power(self):
        """Calculate total attack power including equipment and buffs"""
        # Check temporary buffs
        self._update_temp_buffs()
        
        # Base attack + weapon bonus + temp buffs
        weapon_bonus = 0
        if self.weapon:
            weapon = ItemFactory.get_item(self.weapon)
            if weapon:
                weapon_bonus = weapon.get_attack_bonus()
                
        return self.attack + weapon_bonus + self.temp_attack_bonus
    
    def defense_power(self):
        """Calculate total defense including equipment and buffs"""
        # Check temporary buffs
        self._update_temp_buffs()
        
        # Base defense + armor bonus + temp buffs
        armor_bonus = 0
        if self.armor:
            armor = ItemFactory.get_item(self.armor)
            if armor:
                armor_bonus = armor.get_defense_bonus()
                
        return self.defense + armor_bonus + self.temp_defense_bonus
    
    def _update_temp_buffs(self):
        """Update temporary buffs (check if they've expired)"""
        current_time = time.time()
        if current_time > self.temp_buff_end_time:
            self.temp_attack_bonus = 0
            self.temp_defense_bonus = 0
    
    def gain_experience(self, amount):
        """Add experience and level up if necessary"""
        self.experience += amount
        if self.experience >= self.exp_to_next_level:
            self.level_up()
            return True
        return False
    
    def level_up(self):
        """Increase player's level and stats"""
        self.level += 1
        self.attack += 2
        self.defense += 1
        self.max_health += 10
        self.health = self.max_health
        self.experience -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.5)
        return self.level
    
    def equip_weapon(self, weapon_name):
        """Equip a weapon"""
        weapon = ItemFactory.get_item(weapon_name)
        if weapon and weapon.type == "weapon":
            if weapon.meets_requirements(self):
                self.weapon = weapon_name
                return True
        return False
    
    def equip_armor(self, armor_name):
        """Equip armor"""
        armor = ItemFactory.get_item(armor_name)
        if armor and armor.type == "armor":
            if armor.meets_requirements(self):
                self.armor = armor_name
                return True
        return False
    
    def add_to_inventory(self, item_name, quantity=1):
        """Add an item to inventory"""
        item = ItemFactory.get_item(item_name)
        if not item:
            return False
            
        if item_name in self.inventory:
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity
        return True
    
    def remove_from_inventory(self, item_name, quantity=1):
        """Remove an item from inventory"""
        if item_name in self.inventory:
            if self.inventory[item_name] <= quantity:
                # Remove the item completely
                del self.inventory[item_name]
            else:
                # Reduce the quantity
                self.inventory[item_name] -= quantity
            return True
        return False
    
    def has_item(self, item_name, quantity=1):
        """Check if player has the specified item quantity"""
        return item_name in self.inventory and self.inventory[item_name] >= quantity
    
    def get_item_quantity(self, item_name):
        """Get quantity of a specific item"""
        return self.inventory.get(item_name, 0)
    
    def get_inventory_list(self):
        """Get a list of items in inventory with quantities"""
        inventory_list = []
        for item_name, quantity in self.inventory.items():
            item = ItemFactory.get_item(item_name)
            if item:
                if quantity > 1:
                    inventory_list.append(f"{item.display_name()} (x{quantity})")
                else:
                    inventory_list.append(item.display_name())
        return inventory_list
    
    def use_item(self, item_name, game_state):
        """Use an item from inventory"""
        if not self.has_item(item_name):
            return False, f"You don't have a {item_name.replace('_', ' ')}."
            
        item = ItemFactory.get_item(item_name)
        if not item:
            return False, f"Unknown item: {item_name.replace('_', ' ')}."
            
        if not item.can_use(game_state):
            return False, f"You can't use the {item.display_name()} here."
            
        # Use the item
        success, message = item.use(game_state)
        
        # If successfully used a consumable, remove it from inventory
        if success and (item.type == "consumable" or 
                       (item.type == "key" and hasattr(item, "single_use") and item.single_use)):
            self.remove_from_inventory(item_name)
            
        return success, message
    
    def find_item(self, search_string):
        """
        Find an item in the player's inventory by name or alias
        with partial string matching.
        
        Args:
            search_string (str): The name to search for
            
        Returns:
            str: The internal item name, or None if not found
        """
        search_string = search_string.lower()
        
        # First check for exact match
        for item_name in self.inventory:
            if item_name.replace('_', ' ') == search_string:
                return item_name
                
        # Check for partial match
        best_match = None
        best_score = float('inf')  # Lower is better
        
        for item_name in self.inventory:
            item = ItemFactory.get_item(item_name)
            if not item:
                continue
                
            # Check if search string is in name
            if search_string in item_name.replace('_', ' '):
                score = len(item_name) - len(search_string)
                if score < best_score:
                    best_match = item_name
                    best_score = score
            
            # Check if search string is in aliases
            for alias in item.aliases:
                if search_string in alias.lower():
                    score = len(alias) - len(search_string)
                    if score < best_score:
                        best_match = item_name
                        best_score = score
        
        return best_match

    def get_item(self, item_name):
        """
        Get an item instance from the player's inventory
        
        Args:
            item_name (str): The internal name of the item
            
        Returns:
            Item: The item instance, or None if not in inventory
        """
        if item_name in self.inventory:
            return ItemFactory.get_item(item_name)
        return None

# armor.py
from items.item import Item

class Armor(Item):
    def __init__(self, name, description, defense_bonus, value=15, 
                 durability=None, requirements=None, aliases=None):
        """
        Armor class for all armor items
        
        Args:
            name (str): Internal name of the armor
            description (str): Human-readable description
            defense_bonus (int): Defense bonus provided by the armor
            value (int): Base value in coins
            durability (int, optional): Durability points, None for indestructible
            requirements (dict, optional): Player requirements to use (e.g., {"level": 2})
            aliases (list): Alternative names for the armor
        """
        super().__init__(name, description, value, stackable=False, usable=False, aliases=aliases)
        self.defense_bonus = defense_bonus
        self.durability = durability
        self.max_durability = durability
        self.requirements = requirements or {}
        self.type = "armor"
    
    def get_defense_bonus(self):
        """Return the defense bonus provided by this armor"""
        return self.defense_bonus
    
    def meets_requirements(self, player):
        """Check if player meets the requirements to use this armor"""
        for req, value in self.requirements.items():
            if req == "level" and player.level < value:
                return False
        return True
    
    def __str__(self):
        return f"{self.display_name()} (+{self.defense_bonus} DEF)"

# Predefined armor
ARMORS = {
    "leather_armor": Armor(
        "leather_armor", 
        "Simple leather armor offering basic protection.",
        defense_bonus=3,
        value=15,
        aliases=["leather", "light armor"]
    ),
    "chainmail": Armor(
        "chainmail", 
        "A shirt of interlocking metal rings providing good protection.",
        defense_bonus=6,
        value=30,
        requirements={"level": 2},
        aliases=["chain", "chain armor", "mail"]
    ),
    "plate_armor": Armor(
        "plate_armor", 
        "Heavy plate armor offering superior protection.",
        defense_bonus=10,
        value=45,
        requirements={"level": 3},
        aliases=["plate", "heavy armor", "metal armor"]
    )
}

def get_armor(armor_name):
    """Get an armor from the predefined armors"""
    return ARMORS.get(armor_name)

# box_keys.py
from items.treasure import Key

# Define special keys for treasure boxes
BOX_KEYS = {
    "common_box_key": Key(
        "common_box_key",
        "A simple iron key that can open common treasure boxes.",
        unlocks=["common_treasure_box"],
        value=2,
        single_use=True,
        aliases=["iron key", "simple key", "common key"]
    ),
    "uncommon_box_key": Key(
        "uncommon_box_key",
        "A well-crafted bronze key with small engravings. Opens uncommon treasure boxes.",
        unlocks=["uncommon_treasure_box"],
        value=5,
        single_use=True,
        aliases=["bronze key", "engraved key", "uncommon key"]
    ),
    "rare_box_key": Key(
        "rare_box_key",
        "A silver key with an unusual shape. It feels slightly warm to the touch.",
        unlocks=["rare_treasure_box"],
        value=12,
        single_use=True,
        aliases=["silver key", "warm key", "rare key"]
    ),
    "epic_box_key": Key(
        "epic_box_key",
        "A golden key with glowing blue gems embedded in its handle.",
        unlocks=["epic_treasure_box"],
        value=25,
        single_use=True,
        aliases=["golden key", "gem key", "epic key"]
    ),
    "legendary_box_key": Key(
        "legendary_box_key",
        "A mysterious key that seems to shift and change as you look at it. Powerful magic emanates from it.",
        unlocks=["legendary_treasure_box"],
        value=50,
        single_use=True,
        aliases=["magical key", "shifting key", "legendary key"]
    ),
    "master_key": Key(
        "master_key",
        "A masterfully crafted skeleton key that can open any treasure box. Extremely rare.",
        unlocks=["common_treasure_box", "uncommon_treasure_box", "rare_treasure_box", "epic_treasure_box", "legendary_treasure_box"],
        value=100,
        single_use=False,  # This key is reusable!
        aliases=["skeleton key", "master skeleton key", "universal key"]
    )
}

def get_box_key(key_name):
    """Get a box key from the predefined keys"""
    return BOX_KEYS.get(key_name)

# consumable.py
from items.item import Item

class Consumable(Item):
    def __init__(self, name, description, value=5, 
                 health_restore=0, effects=None, type="consumable", 
                 stackable=True, max_stack=5, aliases=None):
        """
        Consumable class for food and drink items
        
        Args:
            name (str): Internal name of the item
            description (str): Human-readable description
            value (int): Base value in coins
            health_restore (int): Amount of health restored when consumed
            effects (dict): Additional effects (e.g., {"strength": 2, "duration": 60})
            type (str): Specific type ("food", "drink", or generic "consumable")
            stackable (bool): Whether multiple of this item can stack in inventory
            max_stack (int): Maximum number of items in a stack
            aliases (list): Alternative names for the item
        """
        super().__init__(
            name, description, value, 
            stackable=stackable, max_stack=max_stack, usable=True,
            aliases=aliases
        )
        self.health_restore = health_restore
        self.effects = effects or {}
        self.type = type  # Can be "food", "drink", or generic "consumable"
    
    def use(self, game_state):
        """Use/consume the item"""
        player = game_state.player
        message = []
        
        # Restore health if applicable
        if self.health_restore > 0:
            player.heal(self.health_restore)
            message.append(f"You consume the {self.display_name()} and recover {self.health_restore} health points.")
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


# Predefined consumables
CONSUMABLES = {
    "healing_potion": Consumable(
        "healing_potion", 
        "A red potion that restores health.",
        health_restore=20,
        value=5,
        type="drink",
        aliases=["potion", "red potion", "health potion", "heal potion"]
    ),
    "strong_healing_potion": Consumable(
        "strong_healing_potion", 
        "A vibrant red potion that restores significant health.",
        health_restore=50,
        value=15,
        type="drink",
        aliases=["strong potion", "big potion", "large potion"]
    ),
    "stamina_potion": Consumable(
        "stamina_potion", 
        "A green potion that temporarily increases attack power.",
        health_restore=0,
        value=10,
        type="drink",
        effects={"strength": 5, "duration": 60},
        aliases=["green potion", "strength potion"]
    ),
    "bread": Consumable(
        "bread", 
        "A small loaf of bread. Slightly restores health.",
        health_restore=5,
        value=2,
        type="food",
        aliases=["loaf", "food"]
    ),
    "cooked_meat": Consumable(
        "cooked_meat", 
        "A piece of cooked meat. Restores health.",
        health_restore=15,
        value=4,
        type="food",
        aliases=["meat", "steak", "food"]
    ),
    "apple": Consumable(
        "apple", 
        "A fresh apple. Slightly restores health.",
        health_restore=3,
        value=1,
        type="food",
        aliases=["fruit", "food"]
    )
}

def get_consumable(consumable_name):
    """Get a consumable from the predefined consumables"""
    return CONSUMABLES.get(consumable_name)

# herbs.py
from items.item import Item
from items.consumable import Consumable

HERBS = {
    "herb_bundle": Item(
        "herb_bundle", 
        "A bundle of medicinal herbs carefully tied together.",
        value=3,
        stackable=True,
        max_stack=10,
        usable=True,
        aliases=["herbs", "medicinal herbs", "bundle"]
    ),
    "glowing_mushroom": Item(
        "glowing_mushroom", 
        "A mushroom that emits a soft blue glow. Has alchemical properties.",
        value=5,
        stackable=True,
        max_stack=10,
        usable=True,
        aliases=["mushroom", "luminous mushroom", "blue mushroom"]
    ),
    "waterbloom": Item(
        "waterbloom", 
        "A delicate aquatic flower that thrives in dark waters. Used in advanced potions.",
        value=7,
        stackable=True,
        max_stack=5,
        usable=True,
        aliases=["water flower", "cave lily", "aquatic bloom"]
    ),
    "antidote": Consumable(
        "antidote", 
        "A blue potion that cures poison and disease.",
        health_restore=5,
        effects={"cure_status": True}, 
        value=7,
        type="drink",
        aliases=["blue potion", "cure", "medicine"]
    ),
    "elixir_of_clarity": Consumable(
        "elixir_of_clarity", 
        "A purple potion that enhances perception and reflexes.",
        health_restore=0,
        effects={"dodge_chance": 0.2, "duration": 120},
        value=15,
        type="drink",
        aliases=["clarity potion", "purple potion", "reflex potion"]
    )
}

def get_herb(herb_name):
    """Get an herb from the predefined herbs"""
    return HERBS.get(herb_name)

# item.py
class Item:
    def __init__(self, name, description, value=1, stackable=False, max_stack=1, usable=False, aliases=None):
        """
        Base class for all items in the game
        
        Args:
            name (str): Internal name of the item (snake_case)
            description (str): Human-readable description
            value (int): Base value in coins
            stackable (bool): Whether multiple of this item can stack in inventory
            max_stack (int): Maximum number of items in a stack
            usable (bool): Whether the item can be used
            aliases (list): Alternative names for the item
        """
        self.name = name
        self.description = description
        self.value = value
        self.stackable = stackable
        self.max_stack = max_stack if stackable else 1
        self.usable = usable
        self.aliases = aliases or []
        self.type = "item"  # Base type for generic items
        
        # Automatically add some basic aliases
        base_name = name.replace('_', ' ')
        parts = base_name.split()
        if len(parts) > 1 and parts[-1] not in self.aliases:
            # Add the last word as an alias (e.g., "healing potion" -> "potion")
            self.aliases.append(parts[-1])
        if len(parts) > 1 and parts[0] not in self.aliases:
            # Add the first word as an alias (e.g., "rusty sword" -> "rusty")
            self.aliases.append(parts[0])
    
    def display_name(self):
        """Return a friendly display name (spaces instead of underscores)"""
        return self.name.replace('_', ' ')
    
    def can_use(self, game_state):
        """Check if the item can be used in the current context"""
        return self.usable
    
    def use(self, game_state):
        """Use the item - to be overridden by subclasses"""
        if not self.usable:
            return False, f"You can't figure out how to use the {self.display_name()}."
        return True, f"You use the {self.display_name()}."
    
    def get_sell_price(self):
        """Get the price a shop will pay for this item"""
        return max(1, self.value // 2)
    
    def get_buy_price(self):
        """Get the price a shop will charge for this item"""
        return self.value
    
    def can_sell(self):
        """Check if the item can be sold to shops"""
        return True
    
    def __str__(self):
        return self.display_name()

# item_factory.py
from items.weapon import WEAPONS, get_weapon
from items.armor import ARMORS, get_armor
from items.herbs import HERBS, get_herb
from items.consumable import CONSUMABLES, get_consumable
from items.treasure import (
    GEMS, get_gem,
    QUEST_ITEMS, get_quest_item,
    KEYS, get_key,
    TOOLS, get_tool
)
from items.treasure_box import TREASURE_BOXES, get_treasure_box
from items.box_keys import BOX_KEYS, get_box_key

class ItemFactory:
    """
    Factory class to centralize item creation and management
    """
    
    @staticmethod
    def get_item(item_name):
        """
        Get an item instance by name
        
        Args:
            item_name (str): The internal name of the item
            
        Returns:
            Item: The item instance, or None if not found
        """
        if item_name in WEAPONS:
            return get_weapon(item_name)
        elif item_name in ARMORS:
            return get_armor(item_name)
        elif item_name in CONSUMABLES:
            return get_consumable(item_name)
        elif item_name in GEMS:
            return get_gem(item_name)
        elif item_name in QUEST_ITEMS:
            return get_quest_item(item_name)
        elif item_name in KEYS:
            return get_key(item_name)
        elif item_name in TOOLS:
            return get_tool(item_name)
        elif item_name in TREASURE_BOXES:
            return get_treasure_box(item_name)
        elif item_name in BOX_KEYS:
            return get_box_key(item_name)
        elif item_name in HERBS:  # Add this line
            return get_herb(item_name)  # And this line
        elif item_name == "coin":
            # Special case for coins
            from items.item import Item
            return Item("coin", "A gold coin.", value=1, stackable=True, max_stack=999)
        return None
    
    @staticmethod
    def get_all_items():
        """
        Get all available items as a dictionary
        
        Returns:
            dict: A dictionary of all items where keys are item names
        """
        all_items = {}
        
        # Add weapons
        from items.weapon import WEAPONS
        all_items.update(WEAPONS)
        
        # Add armors
        from items.armor import ARMORS
        all_items.update(ARMORS)
        
        # Add consumables
        from items.consumable import CONSUMABLES
        all_items.update(CONSUMABLES)
        
        # Add treasures
        from items.treasure import GEMS, QUEST_ITEMS, KEYS, TOOLS
        all_items.update(GEMS)
        all_items.update(QUEST_ITEMS)
        all_items.update(KEYS)
        all_items.update(TOOLS)
        
        from items.treasure_box import TREASURE_BOXES
        all_items.update(TREASURE_BOXES)
        
        from items.box_keys import BOX_KEYS
        all_items.update(BOX_KEYS)

        # Add coin as a special case
        from items.item import Item
        all_items["coin"] = Item("coin", "A gold coin.", value=1, stackable=True, max_stack=999)
        
        return all_items

    @staticmethod
    def find_item_by_name(search_string, include_partial=True):
        """
        Find an item by name or alias with partial string matching
        
        Args:
            search_string (str): The name to search for
            include_partial (bool): Whether to include partial matches
            
        Returns:
            str: The internal item name, or None if not found
        """
        search_string = search_string.lower().replace(' ', '_')
        
        # First check for direct match
        all_items = ItemFactory.get_all_items()
        if search_string in all_items:
            return search_string
            
        # Then check for exact alias match
        for item_name, item in all_items.items():
            item_obj = ItemFactory.get_item(item_name)
            if item_obj and search_string in [alias.lower().replace(' ', '_') for alias in item_obj.aliases]:
                return item_name
                
        # Finally, check for partial match if enabled
        if include_partial:
            # First check partial matches on item names
            matches = []
            for item_name in all_items.keys():
                if search_string in item_name:
                    matches.append((item_name, len(item_name) - len(search_string)))  # Score by how close the match is
            
            # Then check partial matches on aliases
            for item_name in all_items.keys():
                item_obj = ItemFactory.get_item(item_name)
                if not item_obj:
                    continue
                    
                for alias in item_obj.aliases:
                    alias = alias.lower().replace(' ', '_')
                    if search_string in alias:
                        matches.append((item_name, len(alias) - len(search_string)))
            
            # Return the best match (smallest length difference)
            if matches:
                matches.sort(key=lambda x: x[1])
                return matches[0][0]
                
        return None

# treasure.py
from items.item import Item

class Gem(Item):
    def __init__(self, name, description, value=10, rarity="common", aliases=None):
        """
        Gem class for valuable collectibles
        
        Args:
            name (str): Internal name of the gem
            description (str): Human-readable description
            value (int): Base value in coins
            rarity (str): Rarity level affecting value
            aliases (list): Alternative names for the item
        """
        super().__init__(name, description, value, stackable=True, max_stack=10, aliases=aliases)
        self.rarity = rarity
        self.type = "gem"
    
    def get_sell_price(self):
        """Get the sell price based on rarity"""
        rarity_multiplier = {
            "common": 1,
            "uncommon": 1.5,
            "rare": 2.5,
            "epic": 4,
            "legendary": 10
        }
        return max(1, int(self.value * rarity_multiplier.get(self.rarity, 1)))
    
    def __str__(self):
        return f"{self.display_name()} ({self.rarity.capitalize()} gem)"


class QuestItem(Item):
    def __init__(self, name, description, quest=None, value=0, aliases=None):
        """
        Quest item for storyline progress
        
        Args:
            name (str): Internal name of the item
            description (str): Human-readable description
            quest (str): Associated quest name
            value (int): Base value in coins (usually zero for quest items)
            aliases (list): Alternative names for the item
        """
        super().__init__(name, description, value, aliases=aliases)
        self.quest = quest
        self.type = "quest_item"
    
    def can_sell(self):
        """Quest items usually cannot be sold"""
        return False

class Key(Item):
    def __init__(self, name, description, unlocks=None, value=5, single_use=True, aliases=None):
        """
        Key item for unlocking doors or containers
        
        Args:
            name (str): Internal name of the key
            description (str): Human-readable description
            unlocks (list): List of room/container names this key unlocks
            value (int): Base value in coins
            single_use (bool): Whether the key is consumed upon use
            aliases (list): Alternative names for the item
        """
        super().__init__(name, description, value, usable=True, aliases=aliases)
        self.unlocks = unlocks or []
        self.single_use = single_use
        self.type = "key"
    
    def can_use(self, game_state):
        """
        Check if the key can be used in the current context
        - Checks for locked doors
        - Checks for treasure boxes in the room
        - Checks for treasure boxes in player's inventory
        """
        current_room = game_state.current_room
        
        # Check if current room has any locked exits this key unlocks
        room = game_state.world.get_room(current_room)
        if not room:
            return False
            
        # Check for doors this key can unlock
        for direction, destination in room.get("exits", {}).items():
            dest_room = game_state.world.get_room(destination)
            if dest_room and dest_room.get("locked", False) and destination in self.unlocks:
                return True
        
        # Check for treasure boxes in the room that this key can unlock
        if "items" in room:
            for item_name in room["items"]:
                # Check if this is a treasure box
                from items.item_factory import ItemFactory
                item = ItemFactory.get_item(item_name)
                if item and getattr(item, "type", "item") == "treasure_box" and (
                    item_name in self.unlocks or  # Specific unlock
                    getattr(item, "required_key", None) == self.name  # Required key match
                ):
                    return True
        
        # Also check player's inventory for treasure boxes
        for item_name in game_state.player.inventory:
            from items.item_factory import ItemFactory
            item = ItemFactory.get_item(item_name)
            if item and getattr(item, "type", "item") == "treasure_box" and (
                item_name in self.unlocks or  # Specific unlock
                getattr(item, "required_key", None) == self.name  # Required key match
            ):
                return True
                    
        return False

    def use(self, game_state):
        """
        Use the key to unlock something (door, treasure box in room, or treasure box in inventory)
        """
        current_room = game_state.current_room
        room = game_state.world.get_room(current_room)
        
        # First, try to unlock a door
        for direction, destination in room.get("exits", {}).items():
            dest_room = game_state.world.get_room(destination)
            if dest_room and dest_room.get("locked", False) and destination in self.unlocks:
                dest_room["locked"] = False
                message = f"You use the {self.display_name()} to unlock the way to the {destination.replace('_', ' ')}."
                
                # Handle key consumption for doors
                if self.single_use:
                    game_state.player.remove_from_inventory(self.name)
                    return True, message + " The key crumbles to dust after use."
                return True, message
        
        # If no door was unlocked, try to find a treasure box in the room
        box_found = False
        box = None
        box_name = None
        box_in_inventory = False
        
        # Import ItemFactory here to avoid circular imports
        from items.item_factory import ItemFactory
        
        # First check the room for boxes
        if "items" in room:
            for item_index, item_name in enumerate(room["items"]):
                item = ItemFactory.get_item(item_name)
                
                # Safe checking for treasure boxes
                if not item:
                    continue
                
                item_type = getattr(item, "type", "item")
                if item_type != "treasure_box":
                    continue
                    
                # Check if this key can unlock this box
                required_key = getattr(item, "required_key", None)
                if item_name in self.unlocks or required_key == self.name:
                    # Found a box to unlock in the room!
                    box_found = True
                    box_name = item_name
                    box = item
                    # Remove the box from the room
                    room["items"].pop(item_index)
                    break
        
        # If no box found in room, check player's inventory
        if not box_found:
            inventory_items = list(game_state.player.inventory.keys())
            for item_name in inventory_items:
                item = ItemFactory.get_item(item_name)
                
                # Safe checking for treasure boxes
                if not item:
                    continue
                    
                item_type = getattr(item, "type", "item")
                if item_type != "treasure_box":
                    continue
                    
                # Check if this key can unlock this box
                required_key = getattr(item, "required_key", None)
                if item_name in self.unlocks or required_key == self.name:
                    # Found a box to unlock in inventory!
                    box_found = True
                    box_name = item_name
                    box = item
                    box_in_inventory = True
                    # Remove the box from inventory
                    game_state.player.remove_from_inventory(item_name)
                    break
        
        # If we found a box to unlock (either in room or inventory)
        if box_found and box and box_name:
            # Generate the loot (if the box has a generate_loot method)
            loot = {}
            if hasattr(box, "generate_loot") and callable(box.generate_loot):
                loot = box.generate_loot(game_state)
            else:
                # Fallback - simple random loot
                import random
                loot = {"coin": random.randint(5, 15)}
            
            # Process the loot
            loot_messages = []
            for loot_item, quantity in loot.items():
                if loot_item == "coin":
                    game_state.coins += quantity
                    loot_messages.append(f"{quantity} coins")
                else:
                    # Add to player's inventory
                    for _ in range(quantity):
                        game_state.player.add_to_inventory(loot_item)
                    
                    # Create display message
                    loot_item_obj = ItemFactory.get_item(loot_item)
                    if loot_item_obj:
                        if quantity > 1:
                            loot_messages.append(f"{quantity}x {loot_item_obj.display_name()}")
                        else:
                            loot_messages.append(loot_item_obj.display_name())
                    else:
                        if quantity > 1:
                            loot_messages.append(f"{quantity}x {loot_item.replace('_', ' ')}")
                        else:
                            loot_messages.append(loot_item.replace('_', ' '))
            
            # Create result message
            if loot_messages:
                loot_list = ", ".join(loot_messages)
                if box_in_inventory:
                    message = f"You use the {self.display_name()} to unlock the {box.display_name()} from your inventory and find: {loot_list}."
                else:
                    message = f"You use the {self.display_name()} to unlock the {box.display_name()} and find: {loot_list}."
            else:
                if box_in_inventory:
                    message = f"You use the {self.display_name()} to unlock the {box.display_name()} from your inventory, but it's empty!"
                else:
                    message = f"You use the {self.display_name()} to unlock the {box.display_name()}, but it's empty!"
            
            # Important: Consume the key manually if it's single-use
            if self.single_use:
                # Explicitly remove the key from player's inventory
                game_state.player.remove_from_inventory(self.name)
                return True, message + " The key breaks after use."
            return True, message
        
        return False, f"There's nothing here that the {self.display_name()} can unlock."

class Tool(Item):
    def __init__(self, name, description, tool_type, value=5, aliases=None):
        """
        Tool item for special interactions
        
        Args:
            name (str): Internal name of the tool
            description (str): Human-readable description
            tool_type (str): Type of tool (e.g., "navigation", "digging")
            value (int): Base value in coins
            aliases (list): Alternative names for the item
        """
        super().__init__(name, description, value, usable=True, aliases=aliases)
        self.tool_type = tool_type
        self.type = "tool"
    
    def use(self, game_state):
        """Use the tool based on its type"""
        current_room = game_state.current_room
        
        if self.name == "torch" and current_room in ["entrance", "cavern", "narrow_passage"]:
            return True, "You light the torch, illuminating the dark cave around you."
            
        elif self.name == "boat" and current_room == "underground_lake":
            # Add special boat navigation logic
            return True, "You push the boat into the water and paddle to a small island in the center of the lake."
            
        elif self.name == "pickaxe" and current_room in ["narrow_passage", "hidden_grotto"]:
            # Mining mechanic
            return True, "You mine the wall, revealing small gems hidden in the rock."
            
        return False, f"You can't figure out how to use the {self.display_name()} here."

GEMS = {
    "gem": Gem(
        "gem", 
        "A small, sparkling gemstone.",
        value=10,
        rarity="common",
        aliases=["gemstone", "stone", "crystal"]
    ),
    "ruby": Gem(
        "ruby", 
        "A brilliant red gemstone that catches the light beautifully.",
        value=25,
        rarity="uncommon",
        aliases=["red gem", "red stone"]
    ),
    "sapphire": Gem(
        "sapphire", 
        "A deep blue gemstone of impressive clarity.",
        value=30,
        rarity="uncommon",
        aliases=["blue gem", "blue stone"]
    ),
    "emerald": Gem(
        "emerald", 
        "A vibrant green gemstone, rare and valuable.",
        value=40,
        rarity="rare",
        aliases=["green gem", "green stone"]
    ),
    "diamond": Gem(
        "diamond", 
        "A flawless diamond that sparkles with inner fire.",
        value=75,
        rarity="epic",
        aliases=["clear gem", "white gem"]
    )
}

QUEST_ITEMS = {
    "ancient_scroll": QuestItem(
        "ancient_scroll", 
        "A scroll with mysterious writing. It seems important.",
        aliases=["scroll", "parchment", "old scroll"]
    ),
    "golden_crown": QuestItem(
        "golden_crown", 
        "An ornate crown made of solid gold. It must be valuable.",
        aliases=["crown", "gold crown", "royal crown"]
    )
}

KEYS = {
    "ancient_key": Key(
        "ancient_key", 
        "An ornate key made of strange metal. It feels warm to the touch.",
        unlocks=["treasure_room"],
        value=5,
        aliases=["key", "ornate key", "strange key", "treasure key"]
    )
}

TOOLS = {
    "torch": Tool(
        "torch", 
        "A wooden torch that can be lit to illuminate dark areas.",
        tool_type="light",
        value=2,
        aliases=["light", "wooden torch", "fire"]
    ),
    "boat": Tool(
        "boat", 
        "A small wooden boat, just big enough for one person.",
        tool_type="navigation",
        value=10,
        aliases=["raft", "canoe", "wooden boat"]
    ),
    "pickaxe": Tool(
        "pickaxe", 
        "A sturdy pickaxe for mining.",
        tool_type="mining",
        value=8,
        aliases=["pick", "mining tool", "axe"]
    )
}

def get_gem(gem_name):
    """Get a gem from the predefined gems"""
    return GEMS.get(gem_name)

def get_quest_item(item_name):
    """Get a quest item from the predefined quest items"""
    return QUEST_ITEMS.get(item_name)

def get_key(key_name):
    """Get a key from the predefined keys"""
    return KEYS.get(key_name)

def get_tool(tool_name):
    """Get a tool from the predefined tools"""
    return TOOLS.get(tool_name)

# treasure_box.py
import random
from items.item import Item
from core.utils import calculate_chance, get_random_element

class TreasureBox(Item):
    """
    A locked treasure box that can be opened with the appropriate key.
    Contains random loot based on the box's rarity level.
    """
    def __init__(self, name, description, rarity="common", required_key=None, value=5, aliases=None):
        """
        Initialize a treasure box
        
        Args:
            name (str): Internal name of the box
            description (str): Human-readable description
            rarity (str): Rarity level (common, uncommon, rare, epic, legendary)
            required_key (str): Name of the key item required to open this box
            value (int): Base value in coins
            aliases (list): Alternative names for the item
        """
        super().__init__(name, description, value, stackable=False, usable=True, aliases=aliases)
        self.rarity = rarity
        self.required_key = required_key or f"{rarity}_box_key"
        self.type = "treasure_box"
        
        # Set default aliases if none provided
        if not aliases:
            self.aliases = [rarity + " box", "box", "chest", "treasure"]
    
    def can_use(self, game_state):
        """Check if the box can be used (opened) - player must have the right key"""
        return game_state.player.has_item(self.required_key)
    
    def use(self, game_state):
        """Try to open the treasure box with a key"""
        if not self.can_use(game_state):
            return False, f"You need a {self.required_key.replace('_', ' ')} to open this {self.display_name()}."
        
        # Remove key if it's consumed when used
        from items.item_factory import ItemFactory
        key_item = ItemFactory.get_item(self.required_key)
        if key_item and hasattr(key_item, 'single_use') and key_item.single_use:
            game_state.player.remove_from_inventory(self.required_key)
            key_consumed_msg = f"The {key_item.display_name()} breaks after use."
        else:
            key_consumed_msg = ""
        
        # Generate loot based on rarity
        loot = self.generate_loot(game_state)
        
        # Add loot to player inventory
        loot_messages = []
        coins_found = 0
        
        for item_name, quantity in loot.items():
            if item_name == "coin":
                coins_found = quantity
                game_state.coins += quantity
                loot_messages.append(f"{quantity} coins")
            else:
                # Add non-coin items to inventory
                for _ in range(quantity):
                    game_state.player.add_to_inventory(item_name)
                
                # Get display name for message
                item_obj = ItemFactory.get_item(item_name)
                if item_obj:
                    if quantity > 1:
                        loot_messages.append(f"{quantity}x {item_obj.display_name()}")
                    else:
                        loot_messages.append(item_obj.display_name())
                else:
                    loot_messages.append(f"{quantity}x {item_name.replace('_', ' ')}")
        
        # Create result message
        if loot_messages:
            loot_list = ", ".join(loot_messages)
            result_msg = f"You open the {self.display_name()} and find: {loot_list}."
            if key_consumed_msg:
                result_msg += " " + key_consumed_msg
            return True, result_msg
        else:
            return True, f"You open the {self.display_name()}, but it's empty! {key_consumed_msg}"
    
    def generate_loot(self, game_state):
        """
        Generate random loot based on the box's rarity
        
        Returns:
            dict: Dictionary of {item_name: quantity}
        """
        loot = {}
        
        # Base number of items depends on rarity
        rarity_item_counts = {
            "common": (1, 2),     # 1-2 items
            "uncommon": (2, 3),   # 2-3 items
            "rare": (2, 4),       # 2-4 items
            "epic": (3, 5),       # 3-5 items
            "legendary": (4, 6)   # 4-6 items
        }
        
        # Coin amounts based on rarity
        rarity_coin_ranges = {
            "common": (5, 15),       # 5-15 coins
            "uncommon": (10, 25),    # 10-25 coins
            "rare": (20, 50),        # 20-50 coins
            "epic": (40, 80),        # 40-80 coins
            "legendary": (75, 150)   # 75-150 coins
        }
        
        # Chance to find special items based on rarity
        rarity_special_chance = {
            "common": 0.1,      # 10% chance for special item
            "uncommon": 0.2,    # 20% chance
            "rare": 0.4,        # 40% chance
            "epic": 0.6,        # 60% chance
            "legendary": 0.9    # 90% chance
        }
        
        # Always add coins
        coin_range = rarity_coin_ranges.get(self.rarity, (5, 15))
        coin_amount = random.randint(coin_range[0], coin_range[1])
        
        # Player level can influence coin amount (higher level = more coins)
        player_level_bonus = game_state.player.level - 1  # No bonus at level 1
        if player_level_bonus > 0:
            coin_amount += random.randint(1, player_level_bonus * 5)
            
        loot["coin"] = coin_amount
        
        # Determine number of additional items
        item_count_range = rarity_item_counts.get(self.rarity, (1, 2))
        item_count = random.randint(item_count_range[0], item_count_range[1])
        
        # Get possible loot items based on rarity
        possible_loot = self._get_possible_loot(self.rarity)
        
        # Add random items from possible loot
        for _ in range(item_count):
            if not possible_loot:
                break
                
            # Select an item based on its weight
            item_choices = list(possible_loot.keys())
            item_weights = [info["weight"] for info in possible_loot.values()]
            selected_item = random.choices(item_choices, weights=item_weights, k=1)[0]
            
            # Determine quantity
            quantity_range = possible_loot[selected_item].get("quantity", (1, 1))
            quantity = random.randint(quantity_range[0], quantity_range[1])
            
            # Add to loot
            if selected_item in loot:
                loot[selected_item] += quantity
            else:
                loot[selected_item] = quantity
                
            # Don't pick the same item twice unless it's consumable
            from items.item_factory import ItemFactory
            item_obj = ItemFactory.get_item(selected_item)
            if item_obj and not getattr(item_obj, "stackable", False):
                del possible_loot[selected_item]
        
        # Chance for a special item (gem, weapon, armor)
        special_chance = rarity_special_chance.get(self.rarity, 0.1)
        if random.random() < special_chance:
            special_items = self._get_special_loot(self.rarity)
            if special_items:
                special_item = random.choice(list(special_items.keys()))
                loot[special_item] = 1
        
        return loot
    
    def _get_possible_loot(self, rarity):
        """Get possible loot items for a given rarity"""
        # This is a simplified loot table - you can expand it as needed
        loot_table = {
            "common": {
                "healing_potion": {"weight": 5, "quantity": (1, 1)},
                "bread": {"weight": 3, "quantity": (1, 2)},
                "stick": {"weight": 2, "quantity": (1, 2)},
                "cloth": {"weight": 2, "quantity": (1, 2)},
                "torch": {"weight": 1, "quantity": (1, 1)}
            },
            "uncommon": {
                "healing_potion": {"weight": 5, "quantity": (1, 2)},
                "cooked_meat": {"weight": 3, "quantity": (1, 2)},
                "stamina_potion": {"weight": 2, "quantity": (1, 1)},
                "gem": {"weight": 1, "quantity": (1, 1)}
            },
            "rare": {
                "strong_healing_potion": {"weight": 4, "quantity": (1, 1)},
                "stamina_potion": {"weight": 3, "quantity": (1, 2)},
                "ruby": {"weight": 2, "quantity": (1, 1)},
                "sapphire": {"weight": 2, "quantity": (1, 1)}
            },
            "epic": {
                "strong_healing_potion": {"weight": 4, "quantity": (1, 2)},
                "emerald": {"weight": 3, "quantity": (1, 1)},
                "stamina_potion": {"weight": 2, "quantity": (1, 3)}
            },
            "legendary": {
                "strong_healing_potion": {"weight": 3, "quantity": (2, 3)},
                "diamond": {"weight": 2, "quantity": (1, 1)},
                "stamina_potion": {"weight": 2, "quantity": (2, 4)}
            }
        }
        
        # Combine loot tables from current rarity and lower rarities
        rarities_to_include = []
        if rarity == "legendary":
            rarities_to_include = ["epic", "rare", "uncommon", "common", "legendary"]
        elif rarity == "epic":
            rarities_to_include = ["rare", "uncommon", "common", "epic"]
        elif rarity == "rare":
            rarities_to_include = ["uncommon", "common", "rare"]
        elif rarity == "uncommon":
            rarities_to_include = ["common", "uncommon"]
        else:
            rarities_to_include = ["common"]
            
        combined_loot = {}
        for r in rarities_to_include:
            if r in loot_table:
                for item, info in loot_table[r].items():
                    # Higher rarities have higher weight for their specific items
                    if r == rarity:
                        info["weight"] *= 2
                    combined_loot[item] = info
                
        return combined_loot
    
    def _get_special_loot(self, rarity):
        """Get possible special loot items (rare equipment/items)"""
        special_loot = {
            "common": {
                "rusty_sword": 5,
                "leather_armor": 5
            },
            "uncommon": {
                "steel_sword": 5,
                "chainmail": 5,
                "uncommon_box_key": 2
            },
            "rare": {
                "ancient_blade": 5,
                "plate_armor": 5,
                "rare_box_key": 2
            },
            "epic": {
                "enchanted_sword": 5,
                "reinforced_leather_armor": 5,
                "epic_box_key": 2
            },
            "legendary": {
                "legendary_box_key": 5,
                "ancient_scroll": 3,
                "golden_crown": 2
            }
        }
        
        # Return appropriate special loot based on rarity
        result = {}
        
        # Include current rarity and possible one level higher
        if rarity in special_loot:
            result.update({item: {"weight": weight} for item, weight in special_loot[rarity].items()})
            
        # Small chance for items from 1 tier lower (if available)
        lower_rarities = {
            "legendary": "epic",
            "epic": "rare",
            "rare": "uncommon",
            "uncommon": "common"
        }
        
        if rarity in lower_rarities and random.random() < 0.3:  # 30% chance
            lower_rarity = lower_rarities[rarity]
            if lower_rarity in special_loot:
                result.update({item: {"weight": weight/2} for item, weight in special_loot[lower_rarity].items()})
        
        return result


# Define different treasure box types
TREASURE_BOXES = {
    "common_treasure_box": TreasureBox(
        "common_treasure_box",
        "A simple wooden box with a basic lock. It might contain some useful items.",
        rarity="common",
        required_key="common_box_key",
        value=5,
        aliases=["wooden box", "small chest", "common chest"]
    ),
    "uncommon_treasure_box": TreasureBox(
        "uncommon_treasure_box",
        "A sturdy box with iron reinforcements. The lock looks more complex than usual.",
        rarity="uncommon",
        required_key="uncommon_box_key",
        value=15,
        aliases=["iron box", "reinforced chest", "sturdy chest"]
    ),
    "rare_treasure_box": TreasureBox(
        "rare_treasure_box",
        "An ornate box with silver decorations. It feels heavy, suggesting valuable contents.",
        rarity="rare",
        required_key="rare_box_key",
        value=30,
        aliases=["silver box", "ornate chest", "valuable chest"]
    ),
    "epic_treasure_box": TreasureBox(
        "epic_treasure_box",
        "A beautiful gold-inlaid box with intricate patterns. The lock is masterfully crafted.",
        rarity="epic",
        required_key="epic_box_key",
        value=50,
        aliases=["golden box", "intricate chest", "premium chest"]
    ),
    "legendary_treasure_box": TreasureBox(
        "legendary_treasure_box",
        "A stunning box that seems to shimmer with magical energy. The lock has strange runes.",
        rarity="legendary",
        required_key="legendary_box_key",
        value=100,
        aliases=["magical box", "runic chest", "legendary chest"]
    )
}

def get_treasure_box(box_name):
    """Get a treasure box from the predefined boxes"""
    return TREASURE_BOXES.get(box_name)

def get_random_treasure_box(rarity=None):
    """
    Get a random treasure box, optionally of a specific rarity
    
    Args:
        rarity (str, optional): Specific rarity to get, or None for weighted random
        
    Returns:
        TreasureBox: A treasure box instance
    """
    if rarity:
        # Find a box of the specified rarity
        for box_name, box in TREASURE_BOXES.items():
            if box.rarity == rarity:
                return box
    
    # Default weight distribution for random boxes
    box_weights = {
        "common_treasure_box": 100,
        "uncommon_treasure_box": 50,
        "rare_treasure_box": 20,
        "epic_treasure_box": 5,
        "legendary_treasure_box": 1
    }
    
    # Select a random box based on weights
    box_names = list(box_weights.keys())
    weights = list(box_weights.values())
    
    selected_box_name = random.choices(box_names, weights=weights, k=1)[0]
    return TREASURE_BOXES.get(selected_box_name)

# weapon.py
from items.item import Item

class Weapon(Item):
    def __init__(self, name, description, attack_bonus, value=10, 
                 durability=None, requirements=None, aliases=None):
        """
        Weapon class for all weapon items
        
        Args:
            name (str): Internal name of the weapon
            description (str): Human-readable description
            attack_bonus (int): Attack bonus provided by the weapon
            value (int): Base value in coins
            durability (int, optional): Durability points, None for indestructible
            requirements (dict, optional): Player requirements to use (e.g., {"level": 3})
            aliases (list): Alternative names for the weapon
        """
        super().__init__(name, description, value, stackable=False, usable=False, aliases=aliases)
        self.attack_bonus = attack_bonus
        self.durability = durability
        self.max_durability = durability
        self.requirements = requirements or {}
        self.type = "weapon"
    
    def get_attack_bonus(self):
        """Return the attack bonus provided by this weapon"""
        return self.attack_bonus
    
    def meets_requirements(self, player):
        """Check if player meets the requirements to use this weapon"""
        for req, value in self.requirements.items():
            if req == "level" and player.level < value:
                return False
        return True
    
    def __str__(self):
        return f"{self.display_name()} (+{self.attack_bonus} ATK)"


# Predefined weapons
WEAPONS = {
    "rusty_sword": Weapon(
        "rusty_sword", 
        "An old, rusty sword. It's seen better days but still cuts.",
        attack_bonus=5,
        value=7,
        aliases=["rusty", "old sword"]
    ),
    "steel_sword": Weapon(
        "steel_sword", 
        "A well-crafted steel sword, sharp and reliable.",
        attack_bonus=10,
        value=25,
        requirements={"level": 2},
        aliases=["steel", "good sword"]
    ),
    "ancient_blade": Weapon(
        "ancient_blade", 
        "A mysterious blade of unknown origin. It seems to hum with power.",
        attack_bonus=15,
        value=50,
        requirements={"level": 3},
        aliases=["ancient", "mysterious blade", "powerful sword"]
    )
}

def get_weapon(weapon_name):
    """Get a weapon from the predefined weapons"""
    return WEAPONS.get(weapon_name)

# crafting.py
from items.item_factory import ItemFactory

class CraftingSystem:
    def __init__(self):
        # Recipe definitions: {result_item: {ingredient1: count1, ingredient2: count2, ...}}
        self.recipes = {
            "strong_healing_potion": {"healing_potion": 2, "gem": 1},
            "torch": {"stick": 1, "cloth": 1},
            "reinforced_leather_armor": {"leather_armor": 1, "gem": 2},
            "enchanted_sword": {"steel_sword": 1, "ruby": 1, "sapphire": 1}
        }
        
        # Define new crafted items
        self._initialize_crafted_items()
    
    def _initialize_crafted_items(self):
        """Add new craftable items to the appropriate item collections"""
        from items.weapon import WEAPONS, Weapon
        from items.armor import ARMORS, Armor
        from items.item import Item
        
        # First, create a dictionary of basic items for crafting
        # We'll store these in a new module-level variable in ItemFactory
        from items.treasure import TOOLS  # We'll add our items to TOOLS collection since they are tool-like
        
        # Add a stick item (needed for torch crafting)
        if "stick" not in TOOLS:
            TOOLS["stick"] = Item(
                "stick", 
                "A simple wooden stick.", 
                value=1, 
                stackable=True, 
                max_stack=10,
                aliases=["branch", "wood"]
            )
        
        # Add cloth item (needed for torch crafting)
        if "cloth" not in TOOLS:
            TOOLS["cloth"] = Item(
                "cloth", 
                "A piece of cloth.", 
                value=1, 
                stackable=True, 
                max_stack=10,
                aliases=["fabric", "rag"]
            )
        
        # Add reinforced leather armor
        if "reinforced_leather_armor" not in ARMORS:
            ARMORS["reinforced_leather_armor"] = Armor(
                "reinforced_leather_armor", 
                "Leather armor reinforced with gemstones, offering improved protection.",
                defense_bonus=5,
                value=25,
                aliases=["reinforced leather", "gem leather", "reinforced armor"]
            )
        
        # Add enchanted sword
        if "enchanted_sword" not in WEAPONS:
            WEAPONS["enchanted_sword"] = Weapon(
                "enchanted_sword", 
                "A sword infused with magical gems, glowing with arcane energy.",
                attack_bonus=18,
                value=75,
                requirements={"level": 3},
                aliases=["enchanted blade", "magic sword", "glowing sword"]
            )
    
    def get_available_recipes(self, player):
        """Get recipes that the player can currently craft with their inventory"""
        available_recipes = {}
        
        for result, ingredients in self.recipes.items():
            can_craft = True
            
            # Check if player has all required ingredients
            for ingredient, count in ingredients.items():
                if not player.has_item(ingredient, count):
                    can_craft = False
                    break
            
            if can_craft:
                available_recipes[result] = ingredients
        
        return available_recipes
    
    def craft_item(self, game_state, recipe_name):
        """Attempt to craft an item from a recipe"""
        player = game_state.player
        
        # Find best matching recipe name
        best_match = None
        for result in self.recipes.keys():
            if result.replace('_', ' ') == recipe_name.lower():
                best_match = result
                break
            elif recipe_name.lower() in result.replace('_', ' '):
                best_match = result
                break
        
        if not best_match:
            # Try checking crafted item display names
            for result in self.recipes.keys():
                item = ItemFactory.get_item(result)
                if item and recipe_name.lower() in item.display_name().lower():
                    best_match = result
                    break
        
        if not best_match:
            return False, f"You don't know how to craft '{recipe_name}'."
        
        recipe_result = best_match
        recipe = self.recipes[recipe_result]
        
        # Check if player has all ingredients
        for ingredient, count in recipe.items():
            if not player.has_item(ingredient, count):
                item_obj = ItemFactory.get_item(ingredient)
                item_name = item_obj.display_name() if item_obj else ingredient.replace('_', ' ')
                return False, f"You need {count}x {item_name} to craft this."
        
        # Remove ingredients from inventory
        for ingredient, count in recipe.items():
            player.remove_from_inventory(ingredient, count)
        
        # Add crafted item to inventory
        player.add_to_inventory(recipe_result)
        
        # Get display names for a better message
        result_item = ItemFactory.get_item(recipe_result)
        
        if result_item:
            return True, f"You successfully crafted {result_item.display_name()}!"
        else:
            return True, f"You successfully crafted {recipe_result.replace('_', ' ')}!"
    
    def display_recipes(self, game_state):
        """Display available crafting recipes to the player"""
        player = game_state.player
        available = self.get_available_recipes(player)
        
        if not available:
            game_state.add_to_history("You don't have the ingredients to craft anything right now.")
            return
        
        game_state.add_to_history("Available Crafting Recipes:", (255, 255, 100))  # TITLE_COLOR
        
        for result, ingredients in available.items():
            result_item = ItemFactory.get_item(result)
            if not result_item:
                continue
                
            # Format ingredient list
            ingredient_text = []
            for ing_name, ing_count in ingredients.items():
                ing_item = ItemFactory.get_item(ing_name)
                if ing_item:
                    ingredient_text.append(f"{ing_count}x {ing_item.display_name()}")
                else:
                    ingredient_text.append(f"{ing_count}x {ing_name.replace('_', ' ')}")
            
            # Show special properties of the crafted item
            properties = ""
            if result_item.type == "weapon":
                properties = f" (+{result_item.attack_bonus} ATK)"
            elif result_item.type == "armor":
                properties = f" (+{result_item.defense_bonus} DEF)"
            
            game_state.add_to_history(f"• {result_item.display_name()}{properties}: {', '.join(ingredient_text)}")
        
        game_state.add_to_history("\nUse 'craft [item name]' to create an item.")
    
    def debug_items(self, game_state):
        """Debug function to check if items are properly registered"""
        game_state.add_to_history("Checking crafting materials in ItemFactory:", (255, 255, 100))
        
        # Test if items can be retrieved
        stick = ItemFactory.get_item("stick")
        cloth = ItemFactory.get_item("cloth")
        
        if stick:
            game_state.add_to_history(f"✓ Stick found: {stick.display_name()}")
        else:
            game_state.add_to_history("✗ Stick NOT found in ItemFactory!")
            
        if cloth:
            game_state.add_to_history(f"✓ Cloth found: {cloth.display_name()}")
        else:
            game_state.add_to_history("✗ Cloth NOT found in ItemFactory!")
            
        # Check if these items can be found via partial matching too
        stick_match = ItemFactory.find_item_by_name("stick")
        cloth_match = ItemFactory.find_item_by_name("cloth")
        branch_match = ItemFactory.find_item_by_name("branch")  # alias for stick
        
        game_state.add_to_history(f"Finding by name - stick: {stick_match}, cloth: {cloth_match}, branch: {branch_match}")

# enemy_drops.py
import random
from core.utils import calculate_chance

def get_enemy_drops(enemy_name, enemy_health_percentage, player_level):
    """
    Generate drops when an enemy is defeated
    
    Args:
        enemy_name (str): The name of the defeated enemy
        enemy_health_percentage (float): Original enemy health as percentage of max
                                         (higher percentage = stronger enemy)
        player_level (int): Current player level
        
    Returns:
        dict: Dictionary of {item_name: quantity} representing drops
    """
    drops = {}
    
    # Base drop rates for different enemy types
    drop_rates = {
        # format: {item_category: base_chance}
        "goblin": {
            "common_treasure_box": 0.1,  # 10% chance
            "uncommon_treasure_box": 0.03,
            "common_box_key": 0.15,
            "gold": (2, 10)  # Gold range (min, max)
        },
        "skeleton": {
            "common_treasure_box": 0.15,
            "uncommon_treasure_box": 0.05,
            "rare_treasure_box": 0.01,
            "common_box_key": 0.2,
            "uncommon_box_key": 0.05,
            "gold": (3, 12)
        },
        "troll": {
            "common_treasure_box": 0.2,
            "uncommon_treasure_box": 0.1,
            "rare_treasure_box": 0.03,
            "common_box_key": 0.25,
            "uncommon_box_key": 0.1,
            "rare_box_key": 0.02,
            "gold": (5, 20)
        },
        "orc": {
            "common_treasure_box": 0.18,
            "uncommon_treasure_box": 0.08,
            "rare_treasure_box": 0.02,
            "common_box_key": 0.23,
            "uncommon_box_key": 0.07,
            "gold": (4, 15)
        },
        "spider": {
            "common_treasure_box": 0.08,
            "common_box_key": 0.12,
            "gold": (1, 8)
        },
        "ghost": {
            "uncommon_treasure_box": 0.15,
            "rare_treasure_box": 0.05,
            "uncommon_box_key": 0.2,
            "rare_box_key": 0.05,
            "gold": (3, 15)
        },
        "rat": {
            "common_treasure_box": 0.05,
            "common_box_key": 0.1,
            "gold": (1, 5)
        },
        "bat": {
            "common_box_key": 0.08,
            "gold": (1, 4)
        },
        "slime": {
            "common_treasure_box": 0.07,
            "common_box_key": 0.1,
            "gold": (1, 6)
        },
        "zombie": {
            "common_treasure_box": 0.12,
            "uncommon_treasure_box": 0.04,
            "common_box_key": 0.18,
            "uncommon_box_key": 0.04,
            "gold": (2, 10)
        }
    }
    
    # Get proper drop rates for this enemy
    # Match by partial name (e.g., "hobgoblin" should use "goblin" rates)
    enemy_rate = None
    for rate_name, rates in drop_rates.items():
        if rate_name in enemy_name:
            enemy_rate = rates
            break
    
    # Use generic rates if no specific match
    if not enemy_rate:
        enemy_rate = {
            "common_treasure_box": 0.1,
            "common_box_key": 0.15,
            "gold": (1, 8)
        }
    
    # Add gold/coins drop (almost always drops some gold)
    if "gold" in enemy_rate and random.random() < 0.9:  # 90% chance for gold
        gold_range = enemy_rate["gold"]
        # Adjust gold based on enemy health and player level
        min_gold = max(1, int(gold_range[0] * enemy_health_percentage))
        max_gold = max(min_gold, int(gold_range[1] * enemy_health_percentage))
        
        # Player level bonus
        level_bonus = max(0, player_level - 1)  # No bonus at level 1
        if level_bonus > 0:
            min_gold += level_bonus // 2
            max_gold += level_bonus
            
        gold_amount = random.randint(min_gold, max_gold)
        drops["coin"] = gold_amount
    
    # Process treasure box drops
    for drop_type, base_chance in enemy_rate.items():
        # Skip non-treasure drops
        if drop_type == "gold" or not (drop_type.endswith("_treasure_box") or drop_type.endswith("_box_key")):
            continue
            
        # Calculate actual drop chance with modifiers
        modifiers = []
        
        # Higher level enemies drop better loot
        if enemy_health_percentage > 0.8:
            modifiers.append(0.1)  # +10% for strong enemies
        
        # Higher player levels slightly increase rare drops
        if player_level > 1 and ("rare" in drop_type or "epic" in drop_type or "legendary" in drop_type):
            level_bonus = min(0.1, (player_level - 1) * 0.02)  # Up to +10% at level 6+
            modifiers.append(level_bonus)
        
        # Calculate final chance with all modifiers
        final_chance = calculate_chance(base_chance, modifiers)
        
        # Check if this item drops
        if random.random() < final_chance:
            drops[drop_type] = 1  # Most drops are quantity 1
    
    # Special case: extremely rare legendary drops from any enemy
    if random.random() < 0.001 * player_level * enemy_health_percentage:  # Very rare, affected by level and enemy strength
        if random.random() < 0.7:
            drops["legendary_box_key"] = 1
        else:
            drops["legendary_treasure_box"] = 1
    
    return drops

# journal.py
import time
import textwrap
from datetime import datetime

class Journal:
    """
    Journal system to track player progress, quests, and discoveries
    """
    def __init__(self, game_state):
        self.game_state = game_state
        self.entries = []  # List of journal entries
        self.quest_notes = {}  # Notes for specific quests
        self.region_notes = {}  # Notes for discovered regions
        self.achievements = []  # List of achievements
        self.stats = {
            "enemies_killed": {},  # Format: {enemy_type: count}
            "items_collected": {},  # Format: {item_name: count}
            "regions_discovered": 0,
            "quests_completed": 0,
            "coins_earned": 0,
            "distance_traveled": 0,  # Count of room transitions
            "creation_time": time.time(),
            "play_time": 0
        }
        
    def add_entry(self, text, category="general"):
        """Add a new journal entry"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = {
            "timestamp": timestamp,
            "text": text,
            "category": category
        }
        self.entries.append(entry)
        return entry
    
    def add_quest_note(self, quest_id, note):
        """Add a note to a specific quest"""
        if quest_id not in self.quest_notes:
            self.quest_notes[quest_id] = []
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = {
            "timestamp": timestamp,
            "text": note
        }
        self.quest_notes[quest_id].append(entry)
        return entry
    
    def add_region_note(self, region_name, note):
        """Add a note about a specific region"""
        if region_name not in self.region_notes:
            self.region_notes[region_name] = []
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = {
            "timestamp": timestamp,
            "text": note
        }
        self.region_notes[region_name].append(entry)
        return entry
    
    def add_achievement(self, title, description):
        """Add a new achievement"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        achievement = {
            "timestamp": timestamp,
            "title": title,
            "description": description
        }
        self.achievements.append(achievement)
        return achievement
    
    def update_stats(self, stat_name, value=1, sub_category=None):
        """Update player statistics"""
        if sub_category:
            if stat_name not in self.stats:
                self.stats[stat_name] = {}
            
            if sub_category not in self.stats[stat_name]:
                self.stats[stat_name][sub_category] = 0
                
            self.stats[stat_name][sub_category] += value
        else:
            if stat_name not in self.stats:
                self.stats[stat_name] = 0
                
            self.stats[stat_name] += value
    
    def get_recent_entries(self, count=5, category=None):
        """Get recent journal entries, optionally filtered by category"""
        filtered_entries = self.entries
        if category:
            filtered_entries = [e for e in self.entries if e["category"] == category]
            
        return filtered_entries[-count:] if filtered_entries else []
    
    def get_quest_log(self):
        """Get a formatted quest log with active and completed quests"""
        active_quests = self.game_state.quest_manager.get_active_quests()
        completed_quests = self.game_state.quest_manager.get_completed_quests()
        
        quest_log = {
            "active": [],
            "completed": []
        }
        
        for quest in active_quests:
            quest_info = {
                "id": quest.quest_id,
                "name": quest.name,
                "description": quest.description,
                "progress": quest.get_task_progress(),
                "notes": self.quest_notes.get(quest.quest_id, []),
                "completed": quest.completed
            }
            quest_log["active"].append(quest_info)
        
        for quest in completed_quests:
            quest_info = {
                "id": quest.quest_id,
                "name": quest.name,
                "description": quest.description,
                "notes": self.quest_notes.get(quest.quest_id, [])
            }
            quest_log["completed"].append(quest_info)
            
        return quest_log
    
    def get_region_log(self):
        """Get information about discovered regions"""
        region_log = {}
        
        for region in self.game_state.world.get_all_regions():
            if region.discovered:
                region_info = {
                    "name": region.name,
                    "display_name": region.display_name,
                    "description": region.description,
                    "notes": self.region_notes.get(region.name, []),
                    "rooms_visited": []
                }
                
                # Count rooms visited in this region
                for room_name in region.get_all_room_names():
                    # We don't have a "visited" flag for rooms,
                    # so we'll rely on the existence of region notes
                    if self.region_notes.get(region.name):
                        region_info["rooms_visited"].append(room_name)
                
                region_log[region.name] = region_info
        
        return region_log
    
    def get_stats_summary(self):
        """Get a summary of player statistics"""
        # Update play time
        current_time = time.time()
        creation_time = self.stats.get("creation_time", current_time)
        self.stats["play_time"] = current_time - creation_time
        
        # Format play time
        play_hours = int(self.stats["play_time"] / 3600)
        play_minutes = int((self.stats["play_time"] % 3600) / 60)
        
        # Create summary
        summary = {
            "play_time": f"{play_hours}h {play_minutes}m",
            "enemies_killed": sum(self.stats.get("enemies_killed", {}).values()),
            "enemies_by_type": self.stats.get("enemies_killed", {}),
            "items_collected": sum(self.stats.get("items_collected", {}).values()),
            "items_by_type": self.stats.get("items_collected", {}),
            "regions_discovered": self.stats.get("regions_discovered", 0),
            "quests_completed": self.stats.get("quests_completed", 0),
            "coins_earned": self.stats.get("coins_earned", 0),
            "distance_traveled": self.stats.get("distance_traveled", 0)
        }
        
        return summary
    
    def save_to_dict(self):
        """Convert journal to a dictionary for saving"""
        return {
            "entries": self.entries,
            "quest_notes": self.quest_notes,
            "region_notes": self.region_notes,
            "achievements": self.achievements,
            "stats": self.stats
        }
    
    def load_from_dict(self, data):
        """Load journal from a dictionary"""
        if "entries" in data:
            self.entries = data["entries"]
        if "quest_notes" in data:
            self.quest_notes = data["quest_notes"]
        if "region_notes" in data:
            self.region_notes = data["region_notes"]
        if "achievements" in data:
            self.achievements = data["achievements"]
        if "stats" in data:
            self.stats = data["stats"]

    def track_combat(self, enemy_name, damage_dealt, damage_taken, victory):
        """Track combat statistics
        
        Args:
            enemy_name (str): Name of the enemy
            damage_dealt (int): Damage dealt to enemy
            damage_taken (int): Damage taken from enemy
            victory (bool): Whether player won the combat
        """
        # Initialize combat stats if first combat
        if "combat_stats" not in self.stats:
            self.stats["combat_stats"] = {
                "total_battles": 0,
                "victories": 0,
                "defeats": 0,
                "damage_dealt": 0,
                "damage_taken": 0,
                "enemies_fought": {},
                "critical_hits": 0,
                "near_death_escapes": 0
            }
        
        # Update combat statistics
        self.stats["combat_stats"]["total_battles"] += 1
        self.stats["combat_stats"]["damage_dealt"] += damage_dealt
        self.stats["combat_stats"]["damage_taken"] += damage_taken
        
        if victory:
            self.stats["combat_stats"]["victories"] += 1
        else:
            self.stats["combat_stats"]["defeats"] += 1
        
        # Track enemy-specific stats
        if enemy_name not in self.stats["combat_stats"]["enemies_fought"]:
            self.stats["combat_stats"]["enemies_fought"][enemy_name] = {
                "battles": 0,
                "victories": 0,
                "defeats": 0,
                "damage_dealt": 0,
                "damage_taken": 0
            }
        
        enemy_stats = self.stats["combat_stats"]["enemies_fought"][enemy_name]
        enemy_stats["battles"] += 1
        enemy_stats["damage_dealt"] += damage_dealt
        enemy_stats["damage_taken"] += damage_taken
        
        if victory:
            enemy_stats["victories"] += 1
        else:
            enemy_stats["defeats"] += 1
        
        # Check for critical hits (high damage in a single attack)
        if damage_dealt > 15:  # Arbitrary threshold
            self.stats["combat_stats"]["critical_hits"] += 1
            
            # Add achievement for first critical hit
            if self.stats["combat_stats"]["critical_hits"] == 1:
                self.add_achievement(
                    "Deadly Precision", 
                    "Dealt a devastating blow to an enemy."
                )
        
        # Check for combat-based achievements
        self._check_combat_achievements()
        
        return True

    def _check_combat_achievements(self):
        """Check and award combat-related achievements"""
        stats = self.stats.get("combat_stats", {})
        
        # Achievement for first victory
        if stats.get("victories", 0) == 1:
            self.add_achievement(
                "First Blood", 
                "Defeated your first enemy in combat."
            )
        
        # Achievement for 10 victories
        elif stats.get("victories", 0) == 10:
            self.add_achievement(
                "Battle-Hardened", 
                "Emerged victorious from 10 battles."
            )
        
        # Achievement for 50 victories
        elif stats.get("victories", 0) == 50:
            self.add_achievement(
                "Legendary Warrior", 
                "Defeated 50 enemies in combat."
            )
        
        # Achievement for dealing 500+ damage total
        if stats.get("damage_dealt", 0) >= 500 and not self._has_achievement("Damage Dealer"):
            self.add_achievement(
                "Damage Dealer", 
                "Dealt over 500 points of damage to enemies."
            )
        
        # Achievement for surviving 5+ battles with very low health
        if stats.get("near_death_escapes", 0) >= 5 and not self._has_achievement("Brush with Death"):
            self.add_achievement(
                "Brush with Death", 
                "Survived 5 battles with critically low health."
            )

    def _has_achievement(self, title):
        """Check if player has a specific achievement"""
        return any(a.get("title") == title for a in self.achievements)

    # Add this method to get combat details for display
    def get_combat_stats(self):
        """Get detailed combat statistics"""
        stats = self.stats.get("combat_stats", {
            "total_battles": 0,
            "victories": 0,
            "defeats": 0,
            "damage_dealt": 0,
            "damage_taken": 0
        })
        
        # Calculate win rate
        total_battles = stats.get("total_battles", 0)
        win_rate = 0
        if total_battles > 0:
            win_rate = (stats.get("victories", 0) / total_battles) * 100
        
        # Format combat summary
        summary = {
            "total_battles": total_battles,
            "victories": stats.get("victories", 0),
            "defeats": stats.get("defeats", 0),
            "win_rate": f"{win_rate:.1f}%",
            "damage_dealt": stats.get("damage_dealt", 0),
            "damage_taken": stats.get("damage_taken", 0),
            "critical_hits": stats.get("critical_hits", 0),
            "near_death_escapes": stats.get("near_death_escapes", 0),
            "top_enemies": []
        }
        
        # Get top 5 most fought enemies
        enemies = stats.get("enemies_fought", {})
        sorted_enemies = sorted(
            enemies.items(),
            key=lambda x: x[1].get("battles", 0),
            reverse=True
        )
        
        for enemy_name, enemy_stats in sorted_enemies[:5]:
            enemy_wins = enemy_stats.get("victories", 0)
            enemy_battles = enemy_stats.get("battles", 0)
            enemy_win_rate = 0
            if enemy_battles > 0:
                enemy_win_rate = (enemy_wins / enemy_battles) * 100
                
            summary["top_enemies"].append({
                "name": enemy_name,
                "battles": enemy_battles,
                "victories": enemy_wins,
                "win_rate": f"{enemy_win_rate:.1f}%",
                "damage_dealt": enemy_stats.get("damage_dealt", 0),
                "damage_taken": enemy_stats.get("damage_taken", 0)
            })
        
        return summary

# quest.py
class Quest:
    def __init__(self, quest_id, name, description, tasks, rewards, prereqs=None):
        """
        Initialize a new quest
        
        Args:
            quest_id (str): Unique identifier for this quest
            name (str): Display name of the quest
            description (str): Detailed description of the quest
            tasks (list): List of task dictionaries defining completion requirements
            rewards (dict): Rewards given when quest is completed
            prereqs (list, optional): List of quest IDs that must be completed first
        """
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.tasks = tasks  # [{type: "collect", target: "gem", count: 3}, {type: "kill", target: "goblin", count: 5}]
        self.rewards = rewards  # {"xp": 50, "coins": 100, "items": {"healing_potion": 2}}
        self.prereqs = prereqs or []
        
        # State tracking
        self.active = False
        self.completed = False
        self.progress = {}  # Will track progress on each task
        
        # Initialize progress counters for each task
        for task in self.tasks:
            if task.get("count", 1) > 1:
                self.progress[self._get_task_key(task)] = 0
    
    def _get_task_key(self, task):
        """Generate a unique key for a task for progress tracking"""
        task_type = task["type"]
        target = task.get("target", "")
        location = task.get("location", "")
        return f"{task_type}:{target}:{location}"
    
    def can_activate(self, completed_quests):
        """Check if this quest's prerequisites are met"""
        if not self.prereqs:
            return True
        return all(quest_id in completed_quests for quest_id in self.prereqs)
    
    def activate(self):
        """Mark the quest as active"""
        self.active = True
        return True
    
    def update_progress(self, event_type, target, location=None, count=1):
        """
        Update progress on a quest based on player actions
        
        Args:
            event_type (str): Type of event (collect, kill, visit, talk)
            target (str): Target of the event (item name, enemy type, location)
            location (str, optional): Location where event happened
            count (int): Number to increment (default 1)
            
        Returns:
            bool: True if any progress was made, False otherwise
        """
        if not self.active or self.completed:
            return False
        
        made_progress = False
        
        for task in self.tasks:
            if task["type"] != event_type:
                continue
                
            # Check if this action matches this task
            if "target" in task and task["target"] != target:
                continue
                
            # Check location constraint if specified
            if "location" in task and location and task["location"] != location:
                continue
            
            # Match found - update progress
            task_key = self._get_task_key(task)
            required_count = task.get("count", 1)
            
            if required_count == 1:
                # Simple completion task (no counter)
                self.progress[task_key] = True
                made_progress = True
            else:
                # Increment counter
                if task_key not in self.progress:
                    self.progress[task_key] = 0
                
                self.progress[task_key] = min(required_count, self.progress[task_key] + count)
                made_progress = True
        
        # Check if quest is now complete
        self._check_completion()
        
        return made_progress
    
    def _check_completion(self):
        """Check if all tasks are completed"""
        if self.completed:
            return True
            
        all_complete = True
        
        for task in self.tasks:
            task_key = self._get_task_key(task)
            required_count = task.get("count", 1)
            
            if required_count == 1:
                # Simple completion task
                if task_key not in self.progress or not self.progress[task_key]:
                    all_complete = False
                    break
            else:
                # Counter task
                if task_key not in self.progress or self.progress[task_key] < required_count:
                    all_complete = False
                    break
        
        self.completed = all_complete
        return all_complete
    
    def get_task_progress(self):
        """Get formatted progress for all tasks"""
        progress_text = []
        
        for task in self.tasks:
            task_key = self._get_task_key(task)
            required_count = task.get("count", 1)
            
            # Format based on task type
            if task["type"] == "kill":
                description = f"Defeat {required_count}x {task['target'].replace('_', ' ')}"
            elif task["type"] == "collect":
                description = f"Collect {required_count}x {task['target'].replace('_', ' ')}"
            elif task["type"] == "visit":
                description = f"Visit {task['target'].replace('_', ' ')}"
            elif task["type"] == "talk":
                description = f"Talk to {task['target'].replace('_', ' ')}"
            else:
                description = f"{task['type'].capitalize()} {task['target'].replace('_', ' ')}"
            
            # Add location if specified
            if "location" in task:
                description += f" in {task['location'].replace('_', ' ')}"
            
            # Add progress
            if required_count == 1:
                status = "✓" if task_key in self.progress and self.progress[task_key] else "□"
                progress_text.append(f"{status} {description}")
            else:
                current = self.progress.get(task_key, 0)
                status = "✓" if current >= required_count else f"{current}/{required_count}"
                progress_text.append(f"[{status}] {description}")
        
        return progress_text
    
    def get_rewards_text(self):
        """Get formatted text describing rewards"""
        reward_texts = []
        
        if "xp" in self.rewards and self.rewards["xp"] > 0:
            reward_texts.append(f"{self.rewards['xp']} XP")
            
        if "coins" in self.rewards and self.rewards["coins"] > 0:
            reward_texts.append(f"{self.rewards['coins']} coins")
            
        if "items" in self.rewards:
            from items.item_factory import ItemFactory
            for item_name, quantity in self.rewards["items"].items():
                item = ItemFactory.get_item(item_name)
                if item:
                    if quantity > 1:
                        reward_texts.append(f"{quantity}x {item.display_name()}")
                    else:
                        reward_texts.append(item.display_name())
                else:
                    reward_texts.append(f"{quantity}x {item_name.replace('_', ' ')}")
        
        return reward_texts
    
    def get_status(self):
        """Get the quest status (not started, in progress, complete)"""
        if self.completed:
            return "complete"
        elif self.active:
            return "active"
        else:
            return "inactive"

# quest_manager.py
from systems.quest import Quest

class QuestManager:
    def __init__(self, game_state):
        """
        Initialize the quest system
        
        Args:
            game_state (GameState): Reference to the game state
        """
        self.game_state = game_state
        self.quests = {}  # All available quests
        self.active_quests = set()  # IDs of active quests
        self.completed_quests = set()  # IDs of completed quests
        self.available_quest_indicator = False  # Whether to show indicators
        
        # Initialize with some basic quests
        self._initialize_quests()
    
    def _initialize_quests(self):
        """Create the initial set of quests"""
        # Starter quest - simple item collection
        self.add_quest(Quest(
            quest_id="beginners_quest",
            name="Adventurer's First Steps",
            description="Gather some basic supplies to start your adventure.",
            tasks=[
                {"type": "collect", "target": "torch", "count": 1},
                {"type": "collect", "target": "healing_potion", "count": 1}
            ],
            rewards={"xp": 10, "coins": 15}
        ))
        
        # Simple kill quest
        self.add_quest(Quest(
            quest_id="goblin_threat",
            name="Goblin Threat",
            description="The local goblins have been causing trouble. Reduce their numbers to make the caves safer.",
            tasks=[
                {"type": "kill", "target": "goblin", "count": 3}
            ],
            rewards={"xp": 25, "coins": 30, "items": {"healing_potion": 1}}
        ))
        
        # Exploration quest
        self.add_quest(Quest(
            quest_id="cave_explorer",
            name="Cave Explorer",
            description="Explore the cave system to map out the area.",
            tasks=[
                {"type": "visit", "target": "cavern"},
                {"type": "visit", "target": "narrow_passage"},
                {"type": "visit", "target": "underground_lake"}
            ],
            rewards={"xp": 20, "coins": 25, "items": {"torch": 1}}
        ))
        
        # Treasure hunt quest
        self.add_quest(Quest(
            quest_id="treasure_hunt",
            name="Treasure Hunter",
            description="Find valuable treasures hidden throughout the caves.",
            tasks=[
                {"type": "collect", "target": "gem", "count": 2},
                {"type": "collect", "target": "common_treasure_box", "count": 1}
            ],
            rewards={"xp": 30, "coins": 50}
        ))
        
        # Advanced quest - requires completion of earlier quests
        self.add_quest(Quest(
            quest_id="hidden_treasure",
            name="The Ancient Treasure",
            description="Legends speak of an ancient treasure guarded by a powerful key.",
            tasks=[
                {"type": "collect", "target": "ancient_key", "count": 1},
                {"type": "visit", "target": "treasure_room"}
            ],
            rewards={"xp": 50, "coins": 100, "items": {"ancient_blade": 1}},
            prereqs=["goblin_threat", "cave_explorer"]
        ))
    
    def add_quest(self, quest):
        """Add a new quest to the system"""
        self.quests[quest.quest_id] = quest
        return quest
    
    def get_quest(self, quest_id):
        """Get a quest by ID"""
        return self.quests.get(quest_id)
    
    def activate_quest(self, quest_id):
        """Activate a quest if possible"""
        quest = self.get_quest(quest_id)
        if not quest:
            return False, f"Quest '{quest_id}' not found."
            
        if quest.completed:
            return False, f"Quest '{quest.name}' is already completed."
            
        if quest.active:
            return False, f"Quest '{quest.name}' is already active."
            
        if not quest.can_activate(self.completed_quests):
            return False, f"You haven't completed the prerequisites for '{quest.name}'."
            
        quest.activate()
        self.active_quests.add(quest_id)
        return True, f"Quest activated: {quest.name}"
    
    # Update the complete_quest method in the QuestManager class
    def complete_quest(self, quest_id):
        """
        Complete a quest and give rewards
        
        Args:
            quest_id (str): ID of the quest to complete
            
        Returns:
            tuple: (success, message)
        """
        quest = self.get_quest(quest_id)
        if not quest:
            return False, f"Quest '{quest_id}' not found."
            
        if not quest.active:
            return False, f"Quest '{quest.name}' is not active."
            
        if not quest.completed:
            return False, f"Quest '{quest.name}' is not completed yet."
            
        # Remove from active quests
        if quest_id in self.active_quests:
            self.active_quests.remove(quest_id)
            
        # Add to completed quests
        self.completed_quests.add(quest_id)
        
        # Give rewards
        reward_text = []
        
        if "xp" in quest.rewards and quest.rewards["xp"] > 0:
            xp = quest.rewards["xp"]
            leveled_up = self.game_state.player.gain_experience(xp)
            reward_text.append(f"{xp} XP")
            
            if leveled_up:
                reward_text.append(f"Level up! You are now level {self.game_state.player.level}!")
                
        if "coins" in quest.rewards and quest.rewards["coins"] > 0:
            coins = quest.rewards["coins"]
            self.game_state.coins += coins
            reward_text.append(f"{coins} coins")
            
            # Update journal for coins earned
            self.game_state.journal.update_stats("coins_earned", coins)
            
        if "items" in quest.rewards:
            for item_name, quantity in quest.rewards["items"].items():
                for _ in range(quantity):
                    self.game_state.player.add_to_inventory(item_name)
                
                from items.item_factory import ItemFactory
                item = ItemFactory.get_item(item_name)
                if item:
                    if quantity > 1:
                        reward_text.append(f"{quantity}x {item.display_name()}")
                    else:
                        reward_text.append(item.display_name())
                
                # Update journal for reward items
                self.game_state.journal.update_stats("items_collected", quantity, item_name)
        
        # Update journal for quest completion
        self.game_state.journal.update_stats("quests_completed", 1)
        self.game_state.journal.add_entry(f"Completed quest: {quest.name}", "achievement")
        
        # Check for quest-based achievements
        if len(self.completed_quests) >= 5:
            self.game_state.journal.add_achievement(
                "Quest Master", 
                "Completed at least 5 quests in your adventure."
            )
        
        # Format the reward message
        if reward_text:
            rewards = ", ".join(reward_text)
            return True, f"Quest '{quest.name}' completed! Rewards: {rewards}"
        else:
            return True, f"Quest '{quest.name}' completed!"
        
    def update_quest_progress(self, event_type, target, location=None, count=1):
        """
        Update progress on active quests based on player actions
        
        Args:
            event_type (str): Type of event (collect, kill, visit, talk)
            target (str): Target of the event (item name, enemy type, location)
            location (str, optional): Location where event happened
            count (int): Number to increment (default 1)
            
        Returns:
            list: List of quests that were updated
        """
        updated_quests = []
        
        for quest_id in self.active_quests:
            quest = self.get_quest(quest_id)
            if not quest:
                continue
                
            if quest.update_progress(event_type, target, location, count):
                updated_quests.append(quest)
                
                # If quest was completed, notify the player
                if quest.completed:
                    self.game_state.add_to_history(f"Quest '{quest.name}' is ready to turn in!", (255, 220, 0))
        
        return updated_quests
    
    def get_available_quests(self):
        """Get quests that can be started but haven't been yet"""
        available = []
        
        for quest_id, quest in self.quests.items():
            if not quest.active and not quest.completed and quest.can_activate(self.completed_quests):
                available.append(quest_id)
                
        return available
    
    def get_active_quests(self):
        """Get currently active quests"""
        return [self.get_quest(quest_id) for quest_id in self.active_quests if self.get_quest(quest_id)]
    
    def get_completed_quests(self):
        """Get completed quests"""
        return [self.get_quest(quest_id) for quest_id in self.completed_quests if self.get_quest(quest_id)]

    def get_quests_for_location(self, location):
        """
        Get quests that are relevant to a specific location
        This could be used for location-specific quest givers in the future
        
        Args:
            location (str): The room name to check
            
        Returns:
            list: List of quests that can be obtained in this location
        """
        # For now, only return available quests if we're at the town square (notice board)
        if location == "town_square":
            return self.get_available_quests()
        return []

# shop.py
import random
from items.item_factory import ItemFactory

# Colors for text
TEXT_COLOR = (200, 200, 200)
TITLE_COLOR = (255, 255, 100)
COMBAT_COLOR = (255, 165, 0)
HEALTH_COLOR = (100, 255, 100)

class ShopSystem:
    def __init__(self):
        # Shop dialogues
        self.shop_dialogues = [
            "The dwarf nods at you. 'See anything you like?'",
            "'Best prices in the dungeon, that's my guarantee!'",
            "'Need something to fight off those monsters? I've got just the thing.'",
            "'That armor you're looking at? Made it myself. Quality craftsmanship!'",
            "'I also buy adventurer's gear, if you've got extras to sell.'",
            "'Be careful in those caves. Not everyone comes back, y'know.'"
        ]
    
    def get_random_dialogue(self):
        """Return a random shop dialogue."""
        return random.choice(self.shop_dialogues)
    
    def process_buy(self, game_state, item_name):
        """Process a buy request with partial string matching."""
        # Convert to lowercase for case-insensitive matching
        item_text = item_name.lower()
        
        room = game_state.world.get_room(game_state.current_room)
        if not room or not room.get("is_shop", False):
            game_state.add_to_history("There's no shop here to buy from.")
            return
        
        # Check if item is in shop inventory using partial matching
        shop_inventory = room.get("shop_inventory", {})
        
        # Try to find the best matching item in the shop
        best_match = None
        best_score = float('inf')  # Lower is better
        
        for shop_item in shop_inventory:
            # Get the item object if possible
            item_obj = ItemFactory.get_item(shop_item)
            
            # Check exact match on name
            if shop_item.replace('_', ' ') == item_text:
                best_match = shop_item
                break
                
            # Check partial match on name
            if item_text in shop_item.replace('_', ' '):
                score = len(shop_item) - len(item_text)
                if score < best_score:
                    best_match = shop_item
                    best_score = score
                    
            # If we have an item object, check aliases
            if item_obj:
                # Check exact matches on aliases
                if any(alias.lower() == item_text for alias in item_obj.aliases):
                    best_match = shop_item
                    break
                    
                # Check partial matches on aliases
                for alias in item_obj.aliases:
                    if item_text in alias.lower():
                        score = len(alias) - len(item_text)
                        if score < best_score:
                            best_match = shop_item
                            best_score = score
        
        # If no match found
        if not best_match:
            game_state.add_to_history(f"The shop doesn't sell any '{item_text}'.")
            return
            
        # Get the item details
        item_price = shop_inventory[best_match]["price"]
        
        # Check if player has enough coins
        if game_state.coins < item_price:
            game_state.add_to_history(f"You don't have enough coins. {best_match.replace('_', ' ')} costs {item_price} coins, but you only have {game_state.coins}.")
            return
        
        # Purchase the item
        game_state.coins -= item_price
        game_state.player.add_to_inventory(best_match)
        
        # Get the item object for better display
        item_obj = ItemFactory.get_item(best_match)
        if item_obj:
            game_state.add_to_history(f"You purchased {item_obj.display_name()} for {item_price} coins. You have {game_state.coins} coins left.")
        else:
            game_state.add_to_history(f"You purchased {best_match.replace('_', ' ')} for {item_price} coins. You have {game_state.coins} coins left.")
        
        # If it's a healing potion, let them know they can use it
        if best_match == "healing_potion":
            game_state.add_to_history("Use 'use healing potion' when you need to heal.")

    def process_sell(self, game_state, item_name):
        """Process a sell request with partial string matching."""
        # Convert to lowercase for case-insensitive matching
        item_text = item_name.lower()
        
        room = game_state.world.get_room(game_state.current_room)
        if not room or not room.get("is_shop", False):
            game_state.add_to_history("There's no shop here to sell to.")
            return
        
        # Search through player's inventory for closest match
        best_match = None
        best_score = float('inf')  # Lower is better
        
        for inv_item in game_state.player.inventory:
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
        
        # Check if player has the item
        if not actual_item_name or not game_state.player.has_item(actual_item_name):
            game_state.add_to_history(f"You don't have a {item_text} to sell.")
            return
        
        # Get the item object
        item = ItemFactory.get_item(actual_item_name)
        if not item:
            game_state.add_to_history(f"You can't sell the {item_text}.")
            return
        
        # Check if the item can be sold
        if not item.can_sell():
            game_state.add_to_history(f"The shopkeeper examines your {item.display_name()}.")
            game_state.add_to_history("'I can't buy that from you. Feel free to use it yourself.'")
            return
        
        # Get the sell price
        sell_price = item.get_sell_price()
            
        # Remove from inventory and add coins
        game_state.player.remove_from_inventory(actual_item_name)
        game_state.coins += sell_price
        
        game_state.add_to_history(f"You sold {item.display_name()} for {sell_price} coins. You now have {game_state.coins} coins.")
    
    def display_shop(self, game_state):
        """Display basic shop info without listing items."""
        room = game_state.world.get_room(game_state.current_room)
        
        # Add a shopkeeper dialogue
        if self.shop_dialogues:
            game_state.add_to_history(self.get_random_dialogue())
        
        game_state.add_to_history("You're in a shop. The shopkeeper watches you expectantly.", TITLE_COLOR)
        game_state.add_to_history(f"You have {game_state.coins} coins.")
        game_state.add_to_history("Type 'list' to see available items, 'buy [item]' to purchase, or 'sell [item]' to sell.")

    def display_shop_inventory(self, game_state):
        """Display the shop inventory as a separate command."""
        room = game_state.world.get_room(game_state.current_room)
        
        if not room or not room.get("is_shop", False):
            game_state.add_to_history("There's no shop here.")
            return
        
        game_state.add_to_history("Shop Inventory:", TITLE_COLOR)
        shop_inventory = room.get("shop_inventory", {})
        
        # Sort items by type and price for a more organized display
        weapons = []
        armors = []
        consumables = []
        other_items = []
        
        for item_name, details in shop_inventory.items():
            item_obj = ItemFactory.get_item(item_name)
            price = details["price"]
            
            if not item_obj:
                other_items.append((item_name.replace('_', ' '), price))
                continue
                
            if item_obj.type == "weapon":
                weapons.append((item_obj.display_name(), price, f"+{item_obj.attack_bonus} ATK"))
            elif item_obj.type == "armor":
                armors.append((item_obj.display_name(), price, f"+{item_obj.defense_bonus} DEF"))
            elif item_obj.type == "consumable" or item_obj.type in ["food", "drink"]:
                effect = ""
                if hasattr(item_obj, "health_restore") and item_obj.health_restore > 0:
                    effect = f"+{item_obj.health_restore} HP"
                consumables.append((item_obj.display_name(), price, effect))
            else:
                other_items.append((item_obj.display_name(), price))
        
        # Display weapons
        if weapons:
            game_state.add_to_history("Weapons:", COMBAT_COLOR)
            for name, price, bonus in weapons:
                game_state.add_to_history(f"  {name} ({bonus}) - {price} coins")
        
        # Display armors
        if armors:
            game_state.add_to_history("Armor:", COMBAT_COLOR)
            for name, price, bonus in armors:
                game_state.add_to_history(f"  {name} ({bonus}) - {price} coins")
        
        # Display consumables
        if consumables:
            game_state.add_to_history("Consumables:", HEALTH_COLOR)
            for name, price, effect in consumables:
                if effect:
                    game_state.add_to_history(f"  {name} ({effect}) - {price} coins")
                else:
                    game_state.add_to_history(f"  {name} - {price} coins")
        
        # Display other items
        if other_items:
            game_state.add_to_history("Other Items:", TEXT_COLOR)
            for name, price in other_items:
                game_state.add_to_history(f"  {name} - {price} coins")
        
        game_state.add_to_history(f"Your coins: {game_state.coins}")

# environment.py
import random
import time

class EnvironmentSystem:
    def __init__(self):
        # Weather types and their effects
        self.weather_types = {
            "clear": {
                "description": "The air is clear and still.",
                "messages": [
                    "Rays of light filter through cracks in the ceiling.",
                    "The air is surprisingly fresh here.",
                    "It's quiet and peaceful."
                ],
                "effects": {}  # No special effects
            },
            "misty": {
                "description": "A thick mist hangs in the air, limiting visibility.",
                "messages": [
                    "Wisps of fog curl around your ankles.",
                    "The mist makes it difficult to see far ahead.",
                    "Ghostly shapes seem to form and dissipate in the fog."
                ],
                "effects": {"enemy_accuracy": -2}  # Enemies have harder time hitting player
            },
            "humid": {
                "description": "The air is damp and humid, making movement sluggish.",
                "messages": [
                    "Droplets of water collect on the walls.",
                    "Your clothes cling uncomfortably to your skin.",
                    "The humid air feels heavy in your lungs."
                ],
                "effects": {"player_attack": -1}  # Player attacks less effectively
            },
            "stormy": {
                "description": "Distant rumblings and occasional tremors shake the cave.",
                "messages": [
                    "A tremor causes small rocks to fall from the ceiling.",
                    "The ground beneath your feet vibrates slightly.",
                    "A crash of thunder reverberates through the cavern."
                ],
                "effects": {"enemy_spawn_rate": 1.5}  # More enemies spawn
            },
            "magical": {
                "description": "The air shimmers with magical energy.",
                "messages": [
                    "Tiny motes of light dance in the air around you.",
                    "You feel a tingling sensation on your skin.",
                    "Your wounds seem to heal slightly faster here."
                ],
                "effects": {"healing_bonus": 1.2}  # Healing items more effective
            }
        }
        
        # Environment states for different room types - just some sensible defaults
        self.environment_states = {
            "entrance": ["clear", "misty", "stormy"],
            "cavern": ["clear", "misty", "humid", "stormy", "magical"],
            "passage": ["clear", "misty", "humid"],
            "lake": ["misty", "humid", "magical"],
            "treasure": ["clear", "magical"],
            "den": ["humid", "stormy"],
            "grotto": ["misty", "magical"],
            "shop": ["clear"]
        }
        
        # Default environment for rooms not specifically defined
        self.default_environments = ["clear", "misty"]
        
        # Track current weather in rooms
        self.current_weather = {}
        
        # Time tracking
        self.last_weather_change = time.time()
        self.weather_duration = 300  # 5 minutes before weather can change
    
    def _get_possible_weathers_for_room(self, room_name):
        """Get possible weather types for a room based on its name"""
        # Try to match room name to a known type
        for room_type, weather_list in self.environment_states.items():
            if room_type in room_name:
                return weather_list
        return self.default_environments
    
    def set_weather(self, room_name, weather_type):
        """Manually set weather for a room"""
        if weather_type in self.weather_types:
            self.current_weather[room_name] = weather_type
            return True
        return False
    
    def get_weather(self, room_name):
        """Get current weather for a room"""
        return self.current_weather.get(room_name, "clear")
    
    def set_random_weather(self, room_name, weather_bias=None):
        """Set random weather for a room with optional bias"""
        possible_weathers = self._get_possible_weathers_for_room(room_name)
        
        # Apply bias if provided
        if weather_bias:
            # Create a weighted list based on bias
            weighted_weathers = []
            for weather in possible_weathers:
                weight = weather_bias.get(weather, 1.0)
                # Convert to integer frequency
                for _ in range(int(weight * 10)):
                    weighted_weathers.append(weather)
            
            if weighted_weathers:
                self.current_weather[room_name] = random.choice(weighted_weathers)
                return self.current_weather[room_name]
        
        # No bias or empty weighted list, use simple random choice
        self.current_weather[room_name] = random.choice(possible_weathers)
        return self.current_weather[room_name]
    
    def initialize_weather(self, region):
        """Initialize weather for all rooms in a region"""
        weather_bias = region.get_environment_bias()
        for room_name in region.get_all_room_names():
            self.set_random_weather(room_name, weather_bias)
    
    def update(self, game_state):
        """Update weather for the current room"""
        current_time = time.time()
        current_room = game_state.current_room
        
        # Check if enough time has passed since last weather change
        if current_time - self.last_weather_change > self.weather_duration:
            # 25% chance to change weather
            if random.random() < 0.25:
                # Get the region for bias information
                region = game_state.world.get_region_for_room(current_room)
                weather_bias = region.get_environment_bias() if region else None
                
                old_weather = self.get_weather(current_room)
                self.set_random_weather(current_room, weather_bias)
                new_weather = self.get_weather(current_room)
                
                # Only notify if weather actually changed
                if old_weather != new_weather:
                    self._describe_weather_change(game_state, old_weather, new_weather)
                    
            self.last_weather_change = current_time
    
    def _describe_weather_change(self, game_state, old_weather, new_weather):
        """Describe the change in weather to the player"""
        new_weather_data = self.weather_types.get(new_weather, self.weather_types["clear"])
        game_state.add_to_history("\nThe environment changes...", (100, 200, 255))
        game_state.add_to_history(new_weather_data["description"], (100, 200, 255))
    
    def get_weather_description(self, room_name):
        """Get a description of the current weather in a room"""
        weather = self.get_weather(room_name)
        return self.weather_types[weather]["description"]
    
    def get_effects(self, room_name):
        """Get current weather effects for a room"""
        weather = self.get_weather(room_name)
        return self.weather_types[weather]["effects"]
    
    def get_random_ambient_message(self, game_state):
        """Get a random ambient message based on current weather"""
        room_name = game_state.current_room
        weather = self.get_weather(room_name)
        
        if random.random() < 0.001:
            messages = self.weather_types[weather]["messages"]
            return random.choice(messages)
        
        return None

# region.py
import random
import time
from world.environment import EnvironmentSystem

class Region:
    """
    A region that contains rooms and manages region-specific systems
    """
    def __init__(self, name, display_name, description, region_type="wilderness", difficulty=1):
        self.name = name  # Internal name (snake_case)
        self.display_name = display_name  # Human-readable name
        self.description = description
        self.region_type = region_type
        self.difficulty = difficulty
        self.rooms = {}  # {room_name: room_data}
        
        # Region-specific systems
        self.environment_system = EnvironmentSystem()
        
        # Region state
        self.discovered = False
        self.danger_level = difficulty  # Can fluctuate
        self.enemy_density = self._calculate_base_enemy_density()
        
        # Environment bias for this region
        self.environment_bias = {}
        
        # Time tracking
        self.last_update_time = time.time()
    
    def _calculate_base_enemy_density(self):
        """Calculate the base enemy density for a region based on its properties"""
        base_density = 1.0
        
        if self.region_type == "monster_lair":
            base_density = 1.5
        elif self.region_type == "settlement":
            base_density = 0.2
        elif self.region_type == "dungeon":
            base_density = 1.0
            
        # Adjust based on difficulty
        density = base_density * (1 + (self.difficulty * 0.2))
        
        return density
    
    def add_room(self, room_name, room_data):
        """Add a room to this region"""
        self.rooms[room_name] = room_data
        room_data["region"] = self.name
        return room_data
    
    def get_room(self, room_name):
        """Get a room in this region by name"""
        return self.rooms.get(room_name)
    
    def get_all_room_names(self):
        """Get names of all rooms in this region"""
        return list(self.rooms.keys())
    
    def set_environment_bias(self, weather_type, bias_factor):
        """Set an environment bias for this region"""
        self.environment_bias[weather_type] = bias_factor
    
    def get_environment_bias(self):
        """Get the environment bias dictionary for this region"""
        return self.environment_bias
    
    def update(self, game_state):
        """Update region state"""
        current_time = time.time()
        
        # Only update periodically
        if current_time - self.last_update_time < 60:  # Update every minute
            return
            
        # Random fluctuations in danger level
        if random.random() < 0.05:  # 5% chance
            base_difficulty = self.difficulty
            
            # Decide whether to increase or decrease
            if self.danger_level > base_difficulty and random.random() < 0.7:
                # More likely to return to base level if currently higher
                self.danger_level = max(base_difficulty, self.danger_level - 0.5)
            elif self.danger_level < base_difficulty and random.random() < 0.7:
                # More likely to return to base level if currently lower
                self.danger_level = min(base_difficulty, self.danger_level + 0.5)
            elif random.random() < 0.5:
                # Otherwise random change
                change = 0.5 if random.random() < 0.5 else -0.5
                self.danger_level = max(0, self.danger_level + change)
        
        # Update environment system
        if random.random() < 0.2:  # 20% chance to update environment
            self.environment_system.update(game_state)
        
        self.last_update_time = current_time
    
    def discover(self):
        """Mark this region as discovered"""
        if not self.discovered:
            self.discovered = True
            return True
        return False
    
    def get_summary(self):
        """Get a text summary of this region"""
        summary = []
        summary.append(f"Region: {self.display_name}")
        summary.append(f"Type: {self.region_type.replace('_', ' ').title()}")
        summary.append(f"Description: {self.description}")
        
        # Difficulty rating as stars
        difficulty_stars = "★" * int(self.difficulty) if self.difficulty > 0 else "None"
        summary.append(f"Difficulty: {difficulty_stars}")
        
        # Danger level might be different from base difficulty
        if self.danger_level > self.difficulty + 0.2:
            summary.append(f"Current Danger: Elevated")
        elif self.danger_level < self.difficulty - 0.2:
            summary.append(f"Current Danger: Reduced")
        else:
            summary.append(f"Current Danger: Normal")
        
        return summary

# world.py
import random
from world.region import Region

class GameWorld:
    def __init__(self):
        self.regions = {}  # {region_name: Region object}
        
        # Initialize regions and rooms
        self._initialize_regions()
        self._initialize_rooms()
        self._add_region_biases()
        
        # Default starting room
        self.starting_room = "entrance"
    
    def _initialize_regions(self):
        """Initialize the regions in the world"""
        # Cave System Region
        self.regions["cave_system"] = Region(
            name="cave_system",
            display_name="Shadowed Depths",
            description="A network of natural caverns that extends deep into the mountain.",
            region_type="dungeon",
            difficulty=1
        )
        
        # Goblin Territory Region
        self.regions["goblin_territory"] = Region(
            name="goblin_territory",
            display_name="Goblin Territory",
            description="An area claimed by goblins, marked with crude symbols and primitive structures.",
            region_type="monster_lair",
            difficulty=2
        )
        
        # Town Region
        self.regions["town"] = Region(
            name="town",
            display_name="Adventurer's Rest",
            description="A small outpost where adventurers gather to trade and rest.",
            region_type="settlement",
            difficulty=0
        )
    
    def _add_region_biases(self):
        """Add environmental biases to regions"""
        # Cave System biases
        cave_system = self.regions["cave_system"]
        cave_system.set_environment_bias("misty", 1.5)  # 50% more likely to be misty
        cave_system.set_environment_bias("humid", 1.2)  # 20% more likely to be humid
        
        # Goblin Territory biases
        goblin_territory = self.regions["goblin_territory"]
        goblin_territory.set_environment_bias("stormy", 1.3)  # 30% more likely to be stormy
        
        # Town biases
        town = self.regions["town"]
        town.set_environment_bias("clear", 2.0)  # Much more likely to be clear weather
    
    def _initialize_rooms(self):
        """Initialize the rooms in each region"""
        # Cave System Rooms
        cave_system = self.regions["cave_system"]
        
        cave_system.add_room("entrance", {
            "description": "You stand at the entrance to a dark cave. A cool breeze flows from the opening. There's a worn path leading north into darkness.",
            "exits": {"north": "cavern", "east": "shop"},
            "items": ["torch", "rusty_sword", "stick", "common_box_key"]  # Added common_box_key
        })
        
        cave_system.add_room("cavern", {
            "description": "A vast cavern stretches before you. Stalactites hang from the ceiling, dripping water. The air is damp and cold.",
            "exits": {"south": "entrance", "east": "narrow_passage", "west": "underground_lake", "north": "goblin_den"},
            "items": ["coin", "leather_armor", "common_treasure_box"]  # Added common_treasure_box
        })
        
        cave_system.add_room("narrow_passage", {
            "description": "A narrow passage winds through the rock. The walls are smooth, as if worn by water over centuries. There's a small alcove in the wall.",
            "exits": {"west": "cavern", "north": "treasure_room"},
            "items": ["ancient_key", "healing_potion"]
        })
        
        cave_system.add_room("underground_lake", {
            "description": "A vast underground lake spreads before you. The water is perfectly still, reflecting the stalactites above like a mirror.",
            "exits": {"east": "cavern", "north": "hidden_grotto"},
            "items": ["boat", "uncommon_treasure_box"]  # Added uncommon_treasure_box
        })
        
        cave_system.add_room("hidden_grotto", {
            "description": "A serene grotto hidden behind a waterfall. Crystal formations cast rainbows across the walls when your light hits them.",
            "exits": {"south": "underground_lake"},
            "items": ["chainmail", "healing_potion", "sapphire", "cloth", "uncommon_box_key"]  # Added uncommon_box_key
        })
        
        # Goblin Territory Rooms
        goblin_territory = self.regions["goblin_territory"]
        
        goblin_territory.add_room("goblin_den", {
            "description": "A foul-smelling chamber littered with bones and crude weapons. This appears to be where the goblins make their home.",
            "exits": {"south": "cavern"},
            "items": ["steel_sword", "healing_potion", "bread", "rare_box_key"]  # Added rare_box_key
        })
        
        goblin_territory.add_room("treasure_room", {
            "description": "A small chamber filled with the remnants of an ancient civilization. Gold coins are scattered about, and gems glitter in the light.",
            "exits": {"south": "narrow_passage"},
            "items": ["gem", "ruby", "emerald", "golden_crown", "ancient_scroll", "ancient_blade", "rare_treasure_box"],  # Added rare_treasure_box
            "locked": True,
            "key_item": "ancient_key"
        })
        
        # Town Rooms
        town = self.regions["town"]
        
        town.add_room("shop", {
            "description": "A small, dimly lit shop built into the rock face. Shelves line the walls, filled with various supplies and equipment. A weathered dwarf stands behind a stone counter.",
            "exits": {"west": "entrance", "south": "tavern"},
            "items": [],
            "is_shop": True,
            "shop_inventory": {
                "healing_potion": {"price": 5, "description": "Restores 20 health points."},
                "strong_healing_potion": {"price": 15, "description": "Restores 50 health points."},
                "leather_armor": {"price": 15, "description": "Provides +3 defense."},
                "chainmail": {"price": 30, "description": "Provides +6 defense."},
                "steel_sword": {"price": 25, "description": "Provides +10 attack."},
                "ancient_blade": {"price": 50, "description": "Provides +15 attack."},
                "plate_armor": {"price": 45, "description": "Provides +10 defense."},
                "stamina_potion": {"price": 10, "description": "Temporarily increases attack power."},
                "pickaxe": {"price": 8, "description": "A tool for mining gems."},
                "stick": {"price": 1, "description": "A simple wooden stick."},
                "cloth": {"price": 1, "description": "A piece of cloth."},
                "common_box_key": {"price": 8, "description": "A simple key that opens common treasure boxes."},
                "uncommon_box_key": {"price": 20, "description": "A bronze key that opens uncommon treasure boxes."}
            }
        })

        # Inn/Tavern - a place to rest and gather information
        town.add_room("tavern", {
            "description": "The Rusty Pickaxe tavern is warm and inviting. A crackling fireplace illuminates the room, and the air is filled with the smell of hearty stew. Several patrons chat quietly at wooden tables, while a cheerful bartender serves drinks behind a polished counter.",
            "exits": {"north": "shop", "south": "town_square"},
            "items": ["bread", "cooked_meat", "apple"],
            "is_inn": True,  # Flag for the inn functionality
            "inn_cost": 5,  # Cost to rest in coins
            "inn_dialogue": [
                "The innkeeper smiles warmly. 'Need a room for the night? Only 5 coins.'",
                "'Our stew is the best in the caves! Made it myself.'",
                "'Heard some adventurers talking about a hidden grotto filled with crystals.'",
                "'Watch yourself in the goblin territory. Those little pests have been more aggressive lately.'",
                "'Rumor has it there's an ancient treasure somewhere in these caves.'"
            ]
        })

        # Town Square - central hub connecting other parts of town
        town.add_room("town_square", {
            "description": "The town square is a small open area carved from the cavern itself. Glowing crystals embedded in the ceiling provide natural light. A notice board stands in the center, covered with various announcements and job postings. Several paths lead to different parts of town.",
            "exits": {"north": "tavern", "west": "blacksmith", "south": "chapel", "east": "alchemist"},
            "items": ["torch"],
            "is_notice_board": True,  # Flag for the notice board functionality
            "notices": [
                "REWARD: 50 coins for clearing goblin den. See the captain for details.",
                "LOST: Ruby pendant near underground lake. Reward if found.",
                "CAUTION: Strange magical disturbances reported in the hidden grotto.",
                "WANTED: Mining tools in good condition. Will pay fair price.",
                "ANNOUNCEMENT: Weekly meeting at the chapel tomorrow evening."
            ]
        })

        # Blacksmith - for weapon and armor repairs or upgrades
        town.add_room("blacksmith", {
            "description": "The blacksmith's forge glows with intense heat. A burly dwarf hammers rhythmically at a piece of red-hot metal, sending sparks flying with each strike. Weapons and armor of various designs hang from the walls, and a large anvil dominates the center of the room.",
            "exits": {"east": "town_square"},
            "items": ["pickaxe"],
            "is_shop": True,
            "is_repair": True,  # Flag for repair functionality
            "repair_cost_multiplier": 0.3,  # 30% of item value to repair
            "shop_inventory": {
                "steel_sword": {"price": 22, "description": "A well-crafted steel sword, sharp and reliable."},
                "chainmail": {"price": 28, "description": "A shirt of interlocking metal rings providing good protection."},
                "plate_armor": {"price": 40, "description": "Heavy plate armor offering superior protection."},
                "pickaxe": {"price": 7, "description": "A sturdy pickaxe for mining."}
            },
            "smith_dialogue": [
                "The blacksmith looks up from his work. 'Need something forged or repaired?'",
                "'Quality metal is hard to come by these days.'",
                "'That armor you're wearing could use some work. I can fix it up for you.'",
                "'Careful with that blade. Even the finest steel can break if mistreated.'",
                "'Found some interesting ore near the hidden grotto. Makes for excellent weapons.'"
            ]
        })

        # Chapel - for healing and blessings
        town.add_room("chapel", {
            "description": "A small, peaceful chapel carved into the cave wall. Candles cast a gentle glow across stone pews and a simple altar. The ceiling has been shaped to create natural acoustics, and soft chanting echoes softly through the chamber. A serene aura permeates the air.",
            "exits": {"north": "town_square"},
            "items": ["healing_potion"],
            "is_chapel": True,  # Flag for chapel functionality
            "blessing_cost": 10,  # Cost for blessing in coins
            "healing_cost": 15,  # Cost for full healing in coins
            "cleric_dialogue": [
                "The cleric looks up from his prayer book. 'Welcome, traveler. Seeking healing or blessing?'",
                "'The light guides us even in the darkest caves.'",
                "'I sense you've faced many challenges. Rest here awhile.'",
                "'Beware the deeper caverns. Strange energies flow there.'",
                "'Even the goblin folk have souls, though they've strayed from the light.'"
            ]
        })

        # Alchemist - for potions and special items
        town.add_room("alchemist", {
            "description": "The alchemist's shop is filled with bubbling concoctions and strange aromas. Colorful bottles line the shelves, and dried herbs hang from the ceiling. A slender elf carefully measures ingredients at a workbench covered with arcane tools and mysterious substances.",
            "exits": {"west": "town_square", "north": "garden"},
            "items": [],
            "is_shop": True,
            "shop_inventory": {
                "healing_potion": {"price": 5, "description": "A red potion that restores health."},
                "strong_healing_potion": {"price": 12, "description": "A vibrant red potion that restores significant health."},
                "stamina_potion": {"price": 8, "description": "A green potion that temporarily increases attack power."},
                "antidote": {"price": 7, "description": "A blue potion that cures poison and disease."},
                "elixir_of_clarity": {"price": 15, "description": "A purple potion that enhances perception and reflexes."}
            },
            "alchemist_dialogue": [
                "The alchemist looks up from her work. 'Ah, a customer! Interested in my potions?'",
                "'Each potion is crafted with utmost care and the finest ingredients.'",
                "'That mushroom you passed by might be more valuable than you think.'",
                "'I'm working on a new formula. Just need a few rare ingredients from the deeper caves.'",
                "'Careful with mixing potions. The results can be... unpredictable.'"
            ]
        })

        # Herb Garden - for ingredient gathering
        town.add_room("garden", {
            "description": "A surprisingly lush garden thrives in this cavern, nurtured by glowing crystals that provide plant-sustaining light. Neat rows of herbs, mushrooms, and cave-adapted plants grow in carefully tended beds. A small pond in the corner hosts unusual luminescent water plants.",
            "exits": {"south": "alchemist"},
            "items": ["herb_bundle", "glowing_mushroom", "waterbloom"],
            "is_garden": True,  # Flag for garden functionality
            "regrowth_time": 300,  # Time in seconds for plants to regrow
            "gardener_dialogue": [
                "The old gardener nods at you. 'Feel free to gather what you need, but please be respectful of the plants.'",
                "'These mushrooms only grow in the darkest parts of the cavern.'",
                "'The luminescent properties of these plants have remarkable healing capabilities.'",
                "'I've been experimenting with crossing surface plants with cave species. Fascinating results.'",
                "'If you find any unusual seeds in your travels, bring them to me. I'll make it worth your while.'"
            ]
        })

        
        # Add random coins to rooms
        for region_name, region in self.regions.items():
            for room_name, room_data in region.rooms.items():
                if "is_shop" not in room_data and random.random() < 0.7:  # 70% chance
                    if "items" in room_data:
                        # Add 1-3 coins
                        coin_count = random.randint(1, 3)
                        for _ in range(coin_count):
                            room_data["items"].append("coin")
    
    def get_room(self, room_name):
        """Get a room from any region by name"""
        for region in self.regions.values():
            room = region.get_room(room_name)
            if room:
                return room
        return None
    
    def get_region_for_room(self, room_name):
        """Get the region that contains a specific room"""
        for region_name, region in self.regions.items():
            if room_name in region.rooms:
                return region
        return None
    
    def get_region(self, region_name):
        """Get a region by name"""
        return self.regions.get(region_name)
    
    def get_all_regions(self):
        """Get all regions in the world"""
        return list(self.regions.values())
    
    def get_all_room_names(self):
        """Get names of all rooms in the world"""
        all_rooms = []
        for region in self.regions.values():
            all_rooms.extend(region.get_all_room_names())
        return all_rooms
    
    def update_regions(self, game_state):
        """Update all regions"""
        for region in self.regions.values():
            region.update(game_state)

