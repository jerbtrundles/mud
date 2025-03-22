# intro_screen.py
import pygame
import sys
import os
from config.config import GameConfig

class IntroScreen:
    """Intro screen for MiniMUD with new game/load game options"""
    def __init__(self, screen, game_loop=None):
        self.screen = screen
        self.game_loop = game_loop
        self.clock = pygame.time.Clock()
        
        # Load fonts
        self.title_font = pygame.font.SysFont("Courier New", 36, bold=True)
        self.menu_font = pygame.font.SysFont("Courier New", 24)
        self.footer_font = pygame.font.SysFont("Courier New", 16, italic=True)
        
        # Menu options
        self.options = ["New Game", "Load Game", "Quit"]
        self.selected_option = 0
        
        # Save files (to be populated when shown)
        self.save_files = []
        self.save_selection_mode = False
        self.save_selected_index = 0
        self.save_scroll_offset = 0
        self.max_saves_shown = 8
        
        # Animation variables
        self.title_color = (255, 255, 100)  # Yellow
        self.option_color = (200, 200, 200)  # Light gray
        self.selected_color = (100, 255, 100)  # Green
        self.highlight_color = (255, 165, 0)  # Orange
        self.help_color = (100, 100, 255)  # Light blue
        
        # Text for footer
        self.footer_text = "Use ↑↓ keys to navigate, Enter to select"
        
    def show(self):
        """Display the intro screen and handle input"""
        self.running = True
        self.save_selection_mode = False
        
        # Use once variable to ensure certain operations run only once
        save_list_loaded = False
        
        while self.running:
            # Clear screen
            self.screen.fill(GameConfig.BG_COLOR)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                elif event.type == pygame.KEYDOWN:
                    if self.save_selection_mode:
                        self._handle_save_selection_input(event)
                    else:
                        self._handle_menu_input(event)
            
            # Draw the title
            self._draw_title()
            
            # Draw the main menu or save selection
            if self.save_selection_mode:
                # Load save list if not already loaded
                if not save_list_loaded:
                    self._load_save_list()
                    save_list_loaded = True
                    
                self._draw_save_selection()
            else:
                # Reset the flag when returning to main menu
                save_list_loaded = False
                self._draw_menu_options()
            
            # Draw footer help text
            self._draw_footer()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(30)
            
        # Return action and potentially selected save
        if hasattr(self, 'selected_action') and self.selected_action == "load" and hasattr(self, 'selected_save'):
            return self.selected_action, self.selected_save
        elif hasattr(self, 'selected_action'):
            return self.selected_action, None
        else:
            return "quit", None
    
    def _handle_menu_input(self, event):
        """Handle input for the main menu"""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif event.key == pygame.K_RETURN:
            selected = self.options[self.selected_option]
            
            if selected == "New Game":
                self.selected_action = "new"
                self.running = False
            elif selected == "Load Game":
                self.save_selection_mode = True
                self.save_selected_index = 0
                self.save_scroll_offset = 0
            elif selected == "Quit":
                self.selected_action = "quit"
                self.running = False
    
    def _handle_save_selection_input(self, event):
        """Handle input for the save file selection screen"""
        if event.key == pygame.K_ESCAPE:
            # Return to main menu
            self.save_selection_mode = False
            
        elif event.key == pygame.K_UP:
            if self.save_selected_index > 0:
                self.save_selected_index -= 1
                # Adjust scroll if needed
                if self.save_selected_index < self.save_scroll_offset:
                    self.save_scroll_offset = self.save_selected_index
                    
        elif event.key == pygame.K_DOWN:
            if self.save_selected_index < len(self.save_files) - 1:
                self.save_selected_index += 1
                # Adjust scroll if needed
                if self.save_selected_index >= self.save_scroll_offset + self.max_saves_shown:
                    self.save_scroll_offset = self.save_selected_index - self.max_saves_shown + 1
                    
        elif event.key == pygame.K_RETURN:
            if self.save_files:
                self.selected_action = "load"
                self.selected_save = self.save_files[self.save_selected_index]["filename"]
                self.running = False
    
    def _load_save_list(self):
        """Load the list of available save files"""
        from core.save_load import list_saves
        self.save_files = list_saves()
    
    def _draw_title(self):
        """Draw the game title at the top of the screen"""
        # Use the ASCII art title instead of text
        self._draw_ascii_title()

        title_surf = self.title_font.render("MiniMUD", True, self.title_color)
        title_x = (GameConfig.SCREEN_WIDTH - title_surf.get_width()) // 2
        self.screen.blit(title_surf, (title_x, 270))
        
        # Draw the subtitle
        subtitle_surf = self.menu_font.render("A Text RPG Adventure", True, self.title_color)
        subtitle_x = (GameConfig.SCREEN_WIDTH - subtitle_surf.get_width()) // 2
        self.screen.blit(subtitle_surf, (subtitle_x, 310))  # Adjusted Y position to appear below ASCII art
        
        # Decorative line under the title
        line_y = 350  # Adjusted Y position
        pygame.draw.line(
            self.screen,
            self.title_color,
            (GameConfig.MARGIN * 2, line_y),
            (GameConfig.SCREEN_WIDTH - GameConfig.MARGIN * 2, line_y),
            2
        )

    def _draw_menu_options(self):
        """Draw the main menu options"""
        start_y = 380  # Adjusted Y position to appear below title
        spacing = 40
        
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.option_color
            option_surf = self.menu_font.render(option, True, color)
            
            # Center the option
            option_x = (GameConfig.SCREEN_WIDTH - option_surf.get_width()) // 2
            option_y = start_y + (i * spacing)
            
            # Draw a selection indicator for the current option
            if i == self.selected_option:
                indicator = ">> "
                indicator_surf = self.menu_font.render(indicator, True, self.highlight_color)
                self.screen.blit(indicator_surf, (option_x - indicator_surf.get_width(), option_y))
                
                indicator = " <<"
                indicator_surf = self.menu_font.render(indicator, True, self.highlight_color)
                self.screen.blit(indicator_surf, (option_x + option_surf.get_width(), option_y))
            
            # Draw the option text
            self.screen.blit(option_surf, (option_x, option_y))
    
    def _draw_save_selection(self):
        """Draw the save file selection screen"""
        # Draw a simpler header for save selection
        title_surf = self.title_font.render("MiniMUD", True, self.title_color)
        title_x = (GameConfig.SCREEN_WIDTH - title_surf.get_width()) // 2
        self.screen.blit(title_surf, (title_x, 270))
        
        if not self.save_files:
            # No save files found
            text = "No save files found."
            text_surf = self.menu_font.render(text, True, self.option_color)
            text_x = (GameConfig.SCREEN_WIDTH - text_surf.get_width()) // 2
            self.screen.blit(text_surf, (text_x, 500))
            
            # Back instruction
            back_text = "Press ESC to return to main menu"
            back_surf = self.menu_font.render(back_text, True, self.help_color)
            back_x = (GameConfig.SCREEN_WIDTH - back_surf.get_width()) // 2
            self.screen.blit(back_surf, (back_x, 550))
            return
        
        # Draw header for save selection
        header = "Select a saved game to load:"
        header_surf = self.menu_font.render(header, True, self.highlight_color)
        header_x = (GameConfig.SCREEN_WIDTH - header_surf.get_width()) // 2
        self.screen.blit(header_surf, (header_x, 360))
        
        # Draw save files
        start_y = 390
        spacing = 35
        displayed_saves = 0
        
        # Calculate visible range
        visible_range = range(
            self.save_scroll_offset,
            min(self.save_scroll_offset + self.max_saves_shown, len(self.save_files))
        )
        
        for i in visible_range:
            save = self.save_files[i]
            
            # Format display text
            if len(save["filename"]) > 30:
                filename = save["filename"][:27] + "..."
            else:
                filename = save["filename"]
                
            save_text = f"{filename} - Level {save['level']} at {save['location']}"
            
            # Select color based on selection
            color = self.selected_color if i == self.save_selected_index else self.option_color
            
            # Render text
            save_surf = self.menu_font.render(save_text, True, color)
            save_x = (GameConfig.SCREEN_WIDTH - save_surf.get_width()) // 2
            save_y = start_y + (displayed_saves * spacing)
            
            # Draw selection indicator
            if i == self.save_selected_index:
                indicator = ">"
                indicator_surf = self.menu_font.render(indicator, True, self.highlight_color)
                self.screen.blit(indicator_surf, (save_x - indicator_surf.get_width() - 10, save_y))
            
            # Draw save info
            self.screen.blit(save_surf, (save_x, save_y))
            displayed_saves += 1
        
        # Draw scroll indicators if needed
        if self.save_scroll_offset > 0:
            up_indicator = "^ More saves above"
            up_surf = self.footer_font.render(up_indicator, True, self.help_color)
            up_x = (GameConfig.SCREEN_WIDTH - up_surf.get_width()) // 2
            self.screen.blit(up_surf, (up_x, start_y - 25))
            
        if self.save_scroll_offset + self.max_saves_shown < len(self.save_files):
            down_indicator = "v More saves below"
            down_surf = self.footer_font.render(down_indicator, True, self.help_color)
            down_x = (GameConfig.SCREEN_WIDTH - down_surf.get_width()) // 2
            self.screen.blit(down_surf, (down_x, start_y + (displayed_saves * spacing) + 5))
        
        # Back instruction
        back_text = "Press ESC to return to main menu"
        back_surf = self.footer_font.render(back_text, True, self.help_color)
        back_x = (GameConfig.SCREEN_WIDTH - back_surf.get_width()) // 2
        self.screen.blit(back_surf, (back_x, start_y + (displayed_saves * spacing) + 30))
    
    def _draw_footer(self):
        """Draw footer text with instructions"""
        footer_surf = self.footer_font.render(self.footer_text, True, self.help_color)
        footer_x = (GameConfig.SCREEN_WIDTH - footer_surf.get_width()) // 2
        footer_y = GameConfig.SCREEN_HEIGHT - GameConfig.MARGIN - GameConfig.FONT_SIZE - 10
        
        self.screen.blit(footer_surf, (footer_x, footer_y))

    def _draw_ascii_title(self):
        """Draw the ASCII art title on the screen"""
        from config.config import GameConfig
        
        # Split the ASCII art into lines
        lines = MINIMUD_ASCII_TITLE.split('\n')
        
        # Define colors for different parts of the artwork
        mountain_color = (150, 150, 255)  # Bluish for mountains
        town_color = (255, 220, 100)      # Yellow for town
        treasure_color = (255, 215, 0)     # Gold for treasure
        title_color = (255, 100, 100)     # Red for title
        
        # Starting Y position (adjust based on the size of your art)
        y_offset = 10
        
        # Calculate the width of a character in the current font
        char_width = self.title_font.size(' ')[0]
        
        # Center the ASCII art
        max_width = max(len(line) for line in lines)
        x_offset = (GameConfig.SCREEN_WIDTH - (max_width * char_width / 2.5)) // 2
        
        # Draw each line
        for i, line in enumerate(lines):
            # Skip empty lines at the beginning
            if not line and i < 2:
                continue
                
            # Determine line color based on content
            color = self.title_color  # Default
            
            # Check if this is a title line
            if "MINI" in line or "MUD" in line:
                color = title_color
            # Check for mountains
            elif "/\\" in line or "/  \\" in line:
                color = mountain_color
            # Check for town
            elif "TOWN" in line:
                color = town_color
            # Check for treasure
            elif "T R E A S U R E" in line:
                color = treasure_color
                
            # Render and blit the line
            text_surface = self.footer_font.render(line, True, color)
            self.screen.blit(text_surface, (x_offset, y_offset))
            y_offset += 10  # Line spacing for ASCII art

