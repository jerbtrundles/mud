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
                # Save the full equipment dictionary instead of just weapon/armor
                "equipment": game_state.player.equipment,
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
            "enemies": [],
            
            # Status effects (new)
            "status_effects": []
        }
        
        # Save status effects
        if hasattr(game_state, 'status_effect_manager'):
            for effect_name, effect in game_state.status_effect_manager.active_effects.items():
                effect_data = {
                    "name": effect.name,
                    "duration": effect.duration,
                    "strength": effect.strength,
                    "start_time": effect.start_time,
                    "remaining_time": effect.get_time_remaining()
                }
                save_data["status_effects"].append(effect_data)
        
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
                
                # Save special attacks if present
                if hasattr(enemy, 'special_attacks') and enemy.special_attacks:
                    enemy_data["special_attacks"] = enemy.special_attacks
                    
                save_data["enemies"].append(enemy_data)
        
        # Save game history (last 20 messages)
        save_data["history"] = game_state.game_history[-20:] if len(game_state.game_history) > 20 else game_state.game_history
        save_data["journal"] = game_state.journal.save_to_dict()
        
        # Save bestiary data
        save_data["bestiary"] = game_state.bestiary.save_to_dict()

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
        game_state.player.inventory = player_data["inventory"]
        
        # Check if we have the newer equipment dictionary format
        if "equipment" in player_data:
            # New format with equipment slots
            game_state.player.equipment = player_data["equipment"]
        else:
            # Legacy format with separate weapon/armor
            # Initialize an empty equipment dictionary with slots
            game_state.player.equipment = {
                "head": None,
                "chest": None,
                "hands": None,
                "legs": None,
                "feet": None,
                "neck": None,
                "ring": None,
                "weapon": None
            }
            
            # Set weapon and armor from old format if they exist
            if "weapon" in player_data and player_data["weapon"]:
                game_state.player.equipment["weapon"] = player_data["weapon"]
                
            if "armor" in player_data and player_data["armor"]:
                # In the old format, armor was just a single item, assign it to the chest slot
                game_state.player.equipment["chest"] = player_data["armor"]
        
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
        
        # Load status effects
        if "status_effects" in save_data and hasattr(game_state, 'status_effect_manager'):
            # Clear existing effects first
            game_state.status_effect_manager.active_effects = {}
            
            # Import needed status effect classes
            from systems.status_effects.status_effects import PoisonEffect
            
            for effect_data in save_data["status_effects"]:
                # Create the appropriate effect based on type
                if effect_data["name"] == "poison":
                    effect = PoisonEffect(
                        duration=effect_data["duration"],
                        strength=effect_data["strength"]
                    )
                    # Adjust start time to maintain remaining duration
                    current_time = time.time()
                    remaining_time = effect_data.get("remaining_time", effect.duration)
                    effect.start_time = current_time - (effect.duration - remaining_time)
                    effect.last_tick_time = current_time  # Reset tick timer
                    
                    # Add to active effects
                    game_state.status_effect_manager.active_effects[effect.name] = effect
        
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
                # Create base enemy
                enemy = Enemy(
                    name=enemy_data["name"],
                    health=enemy_data["max_health"],  # Initialize with max health
                    attack=enemy_data["attack"],
                    experience=enemy_data["experience"],
                    allowed_rooms=[enemy_data["current_room"]],  # Minimal allowed rooms
                    respawn_delay=enemy_data.get("respawn_delay", 60)  # Default if missing
                )
                
                # Load special attacks if present
                if "special_attacks" in enemy_data:
                    enemy.special_attacks = enemy_data["special_attacks"]
                
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
            
        # Load bestiary data if available
        if "bestiary" in save_data:
            game_state.bestiary.load_from_dict(save_data["bestiary"])

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