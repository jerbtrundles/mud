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