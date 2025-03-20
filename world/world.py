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
            "items": ["steel_sword", "healing_potion", "bread", "rare_box_key"]
        })
        
        goblin_territory.add_room("treasure_room", {
            "description": "A small chamber filled with the remnants of an ancient civilization. Gold coins are scattered about, and gems glitter in the light.",
            "exits": {"south": "narrow_passage"},
            "items": [
                "gem", "ruby", "emerald", "golden_crown", "ancient_scroll", 
                "ancient_blade", "rare_treasure_box", "protection_amulet", "vampire_ring"
            ],
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
                # Consumables
                "healing_potion": {"price": 5, "description": "Restores 20 health points."},
                "strong_healing_potion": {"price": 15, "description": "Restores 50 health points."},
                "stamina_potion": {"price": 10, "description": "Temporarily increases attack power."},
                
                # Basic armor pieces
                "leather_cap": {"price": 5, "description": "A simple leather cap offering minimal protection."},
                "leather_armor": {"price": 15, "description": "Simple leather armor offering basic protection."},
                "leather_gloves": {"price": 5, "description": "Simple leather gloves that provide minimal protection."},
                "leather_leggings": {"price": 10, "description": "Simple leather pants that provide basic protection."},
                "leather_boots": {"price": 8, "description": "Simple leather boots that provide basic foot protection."},
                
                # Basic weapons
                "rusty_sword": {"price": 7, "description": "An old, rusty sword. It's seen better days but still cuts."},
                
                # Tools
                "torch": {"price": 2, "description": "A wooden torch that can be lit to illuminate dark areas."},
                "pickaxe": {"price": 8, "description": "A tool for mining gems."},
                "stick": {"price": 1, "description": "A simple wooden stick."},
                "cloth": {"price": 1, "description": "A piece of cloth."},
                
                # Keys
                "common_box_key": {"price": 8, "description": "A simple key that opens common treasure boxes."},
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
                # Intermediate weapons
                "steel_sword": {"price": 22, "description": "A well-crafted steel sword, sharp and reliable."},
                
                # Advanced weapons
                "ancient_blade": {"price": 50, "description": "A mysterious blade of unknown origin. It seems to hum with power."},
                
                # Intermediate armor
                "iron_helmet": {"price": 15, "description": "A solid iron helmet that protects your head from blows."},
                "chainmail": {"price": 28, "description": "A shirt of interlocking metal rings providing good protection."},
                "chainmail_gauntlets": {"price": 12, "description": "Gauntlets made of fine chainmail that protect your hands and wrists."},
                "chainmail_leggings": {"price": 22, "description": "Leggings crafted from interwoven metal rings."},
                "chain_boots": {"price": 18, "description": "Boots reinforced with chainmail for added protection."},
                
                # Advanced armor
                "plate_armor": {"price": 40, "description": "Heavy plate armor offering superior protection."},
                "plate_gauntlets": {"price": 25, "description": "Heavy metal gauntlets that offer excellent protection for your hands."},
                "plate_greaves": {"price": 35, "description": "Heavy metal plates that protect your legs from serious damage."},
                "plate_boots": {"price": 28, "description": "Heavy boots made of solid metal plates."},
                
                # Tools
                "pickaxe": {"price": 7, "description": "A sturdy pickaxe for mining."},
            },
            "smith_dialogue": [
                "The blacksmith looks up from his work. 'Need something forged or repaired?'",
                "'Quality metal is hard to come by these days.'",
                "'That armor you're wearing could use some work. I can fix it up for you.'",
                "'Careful with that blade. Even the finest steel can break if mistreated.'",
                "'Found some interesting ore near the hidden grotto. Makes for excellent weapons.'",
                "'A full set of plate armor will keep you safer than mismatched pieces.'",
                "'Each piece of armor counts. Don't neglect your helmet and boots!'"
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

        town.add_room("alchemist", {
            "description": "The alchemist's shop is filled with bubbling concoctions and strange aromas. Colorful bottles line the shelves, and dried herbs hang from the ceiling. A slender elf carefully measures ingredients at a workbench covered with arcane tools and mysterious substances.",
            "exits": {"west": "town_square", "north": "garden"},
            "items": [],
            "is_shop": True,
            "shop_inventory": {
                # Potions
                "healing_potion": {"price": 5, "description": "A red potion that restores health."},
                "strong_healing_potion": {"price": 12, "description": "A vibrant red potion that restores significant health."},
                "stamina_potion": {"price": 8, "description": "A green potion that temporarily increases attack power."},
                "antidote": {"price": 8, "description": "A green potion that neutralizes poison."},
                "elixir_of_clarity": {"price": 15, "description": "A purple potion that enhances perception and reflexes."},
                
                # Magical armor and accessories
                "enchanted_circlet": {"price": 30, "description": "A silver circlet with a glowing blue gem that enhances mental focus."},
                "thief_gloves": {"price": 20, "description": "Lightweight gloves made of supple leather that improve dexterity."},
                "explorer_boots": {"price": 35, "description": "Enchanted boots that make walking easier and reduce fatigue."},
                
                # Jewelry
                "basic_amulet": {"price": 10, "description": "A simple amulet with a small protective enchantment."},
                "healing_amulet": {"price": 30, "description": "A ruby amulet that slowly regenerates health over time."},
                "simple_ring": {"price": 5, "description": "A plain metal ring with a minor enchantment."},
                "strength_ring": {"price": 25, "description": "A ring that enhances the wearer's physical strength."},
                "mage_ring": {"price": 35, "description": "A sapphire ring that enhances magical abilities."}
            },
            "alchemist_dialogue": [
                "The alchemist looks up from her work. 'Ah, a customer! Interested in my potions?'",
                "'Each potion is crafted with utmost care and the finest ingredients.'",
                "'That mushroom you passed by might be more valuable than you think.'",
                "'I'm working on a new formula. Just need a few rare ingredients from the deeper caves.'",
                "'Careful with mixing potions. The results can be... unpredictable.'",
                "'My enchanted circlets improve focus and mental clarity.'",
                "'These rings may look simple, but they hold powerful enchantments.'"
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