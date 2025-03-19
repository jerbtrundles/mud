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
