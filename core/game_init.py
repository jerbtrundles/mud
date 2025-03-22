# game_init.py
import pygame

from entities.player import Player
from core.game_state import GameState
from world.world import GameWorld
from entities.regional_enemy_manager import RegionalEnemyManager
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
    enemy_manager = RegionalEnemyManager(world)
    enemy_manager.set_game_state(game_state)
    game_state.set_enemy_manager(enemy_manager)
    
    return world, player, game_state, command_parser, enemy_manager