MINIMUD_ASCII_TITLE = r"""
  /\/\   /\   |\   |   /\   /\/\   |   |   |~\
 |    | |  |  | \  |  |  |  |    |  |   |   |  \
 |    | |__|  |  \ | |____|  |    |  |   |   |  /
  \__/  |  |  |   \| |    |   \__/    \_/    |_/

                /\     *
               /  \    |
   /\    /\   /    \   |
  /  \  /  \ /      \  | ADVENTURE
 /____\/____\________\_|

   _____      ______      ___       ____      __  __      _____      ___
  |     \    |      |    /   \     /    \    |  \/  |    |     \    |   \
  |  |\  \   |  |~|_|   |     |   |  /\  |   |      |    |  |\  \   |    \
  |  | \  \  |  |  |    |     |   | |  | |   |  |\/  |   |  | \  \  |  |\  \
  |  |  |  | |  |__|    |     |   | |__| |   |  |  |  |  |  |  |  | |  | |  |
  |  |_/  /  |   \      |     |   |      |   |  |  |  |  |  |_/  /  |  | |  |
  |      /   |    \     |     |   |  /\  |   |  |  |  |  |      /   |  | |  |
  |  |\  \   |     \    |     |   | |  | |   |  |  |  |  |  |\  \   |  | |  |
  |  | \  \  |  |\  \   |     |   | |  | |   |  |  |  |  |  | \  \  |  | |  |
  |  |  \  \ |  | |  |  |     |   | |  | |   |  |  |  |  |  |  \  \ |  | |  |
  |  |   |  ||  |_/  /   \___/    | |  | |   |  |__|  |  |  |   |  ||  |/  /
  |__|   |__||______/     \_/     |_|  |_|   |________|  |__|   |__||_____/

   /\  TOWN   /\  CAVE   $$$  TREASURE   <><>  MONSTERS   /\  ADVENTURE
"""

