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