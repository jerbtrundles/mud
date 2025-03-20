# bestiary.py
from items.item_factory import ItemFactory
from systems.bestiary_entry import BestiaryEntry

class Bestiary:
    """Main bestiary class to track and display enemy information"""
    def __init__(self, game_state):
        self.game_state = game_state
        self.entries = {}  # {enemy_name: BestiaryEntry}
        self.enemy_descriptions = {
            "goblin": {
                "description": "Small, green-skinned humanoids known for their cunning and cowardice. They prefer to attack in groups and are often found in dark, underground spaces.",
                "difficulty": "Easy",
                "type": "Humanoid",
                "common_drops": ["coin", "healing_potion", "stick"],
                "rare_drops": ["common_box_key", "common_treasure_box"],
                "weakness": "Light",
                "habitat": "Caves, Goblin Territory"
            },
            "skeleton": {
                "description": "Animated bones of the dead, these undead creatures are mindless and relentless in their attacks. They make a distinctive rattling sound when they move.",
                "difficulty": "Medium",
                "type": "Undead",
                "common_drops": ["coin", "bone"],
                "rare_drops": ["common_box_key"],
                "weakness": "Blunt weapons",
                "habitat": "Caverns, Narrow Passages"
            },
            "troll": {
                "description": "Massive, brutish creatures with incredible strength and regenerative abilities. They are not very intelligent but make up for it with raw power.",
                "difficulty": "Hard",
                "type": "Giant",
                "common_drops": ["coin", "troll_hide"],
                "rare_drops": ["uncommon_treasure_box", "rare_box_key"],
                "weakness": "Fire",
                "habitat": "Underground Lake, Hidden Grotto"
            },
            "spider": {
                "description": "Oversized arachnids that lurk in dark corners. Some species can spit venom or weave webs to trap unwary adventurers.",
                "difficulty": "Easy",
                "type": "Beast",
                "common_drops": ["coin", "spider_silk"],
                "rare_drops": ["poison_sac"],
                "weakness": "Fire",
                "habitat": "Entrance, Cavern"
            },
            "orc": {
                "description": "Brutish humanoids with tusks and a natural aptitude for violence. More organized and dangerous than goblins, they often serve as leaders.",
                "difficulty": "Medium",
                "type": "Humanoid",
                "common_drops": ["coin", "orc_tooth"],
                "rare_drops": ["uncommon_box_key"],
                "weakness": "None",
                "habitat": "Cavern, Goblin Den"
            },
            "ghost": {
                "description": "Spectral remnants of deceased beings, these ethereal entities can pass through solid objects and are immune to normal weapons.",
                "difficulty": "Hard",
                "type": "Undead",
                "common_drops": ["coin", "ectoplasm"],
                "rare_drops": ["rare_box_key"],
                "weakness": "Magic",
                "habitat": "Narrow Passage, Treasure Room"
            },
            "rat": {
                "description": "Giant rodents that thrive in dark, damp places. Often carriers of disease, their bites can cause infections if not treated.",
                "difficulty": "Very Easy",
                "type": "Beast",
                "common_drops": ["coin", "rat_tail"],
                "rare_drops": ["disease_cure"],
                "weakness": "None",
                "habitat": "Entrance, Cavern, Underground Lake"
            },
            "bat": {
                "description": "Cave-dwelling flying mammals with excellent echolocation. They're not inherently aggressive but can become territorial.",
                "difficulty": "Very Easy",
                "type": "Beast",
                "common_drops": ["coin", "bat_wing"],
                "rare_drops": ["echo_crystal"],
                "weakness": "Sound",
                "habitat": "Cavern, Narrow Passage, Hidden Grotto"
            },
            "slime": {
                "description": "Amorphous creatures composed of semi-solid goo. They absorb nutrients through their body and can split into smaller slimes when damaged.",
                "difficulty": "Easy",
                "type": "Ooze",
                "common_drops": ["coin", "slime_residue"],
                "rare_drops": ["reactive_gel"],
                "weakness": "Fire",
                "habitat": "Underground Lake, Hidden Grotto"
            },
            "zombie": {
                "description": "Reanimated corpses with an insatiable hunger for living flesh. Slow but relentless, they attack with surprising strength.",
                "difficulty": "Medium",
                "type": "Undead",
                "common_drops": ["coin", "rotted_flesh"],
                "rare_drops": ["brain_matter"],
                "weakness": "Fire",
                "habitat": "Goblin Den, Narrow Passage"
            }
        }
    
    def record_encounter(self, enemy_name, killed=False, damage_dealt=0, damage_taken=0, location=None):
        """Record an encounter with an enemy"""
        if enemy_name not in self.entries:
            self.entries[enemy_name] = BestiaryEntry(enemy_name)
        
        self.entries[enemy_name].update(killed, damage_dealt, damage_taken, location)
        
        # Add achievement for discovering many enemy types
        if len(self.get_discovered_enemies()) == 5:
            self.game_state.journal.add_achievement(
                "Monster Scholar", 
                "Encountered and recorded 5 different types of creatures in your bestiary."
            )
        elif len(self.get_discovered_enemies()) == 10:
            self.game_state.journal.add_achievement(
                "Monster Expert", 
                "Encountered and recorded all 10 types of creatures in your bestiary."
            )
    
    def get_entry(self, enemy_name):
        """Get a bestiary entry for a specific enemy"""
        return self.entries.get(enemy_name)
    
    def get_all_entries(self):
        """Get all bestiary entries"""
        return self.entries
    
    def get_discovered_enemies(self):
        """Get list of all discovered enemies"""
        return [name for name, entry in self.entries.items() if entry.discovered]
    
    def get_enemy_description(self, enemy_name):
        """Get the description for an enemy"""
        return self.enemy_descriptions.get(enemy_name, {}).get("description", "No information available.")
    
    def get_enemy_details(self, enemy_name):
        """Get detailed information about an enemy"""
        if enemy_name not in self.enemy_descriptions:
            return None
            
        details = self.enemy_descriptions[enemy_name].copy()
        
        # Format drops with proper item names
        for drop_type in ["common_drops", "rare_drops"]:
            if drop_type in details:
                formatted_drops = []
                for item_name in details[drop_type]:
                    item = ItemFactory.get_item(item_name)
                    if item:
                        formatted_drops.append(item.display_name())
                    else:
                        formatted_drops.append(item_name.replace("_", " "))
                details[drop_type] = formatted_drops
        
        return details
    
    def save_to_dict(self):
        """Convert bestiary to a dictionary for saving"""
        entries_dict = {}
        for name, entry in self.entries.items():
            entries_dict[name] = {
                "encounters": entry.encounters,
                "kills": entry.kills,
                "damage_dealt": entry.damage_dealt,
                "damage_taken": entry.damage_taken,
                "discovered": entry.discovered,
                "last_seen_location": entry.last_seen_location,
                "weakness": entry.weakness,
                "resistance": entry.resistance
            }
        return entries_dict
    
    def load_from_dict(self, data):
        """Load bestiary from a dictionary"""
        self.entries = {}
        for name, entry_data in data.items():
            entry = BestiaryEntry(name)
            entry.encounters = entry_data.get("encounters", 0)
            entry.kills = entry_data.get("kills", 0)
            entry.damage_dealt = entry_data.get("damage_dealt", 0)
            entry.damage_taken = entry_data.get("damage_taken", 0)
            entry.discovered = entry_data.get("discovered", False)
            entry.last_seen_location = entry_data.get("last_seen_location", None)
            entry.weakness = entry_data.get("weakness", None)
            entry.resistance = entry_data.get("resistance", None)
            self.entries[name] = entry