# Simplified Game Over ASCII art
GAME_OVER_ASCII = r"""
   _____                         ____                 
  / ____|                       / __ \                
 | |  __  __ _ _ __ ___   ___  | |  | |_   _____ _ __ 
 | | |_ |/ _` | '_ ` _ \ / _ \ | |  | \ \ / / _ \ '__|
 | |__| | (_| | | | | | |  __/ | |__| |\ V /  __/ |   
  \_____|\__,_|_| |_| |_|\___|  \____/  \_/ \___|_|   
                                                      
  +---------------------------------------------+
  |  Your adventure has come to an unfortunate  |
  |           end in the dark caves.            |
  +---------------------------------------------+
"""

def show_game_over_screen(screen, reason=None):
    """Show game over screen with option to restart or return to menu"""
    font = pygame.font.SysFont("Courier New", 36, bold=True)
    message_font = pygame.font.SysFont("Courier New", 24)
    ascii_font = pygame.font.SysFont("Courier New", 16)  # For ASCII art
    option_font = pygame.font.SysFont("Courier New", 20)
    
    # Colors
    title_color = (255, 100, 100)  # Red
    ascii_color = (180, 0, 0)      # Darker red for ASCII art
    message_color = (200, 200, 200)  # Light gray
    option_color = (200, 200, 200)  # Light gray
    selected_color = (100, 255, 100)  # Green
    
    # Options
    options = ["Return to Main Menu", "Quit Game"]
    selected = 0
    
    running = True
    clock = pygame.time.Clock()
    
    # Parse ASCII art
    ascii_lines = GAME_OVER_ASCII.split('\n')
    
    while running:
        screen.fill(GameConfig.BG_COLOR)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected == 0:  # Return to Main Menu
                        return "menu"
                    else:  # Quit Game
                        pygame.quit()
                        sys.exit()
        
        # Draw ASCII art
        y_offset = 50
        for line in ascii_lines:
            if line.strip():  # Skip empty lines
                text_surf = ascii_font.render(line, True, ascii_color)
                x_offset = (GameConfig.SCREEN_WIDTH - text_surf.get_width()) // 2
                screen.blit(text_surf, (x_offset, y_offset))
            y_offset += 16
        
        # Draw reason if provided
        if reason:
            reason_text = message_font.render(reason, True, message_color)
            reason_x = (GameConfig.SCREEN_WIDTH - reason_text.get_width()) // 2
            screen.blit(reason_text, (reason_x, y_offset + 30))
        
        # Draw options
        start_y = y_offset + 100
        for i, option in enumerate(options):
            color = selected_color if i == selected else option_color
            option_text = option_font.render(option, True, color)
            option_x = (GameConfig.SCREEN_WIDTH - option_text.get_width()) // 2
            
            # Draw selection indicators
            if i == selected:
                indicator = ">> "
                indicator_surf = option_font.render(indicator, True, color)
                screen.blit(indicator_surf, (option_x - indicator_surf.get_width(), start_y + i * 40))
                
                indicator = " <<"
                indicator_surf = option_font.render(indicator, True, color)
                screen.blit(indicator_surf, (option_x + option_text.get_width(), start_y + i * 40))
            
            screen.blit(option_text, (option_x, start_y + i * 40))
        
        pygame.display.flip()
        clock.tick(30)
    
    return "quit"
