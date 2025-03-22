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
            difficulty=1  # Level 1-3
        )
        
        # Goblin Territory Region
        self.regions["goblin_territory"] = Region(
            name="goblin_territory",
            display_name="Goblin Territory",
            description="An area claimed by goblins, marked with crude symbols and primitive structures.",
            region_type="monster_lair",
            difficulty=2  # Level 3-5
        )
        
        # Town Region
        self.regions["town"] = Region(
            name="town",
            display_name="Adventurer's Rest",
            description="A small outpost where adventurers gather to trade and rest.",
            region_type="settlement",
            difficulty=0  # Safe zone
        )
        
        # NEW REGION: Fungal Grottos
        self.regions["fungal_grottos"] = Region(
            name="fungal_grottos",
            display_name="Fungal Grottos",
            description="Vast chambers filled with glowing mushrooms and strange fungi. The air is thick with spores, and the ground squishes beneath your feet.",
            region_type="wilderness",
            difficulty=3  # Level 5-7
        )
        
        # NEW REGION: Dwarven Ruins
        self.regions["dwarven_ruins"] = Region(
            name="dwarven_ruins",
            display_name="Dwarven Ruins",
            description="Ancient halls and mineshafts built by dwarven craftsmen long ago. Many passages have collapsed, but valuable treasures and dangerous guardians still remain.",
            region_type="ruins",
            difficulty=4  # Level 7-10
        )
        
        # NEW REGION: Crystal Caverns
        self.regions["crystal_caverns"] = Region(
            name="crystal_caverns",
            display_name="Crystal Caverns",
            description="Massive chambers filled with crystals of all sizes and colors. Energy pulses through the formations, creating strange magical effects.",
            region_type="magical",
            difficulty=5  # Level 10-12
        )
        
        # NEW REGION: The Abyssal Rift
        self.regions["abyssal_rift"] = Region(
            name="abyssal_rift",
            display_name="The Abyssal Rift",
            description="A vast chasm that seems to descend forever. Strange phosphorescent light emanates from the depths, illuminating bizarre alien structures and unfamiliar lifeforms.",
            region_type="eldritch",
            difficulty=6  # Level 12-15
        )

        # NEW REGION: Sunlit Forest
        self.regions["sunlit_forest"] = Region(
            name="sunlit_forest",
            display_name="Sunlit Forest",
            description="A vibrant woodland area where sunlight filters through the canopy. The air is fresh and wildlife can be seen and heard all around.",
            region_type="wilderness",
            difficulty=1  # Level 1-3
        )
        
        # NEW REGION: Farmlands
        self.regions["farmlands"] = Region(
            name="farmlands",
            display_name="Fertile Farmlands",
            description="Rolling fields of crops and pastures surround scattered farmhouses. The area is peaceful but not without its dangers.",
            region_type="countryside",
            difficulty=1  # Level 1-3
        )
        
        # NEW REGION: Coastal Cliffs
        self.regions["coastal_cliffs"] = Region(
            name="coastal_cliffs",
            display_name="Coastal Cliffs",
            description="Dramatic cliffs overlooking a vast ocean. Salt spray fills the air, and seabirds nest in the rocky outcroppings.",
            region_type="wilderness",
            difficulty=2  # Level 3-5
        )
        
        # NEW REGION: Ancient Temple
        self.regions["ancient_temple"] = Region(
            name="ancient_temple",
            display_name="Ancient Temple",
            description="A weathered temple complex dedicated to forgotten gods. Stone statues and crumbling altars hint at past reverence.",
            region_type="ruins",
            difficulty=3  # Level 5-7
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
            "exits": {"north": "cavern", "west": "east_gate"},
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
            "exits": {"south": "underground_lake", "north": "fungal_entrance"},
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
            "exits": {
                "north": "tavern",      # existing
                "west": "blacksmith",   # existing
                "south": "chapel",      # existing
                "east": "alchemist",    # existing
                "northeast": "market_street"  # new
            },
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

        town.add_room("market_street", {
            "description": "A bustling street lined with merchant stalls and small shops. Traders call out their wares, and the air is filled with the scents of spices, leather, and fresh bread.",
            "exits": {"southwest": "town_square", "north": "north_gate", "east": "east_district"},
            "items": ["apple", "leather_gloves"],
            "is_market": True,
            "market_inventory": {
                "bread": {"price": 1, "description": "A fresh loaf of bread."},
                "cheese": {"price": 2, "description": "A wedge of local cheese."},
                "dried_meat": {"price": 3, "description": "Preserved meat for traveling."},
                "simple_clothes": {"price": 4, "description": "Basic traveling clothes."},
                "backpack": {"price": 8, "description": "A sturdy canvas backpack."}
            }
        })

        # North Gate - leads to Farmlands
        town.add_room("north_gate", {
            "description": "The northern gate of the town, consisting of a sturdy wooden structure with guard posts. Beyond, you can see fields and farmland stretching into the distance.",
            "exits": {"south": "market_street", "north": "farm_road"},
            "items": ["torch"],
            "is_guard_post": True,
            "guard_dialogue": [
                "The guard nods as you pass. 'Travel safely. The farms are peaceful, but wild animals sometimes prowl at night.'",
                "'Make sure to visit the crossroads if you need supplies. The farmers are friendly folk.'",
                "'Been some strange travelers coming from the north lately. Keep your wits about you.'"
            ]
        })

        # East District - residential area
        town.add_room("east_district", {
            "description": "A quiet residential area with modest homes built into the cavern walls. Children play in small yards, and neighbors chat across stone fences.",
            "exits": {"west": "market_street", "south": "craftsman_corner", "east": "east_gate"},
            "items": ["child_toy", "flower_pot"]
        })

        # East Gate - leads to Cave System
        town.add_room("east_gate", {
            "description": "The eastern gate of the town, where the inhabited area meets the untamed caves. Adventurers gather here before setting out, checking their gear one last time.",
            "exits": {"west": "east_district", "east": "entrance"},
            "items": ["map_fragment", "torch", "water_flask"],
            "is_guard_post": True,
            "guard_dialogue": [
                "The guard looks you up and down. 'Heading into the caves? Make sure you're prepared.'",
                "'We've lost too many good folk to the dangers beyond. Don't become another statistic.'",
                "'If you find any goblin scouts near town, report back immediately. We've had raids recently.'"
            ]
        })

        # Craftsman Corner - specialized shops
        town.add_room("craftsman_corner", {
            "description": "A section of town dedicated to skilled craftspeople. The constant sounds of hammering, sawing, and the smell of various materials fill the air. Each workshop specializes in different crafts.",
            "exits": {"north": "east_district", "west": "south_plaza", "east": "tinker_workshop"},
            "items": ["crafting_tools", "wooden_figure"]
        })

        # Tinker Workshop - gadgets and devices
        town.add_room("tinker_workshop", {
            "description": "A cluttered workshop filled with strange contraptions, gears, and mechanical devices in various states of assembly. The gnomish tinker barely looks up from her work as you enter.",
            "exits": {"west": "craftsman_corner"},
            "items": ["small_gear", "strange_device"],
            "is_shop": True,
            "shop_inventory": {
                "pocket_watch": {"price": 15, "description": "A precise timekeeper with tiny gears."},
                "mechanical_trap": {"price": 12, "description": "A device that can be set to catch small game."},
                "folding_tool": {"price": 8, "description": "A compact tool with multiple functions."},
                "music_box": {"price": 20, "description": "A small box that plays a tinkling melody when wound."},
                "glowing_lantern": {"price": 25, "description": "A specially designed lantern that burns longer than normal."}
            }
        })

        # South Plaza - southern gathering area
        town.add_room("south_plaza", {
            "description": "A smaller plaza in the southern part of town. A large well stands in the center, serving as both water source and meeting place. The area is decorated with hanging lanterns.",
            "exits": {"east": "craftsman_corner", "north": "chapel", "west": "west_district", "south": "south_gate"},
            "items": ["water_bucket", "lantern"]
        })

        # South Gate - leads to Ancient Temple
        town.add_room("south_gate", {
            "description": "The southern gate of town, smaller than the others but well-maintained. Stone pillars reminiscent of the ancient temple in the distance flank the path leading outward.",
            "exits": {"north": "south_plaza", "south": "temple_road"},
            "items": ["stone_fragment", "religious_symbol"],
            "is_guard_post": True,
            "guard_dialogue": [
                "The guard gives you a respectful nod. 'The temple road is generally safe, but the ruins themselves... that's another matter.'",
                "'Some say the old gods still watch over those who pray at the temple. Others say they've abandoned us.'",
                "'If you're a scholar, you'll find much to study there. If you're a treasure hunter, show some respect.'"
            ]
        })

        # West District - more shops and homes
        town.add_room("west_district", {
            "description": "The western part of town features a mix of homes and businesses built in a circular pattern around a small garden area. The architecture here incorporates more stonework.",
            "exits": {"east": "south_plaza", "north": "blacksmith", "west": "west_gate"},
            "items": ["potted_plant", "stone_bench"]
        })

        # West Gate - leads to Coastal Cliffs
        town.add_room("west_gate", {
            "description": "The western gate offers a glimpse of the distant ocean beyond the cliffs. The air here carries a faint salty tang, and seabirds occasionally fly overhead.",
            "exits": {"east": "west_district", "west": "cliff_path"},
            "items": ["seashell", "fishing_net"],
            "is_guard_post": True,
            "guard_dialogue": [
                "The guard squints toward the horizon. 'The cliffs are beautiful but dangerous. Watch your step out there.'",
                "'The lighthouse keeper is a bit odd, but he knows more about the coast than anyone.'",
                "'There's good fishing in the coves if you know where to look, but the tides can change quickly.'"
            ]
        })

        # Northwest District - hunting supplies
        town.add_room("northwest_district", {
            "description": "The northwestern corner of town caters to hunters and woodsfolk. Tanned hides hang outside shops, and the smell of leather and smoked meat fills the air.",
            "exits": {"southeast": "blacksmith", "north": "northwest_gate"},
            "items": ["hunting_knife", "animal_pelt"]
        })

        # Northwest Gate - leads to Sunlit Forest
        town.add_room("northwest_gate", {
            "description": "The northwestern gate is simple but sturdy, opening to a path that leads into the forest. Carved wooden totems ward against forest spirits according to local tradition.",
            "exits": {"south": "northwest_district", "northwest": "forest_path"},
            "items": ["wooden_totem", "berry_pouch"],
            "is_guard_post": True,
            "guard_dialogue": [
                "The guard whittles a piece of wood as she speaks. 'The forest is peaceful enough by day, but don't get lost after dark.'",
                "'The rangers have a cabin not far in. They might share information if you're friendly.'",
                "'Watch for the colored trail markers if you venture deep - they'll help you find your way back.'"
            ]
        })

        # ======== Fungal Grottos (Level 5-7) ========
        fungal_grottos = self.regions["fungal_grottos"]
        
        fungal_grottos.add_room("fungal_entrance", {
            "description": "A narrow passage opens up into a humid chamber filled with softly glowing mushrooms. The air feels thick and smells earthy.",
            "exits": {"south": "hidden_grotto", "east": "fungal_junction"},
            "items": ["glowing_mushroom", "torch", "coin", "coin"]
        })
        
        fungal_grottos.add_room("fungal_junction", {
            "description": "Large mushroom caps dot the floor of this chamber, some big enough to stand on. Bioluminescent fungi paint the walls with eerie blue light.",
            "exits": {"west": "fungal_entrance", "north": "spore_chambers", "east": "fungi_forest"},
            "items": ["glowing_mushroom", "uncommon_treasure_box", "healing_potion"]
        })
        
        fungal_grottos.add_room("spore_chambers", {
            "description": "Clouds of glowing spores drift through the air in this large cavern. The floor is covered in a spongy fungal mat that sinks slightly with each step.",
            "exits": {"south": "fungal_junction", "east": "myconid_colony"},
            "items": ["reactive_gel", "strange_spores"]
        })
        
        fungal_grottos.add_room("fungi_forest", {
            "description": "Towering mushroom stalks reach from floor to ceiling, forming a strange forest of fungi. Trails of luminescence pulse along their surfaces in hypnotic patterns.",
            "exits": {"west": "fungal_junction", "north": "myconid_colony", "east": "luminous_pool"},
            "items": ["mushroom_cap", "sturdy_fungus"]
        })
        
        fungal_grottos.add_room("myconid_colony", {
            "description": "This vast chamber houses what appears to be a colony of sentient fungi. Mushroom-like structures form dwellings, and the walls are carved with strange circular patterns.",
            "exits": {"west": "spore_chambers", "south": "fungi_forest", "east": "mushroom_queen"},
            "items": ["rare_spores", "myconid_staff", "coin", "coin", "coin"]
        })
        
        fungal_grottos.add_room("luminous_pool", {
            "description": "A pool of glowing blue water sits in the center of this chamber. Small luminescent fish dart beneath the surface, and the ceiling is dotted with thousands of tiny glowing mushrooms like stars.",
            "exits": {"west": "fungi_forest", "north": "mushroom_queen"},
            "items": ["glowing_fish", "purified_water"]
        })
        
        fungal_grottos.add_room("mushroom_queen", {
            "description": "The heart of the fungal grottos. A massive mushroom structure dominates the center of this chamber, pulsing with vibrant colors. The air is thick with magic and spores.",
            "exits": {"west": "myconid_colony", "south": "luminous_pool", "north": "ruined_entrance"},
            "items": ["queen_cap", "rare_treasure_box", "uncommon_box_key"]
        })
        
        # ======== Dwarven Ruins (Level 7-10) ========
        dwarven_ruins = self.regions["dwarven_ruins"]
        
        dwarven_ruins.add_room("ruined_entrance", {
            "description": "A grand stone archway, partially collapsed, marks the entrance to an ancient dwarven settlement. Runes carved into the walls have worn with time, but still shimmer faintly.",
            "exits": {"south": "mushroom_queen", "north": "collapsed_hall"},
            "items": ["dwarven_rune", "old_pickaxe", "coin", "coin", "coin"]
        })
        
        dwarven_ruins.add_room("collapsed_hall", {
            "description": "A once-majestic hall now in ruins. Parts of the ceiling have fallen, and support pillars lie broken on the ground. Dust fills the air, and the sound of shifting stone can be heard in the distance.",
            "exits": {"south": "ruined_entrance", "west": "barracks", "east": "forge_room", "north": "throne_room"},
            "items": ["dwarven_helmet", "uncommon_treasure_box"]
        })
        
        dwarven_ruins.add_room("barracks", {
            "description": "Rows of stone beds line the walls of this chamber, once housing the dwarven guards. Rusted weapon racks and broken armor litter the floor, remnants of a hasty evacuation.",
            "exits": {"east": "collapsed_hall", "north": "armory"},
            "items": ["rusted_axe", "dwarven_shield", "steel_sword"]
        })
        
        dwarven_ruins.add_room("forge_room", {
            "description": "The heart of dwarven craftsmanship. Ancient forges stand cold, but magical embers still glow in some of the furnaces. Tools of exceptional quality are scattered about, waiting to be claimed.",
            "exits": {"west": "collapsed_hall", "north": "treasure_vault"},
            "items": ["master_hammer", "rare_metal", "smith_plans"]
        })
        
        dwarven_ruins.add_room("armory", {
            "description": "A chamber devoted to the storage of weapons and armor. Most racks are empty, but some prized pieces remain, protected by ancient wards that still function.",
            "exits": {"south": "barracks", "east": "throne_room"},
            "items": ["dwarven_axe", "chainmail", "rare_box_key"]
        })
        
        dwarven_ruins.add_room("treasure_vault", {
            "description": "A massive vault with walls of solid stone. Heavy metal doors hang broken from their hinges. While most treasures are gone, overlooked items of value still remain in shadowy corners.",
            "exits": {"south": "forge_room", "west": "throne_room"},
            "items": ["gemstone_collection", "gold_ingot", "rare_treasure_box"]
        })
        
        dwarven_ruins.add_room("throne_room", {
            "description": "The grand throne room of the dwarven king. A massive stone throne sits atop a dais, cracked but still majestic. The walls are adorned with elaborate carvings depicting dwarven history.",
            "exits": {"south": "collapsed_hall", "west": "armory", "east": "treasure_vault", "north": "deep_mine"},
            "items": ["royal_signet", "ancient_crown", "epic_treasure_box"]
        })
        
        dwarven_ruins.add_room("deep_mine", {
            "description": "A vast mining operation that extends deep into the mountain. Cart tracks lead off in multiple directions, and the walls sparkle with veins of precious metals and gemstones.",
            "exits": {"south": "throne_room", "north": "crystal_passage"},
            "items": ["uncut_gem", "mining_pick", "explosive_powder"]
        })
        
        # ======== Crystal Caverns (Level 10-12) ========
        crystal_caverns = self.regions["crystal_caverns"]
        
        crystal_caverns.add_room("crystal_passage", {
            "description": "A narrow tunnel whose walls are lined with small crystals that emit a soft, pulsating light. The air feels charged with energy, and sounds echo strangely.",
            "exits": {"south": "deep_mine", "north": "crystal_junction"},
            "items": ["small_crystal", "energy_shard", "coin", "coin", "coin"]
        })
        
        crystal_caverns.add_room("crystal_junction", {
            "description": "A large cavern where crystal formations create natural columns from floor to ceiling. Light refracts through the crystals, creating rainbow patterns on the walls. The air hums with magical energy.",
            "exits": {"south": "crystal_passage", "west": "resonance_chamber", "east": "reflection_pool", "north": "crystal_forest"},
            "items": ["resonating_crystal", "rare_treasure_box"]
        })
        
        crystal_caverns.add_room("resonance_chamber", {
            "description": "A perfect dome-shaped chamber where crystals of various sizes are arranged in concentric circles. Tapping any crystal creates harmonic sounds that are amplified throughout the space.",
            "exits": {"east": "crystal_junction", "north": "phase_zone"},
            "items": ["harmonic_crystal", "sonic_gem", "rare_box_key"]
        })
        
        crystal_caverns.add_room("reflection_pool", {
            "description": "A still pool of water surrounded by mirror-like crystal formations. The reflections create an infinite regress of images, and sometimes show glimpses of other places or times.",
            "exits": {"west": "crystal_junction", "north": "crystal_forge"},
            "items": ["mirror_shard", "temporal_crystal", "vial_of_reflections"]
        })
        
        crystal_caverns.add_room("crystal_forest", {
            "description": "An otherworldly forest of massive crystal formations in all colors and shapes. They grow from floor to ceiling like trees, creating a labyrinthine path through the chamber.",
            "exits": {"south": "crystal_junction", "west": "phase_zone", "east": "crystal_forge", "north": "energy_nexus"},
            "items": ["growth_crystal", "prismatic_shard", "crystal_staff"]
        })
        
        crystal_caverns.add_room("phase_zone", {
            "description": "An area where reality seems to shift and waver. Stepping through certain crystal archways teleports you to another part of the chamber. The very air seems to phase in and out of existence.",
            "exits": {"south": "resonance_chamber", "east": "crystal_forest"},
            "items": ["phase_crystal", "displacement_orb", "epic_box_key"]
        })
        
        crystal_caverns.add_room("crystal_forge", {
            "description": "A natural forge where intense geothermal heat melts even the hardest crystals. Magical tools hover in place, waiting to be used by those who understand their function.",
            "exits": {"south": "reflection_pool", "west": "crystal_forest"},
            "items": ["crystal_hammer", "forge_crystal", "elemental_essence"]
        })
        
        crystal_caverns.add_room("energy_nexus", {
            "description": "The heart of the crystal caverns. A massive central crystal pillar pulses with blinding light, connecting to smaller crystals throughout the chamber in a web of energy beams.",
            "exits": {"south": "crystal_forest", "north": "rift_entrance"},
            "items": ["nexus_crystal", "energy_core", "epic_treasure_box"]
        })
        
        # ======== The Abyssal Rift (Level 12-15) ========
        abyssal_rift = self.regions["abyssal_rift"]
        
        abyssal_rift.add_room("rift_entrance", {
            "description": "A jagged tear in reality leads to a vast chasm that seems to descend forever. Strange winds howl from the depths, carrying whispers in unknown languages. The rock itself seems alien and wrong.",
            "exits": {"south": "energy_nexus", "north": "floating_islands"},
            "items": ["rift_stone", "echo_crystal", "coin", "coin", "coin", "coin", "coin"]
        })
        
        abyssal_rift.add_room("floating_islands", {
            "description": "Chunks of rock hang suspended in the void, connected by narrow stone bridges. Far below, strange lights pulse in patterns that hurt the mind to observe. The laws of physics seem optional here.",
            "exits": {"south": "rift_entrance", "west": "aberration_pools", "east": "twisted_library", "north": "descent_path"},
            "items": ["levitation_crystal", "void_essence", "epic_treasure_box"]
        })
        
        abyssal_rift.add_room("aberration_pools", {
            "description": "Pools of liquid that defies categorization - neither water nor slime nor acid, but something else entirely. Bizarre creatures swim in the depths, occasionally surfacing to observe visitors.",
            "exits": {"east": "floating_islands", "north": "elder_shrine"},
            "items": ["aberrant_sample", "mutagen_vial", "adaptive_tissue"]
        })
        
        abyssal_rift.add_room("twisted_library", {
            "description": "A collection of stone shelves filled with tablets, scrolls, and books in languages never meant for human tongues. The knowledge here is vast but dangerous, and the air vibrates with forbidden magic.",
            "exits": {"west": "floating_islands", "north": "projection_chamber"},
            "items": ["elder_scroll", "forbidden_tome", "mind_crystal"]
        })
        
        abyssal_rift.add_room("descent_path", {
            "description": "A spiraling path that descends deeper into the rift. Reality grows thinner here, and visions of other worlds occasionally overlay your perception. The path itself seems to shift when not observed directly.",
            "exits": {"south": "floating_islands", "west": "elder_shrine", "east": "projection_chamber", "north": "abyssal_throne"},
            "items": ["reality_shard", "rift_map", "legendary_box_key"]
        })
        
        abyssal_rift.add_room("elder_shrine", {
            "description": "A circular chamber with a stone altar at its center. Carvings of tentacled beings cover the walls, and a sense of being watched permeates the space. Offerings of strange artifacts line the altar.",
            "exits": {"south": "aberration_pools", "east": "descent_path"},
            "items": ["elder_idol", "sacrificial_dagger", "worshiper_robes"]
        })
        
        abyssal_rift.add_room("projection_chamber", {
            "description": "A chamber where the barrier between dimensions is at its thinnest. Ghostly images from other realities project onto the walls, and occasionally solid objects phase into existence before disappearing again.",
            "exits": {"south": "twisted_library", "west": "descent_path"},
            "items": ["reality_lens", "phantom_object", "dimensional_key"]
        })
        
        abyssal_rift.add_room("abyssal_throne", {
            "description": "The deepest chamber in the rift. A massive throne carved from obsidian sits atop a dais, surrounded by strange machines or organisms that pulse with otherworldly light. The very air seems alive with malevolent intelligence.",
            "exits": {"south": "descent_path"},
            "items": ["abyss_crown", "reality_warper", "legendary_treasure_box"],
            "locked": True,
            "key_item": "dimensional_key"
        })

        sunlit_forest = self.regions["sunlit_forest"]
    
        sunlit_forest.add_room("forest_path", {
            "description": "A well-worn path leading from town into the forest. Tall trees begin to line both sides of the trail.",
            "exits": {"southeast": "northwest_gate", "north": "forest_clearing"},
            "items": ["stick", "berry_bush"]
        })
        
        sunlit_forest.add_room("forest_clearing", {
            "description": "A peaceful clearing where sunlight streams down to illuminate a circle of soft grass. Wildflowers dot the area.",
            "exits": {"south": "forest_path", "east": "ranger_cabin", "west": "ancient_oak", "north": "dense_woods"},
            "items": ["healing_herb", "mushroom", "common_treasure_box"]
        })
        
        sunlit_forest.add_room("ranger_cabin", {
            "description": "A small wooden cabin where forest rangers rest and resupply. Hunting trophies adorn the walls.",
            "exits": {"west": "forest_clearing"},
            "items": ["bow", "quiver", "common_box_key"],
            "is_shop": True,
            "shop_inventory": {
                "bow": {"price": 15, "description": "A simple wooden bow for hunting."},
                "arrows": {"price": 5, "description": "A bundle of 10 arrows."},
                "leather_cap": {"price": 5, "description": "A simple leather cap offering minimal protection."},
                "forest_map": {"price": 10, "description": "A map of the surrounding forest."}
            }
        })
        
        # FARMLANDS ROOMS
        farmlands = self.regions["farmlands"]
        
        farmlands.add_room("farm_road", {
            "description": "A dirt road leading from town into the surrounding farmlands. Fields of crops stretch out on either side.",
            "exits": {"south": "north_gate", "east": "crossroads"},
            "items": ["apple", "pitchfork"]
        })
        
        farmlands.add_room("crossroads", {
            "description": "A simple crossroads marked by a weathered signpost. Farm cottages can be seen in the distance.",
            "exits": {"west": "farm_road", "east": "farm_cottage", "south": "riverside"},
            "items": ["bread", "common_treasure_box"]
        })
        
        farmlands.add_room("farm_cottage", {
            "description": "A cozy farmhouse with a thatched roof. Chickens peck at the ground in a small yard.",
            "exits": {"west": "crossroads"},
            "items": ["cooked_meat", "chicken_egg"],
            "is_inn": True,
            "inn_cost": 3,
            "inn_dialogue": [
                "The farm wife smiles. 'Need a place to rest? We have a spare room for just 3 coins.'",
                "'Our chickens lay the best eggs in the region.'",
                "'Be careful if you go near the river. Strange creatures have been seen there lately.'",
                "'My husband trades with the merchants in town every week.'"
            ]
        })
        
        # COASTAL CLIFFS ROOMS
        coastal_cliffs = self.regions["coastal_cliffs"]
        
        coastal_cliffs.add_room("cliff_path", {
            "description": "A winding path that leads from town toward the distant sound of crashing waves.",
            "exits": {"east": "west_gate", "west": "cliff_overlook"},
            "items": ["seashell", "smooth_stone"]
        })
        
        coastal_cliffs.add_room("cliff_overlook", {
            "description": "A breathtaking viewpoint atop high cliffs. Far below, waves crash against jagged rocks.",
            "exits": {"east": "cliff_path", "north": "lighthouse", "south": "hidden_cove", "west": "sea_cave"},
            "items": ["spyglass", "rare_box_key", "uncommon_treasure_box"]
        })
        
        coastal_cliffs.add_room("lighthouse", {
            "description": "An old stone lighthouse standing tall against the sea winds. Its beacon still functions, warning ships of the dangerous rocks.",
            "exits": {"south": "cliff_overlook"},
            "items": ["lantern_oil", "sailor_hat"],
            "is_shop": True,
            "shop_inventory": {
                "lantern": {"price": 8, "description": "A sturdy brass lantern."},
                "fish": {"price": 3, "description": "Fresh caught fish."},
                "sailor_coat": {"price": 12, "description": "A coat that provides protection against the elements."},
                "rope": {"price": 5, "description": "A coil of strong rope."}
            }
        })
        
        # ANCIENT TEMPLE ROOMS
        ancient_temple = self.regions["ancient_temple"]
        
        ancient_temple.add_room("temple_road", {
            "description": "A cobblestone road leading from town toward ancient stone structures visible in the distance.",
            "exits": {"north": "south_gate", "east": "temple_courtyard"},
            "items": ["old_coin", "stone_tablet"]
        })
        
        ancient_temple.add_room("temple_courtyard", {
            "description": "A large open area surrounded by crumbling stone columns. Weeds grow between the ancient paving stones.",
            "exits": {"west": "temple_road", "east": "main_hall", "north": "meditation_garden", "south": "priest_quarters"},
            "items": ["ceremonial_dagger", "uncommon_treasure_box", "uncommon_box_key"]
        })
        
        ancient_temple.add_room("main_hall", {
            "description": "The partially collapsed main hall of the temple. Sunlight streams through holes in the ceiling, illuminating faded murals on the walls.",
            "exits": {"west": "temple_courtyard", "east": "inner_sanctum"},
            "items": ["prayer_beads", "holy_symbol", "rare_treasure_box"]
        })
        
        ancient_temple.add_room("inner_sanctum", {
            "description": "The sacred heart of the temple, protected from the elements and time. A large stone altar dominates the center of the room.",
            "exits": {"west": "main_hall"},
            "items": ["sacred_relic", "epic_treasure_box"],
            "locked": True,
            "key_item": "temple_key"
        })

        self._add_random_treasures()

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
    
    def _add_random_treasures(self):
        """Add random coins and treasure to rooms based on region difficulty"""
        import random
        
        # Define treasure probabilities by region difficulty
        treasure_chances = {
            # difficulty: (coin_chance, min_coins, max_coins, common_box_chance, uncommon_box_chance, rare_box_chance, epic_box_chance)
            0: (0.3, 1, 3, 0.05, 0.01, 0.0, 0.0),       # Town (safe)
            1: (0.7, 1, 5, 0.15, 0.05, 0.01, 0.0),      # Shadowed Depths (level 1-3)
            2: (0.75, 3, 8, 0.2, 0.1, 0.02, 0.0),       # Goblin Territory (level 3-5)
            3: (0.8, 5, 12, 0.25, 0.15, 0.05, 0.01),    # Fungal Grottos (level 5-7)
            4: (0.85, 8, 15, 0.3, 0.2, 0.08, 0.02),     # Dwarven Ruins (level 7-10)
            5: (0.9, 10, 20, 0.3, 0.25, 0.12, 0.04),    # Crystal Caverns (level 10-12)
            6: (0.95, 15, 30, 0.35, 0.3, 0.15, 0.08)    # Abyssal Rift (level 12-15)
        }
        
        for region_name, region in self.regions.items():
            difficulty = region.difficulty
            if difficulty not in treasure_chances:
                difficulty = 1  # Default to easiest if not found
                
            coin_chance, min_coins, max_coins, common_box, uncommon_box, rare_box, epic_box = treasure_chances[difficulty]
            
            # Process each room in the region
            for room_name, room_data in region.rooms.items():
                # Skip shops and special rooms
                if room_data.get("is_shop", False) or room_data.get("is_inn", False):
                    continue
                    
                # Make sure items list exists
                if "items" not in room_data:
                    room_data["items"] = []
                    
                # Add coins
                if random.random() < coin_chance:
                    coin_count = random.randint(min_coins, max_coins)
                    for _ in range(coin_count):
                        if random.random() < 0.7:  # 70% chance to add each coin individually
                            room_data["items"].append("coin")
                
                # Add treasure boxes
                if random.random() < common_box:
                    room_data["items"].append("common_treasure_box")
                    
                if random.random() < uncommon_box:
                    room_data["items"].append("uncommon_treasure_box")
                    
                if random.random() < rare_box:
                    room_data["items"].append("rare_treasure_box")
                    
                if random.random() < epic_box:
                    room_data["items"].append("epic_treasure_box")
                    
                # Very rare chance (0.5%) for legendary box in high-level areas (difficulty 5+)
                if difficulty >= 5 and random.random() < 0.005:
                    room_data["items"].append("legendary_treasure_box")
