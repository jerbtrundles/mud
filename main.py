#!/usr/bin/env python3
# main.py - Main entry point for MiniMUD game

import sys
import traceback
import pygame

from core.game_init import initialize_game
from core.game_loop import GameLoop
from intro_screen import IntroScreen

def main():
    """Main entry point for the game"""
    try:
        # Initialize pygame
        pygame.init()
        
        # Create the main game screen
        from config.config import GameConfig
        screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        pygame.display.set_caption("MiniMUD - Text RPG Adventure")
        
        # Main game loop with restart capability
        running = True
        while running:
            # Initialize all game components
            world, player, game_state, command_parser, enemy_manager = initialize_game()
            
            # Create and run the game loop
            game_loop = GameLoop(game_state, command_parser, enemy_manager, world)
            
            # Run the game - when it returns, we'll restart from the main menu
            game_loop.run()
            
            # If we reach here, we've exited the game loop
            # If game_over is true but we're here, we want to restart
            # Otherwise, we want to quit
            if not game_state.game_over:
                running = False
        
    except Exception as e:
        # Handle unexpected errors gracefully
        print("An error occurred:")
        print(str(e))
        traceback.print_exc()
        return 1
    finally:
        # Clean up pygame
        pygame.quit()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())