# Modified game_loop.py with intro screen and game over handling
import pygame
import sys
import time
import os
from config.config import GameConfig
from core.save_load import save_game, load_game
from config.autosave import AutosaveSettings
from core.utils import get_timestamp, ensure_dir_exists, format_time_delta
from intro_screen import IntroScreen, show_game_over_screen

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
        # Show the intro screen first
        intro_screen = IntroScreen(self.screen, self)
        action, save_file = intro_screen.show()
        
        # Handle intro screen results
        if action == "quit":
            pygame.quit()
            sys.exit()
        elif action == "load" and save_file:
            # Load the selected save
            success, message = load_game(self.game_state, save_file)
            if not success:
                self.game_state.add_to_history(message)
        elif action == "new":
            # Start a new game - look at the initial room
            self.game_state.look()
        
        # Main game loop
        while True:
            current_time = time.time()
            self.screen.fill(GameConfig.BG_COLOR)
            
            # Update enemies periodically
            self.update_enemies()

            # Update regions
            self.world.update_regions(self.game_state)

            self.game_state.status_effect_manager.update()
            
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
            
            # Handle game over state
            if self.game_state.game_over:
                # Show game over screen
                game_over_reason = "You have been defeated!"
                for line, _ in reversed(self.game_state.game_history):
                    if "defeated" in line:
                        game_over_reason = line
                        break
                
                # Wait a moment to show the death message
                pygame.time.wait(1500)
                
                # Show game over screen
                action = show_game_over_screen(self.screen, game_over_reason)
                
                if action == "menu":
                    # Return to main menu
                    return self.restart_game()
                else:
                    # Quit game
                    pygame.quit()
                    sys.exit()
    
    def restart_game(self):
        """Restart the game by returning to the main menu"""
        # We'll just return from the run method, which will result in a new game if called from main.py
        # The game initialization in main.py will create a new game state
        return
    
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
            
            # Display health and level with expanded info
            health_text = f"HP: {self.game_state.player.health}/{self.game_state.player.max_health}"
            health_surface = self.font.render(health_text, True, GameConfig.HEALTH_COLOR)
            
            # Add XP progress info
            xp_text = f"LVL: {self.game_state.player.level} | XP: {self.game_state.player.experience}/{self.game_state.player.exp_to_next_level}"
            xp_surface = self.font.render(xp_text, True, (180, 180, 255))  # Light blue for XP
            
            # Position the health and XP text at the right side
            self.screen.blit(health_surface, (GameConfig.SCREEN_WIDTH - GameConfig.MARGIN - health_surface.get_width(), 
                            GameConfig.SCREEN_HEIGHT - GameConfig.MARGIN - GameConfig.FONT_SIZE))
            self.screen.blit(xp_surface, (GameConfig.SCREEN_WIDTH - GameConfig.MARGIN - xp_surface.get_width(), 
                            GameConfig.SCREEN_HEIGHT - GameConfig.MARGIN - GameConfig.FONT_SIZE*2 - 2))
            
            # Display status effects as icons with remaining time
            status_text = ""
            if hasattr(self.game_state, 'status_effect_manager'):
                # Get only the status icons without detailed text for a cleaner display
                for effect_name, effect in self.game_state.status_effect_manager.active_effects.items():
                    seconds_left = int(effect.get_time_remaining())
                    if effect_name == "poison":
                        status_text += f"{effect.icon} Poisoned ({seconds_left}s) "
                    else:
                        status_text += f"{effect.icon} {effect.display_name} ({seconds_left}s) "
            
            if status_text:
                # Display status icons in a more visible position
                status_surface = self.font.render(status_text, True, (0, 180, 0))  # Green for poison
                self.screen.blit(status_surface, (GameConfig.MARGIN, 
                                GameConfig.SCREEN_HEIGHT - GameConfig.MARGIN - GameConfig.FONT_SIZE*2 - 2))
            
            # Display scroll indicator if scrolled up
            if self.scroll_offset > 0:
                scroll_text = f"[SCROLLED UP: PgUp/PgDn or Mouse Wheel to navigate]"
                scroll_surface = self.font.render(scroll_text, True, (150, 150, 150))
                self.screen.blit(scroll_surface, (GameConfig.MARGIN, GameConfig.SCREEN_HEIGHT - GameConfig.MARGIN - GameConfig.FONT_SIZE*3 - 5))