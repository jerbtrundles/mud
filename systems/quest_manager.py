# quest_manager.py
from systems.quest import Quest

class QuestManager:
    def __init__(self, game_state):
        """
        Initialize the quest system
        
        Args:
            game_state (GameState): Reference to the game state
        """
        self.game_state = game_state
        self.quests = {}  # All available quests
        self.active_quests = set()  # IDs of active quests
        self.completed_quests = set()  # IDs of completed quests
        self.available_quest_indicator = False  # Whether to show indicators
        
        # Initialize with some basic quests
        self._initialize_quests()
    
    def _initialize_quests(self):
        """Create the initial set of quests"""
        # Starter quest - simple item collection
        self.add_quest(Quest(
            quest_id="beginners_quest",
            name="Adventurer's First Steps",
            description="Gather some basic supplies to start your adventure.",
            tasks=[
                {"type": "collect", "target": "torch", "count": 1},
                {"type": "collect", "target": "healing_potion", "count": 1}
            ],
            rewards={"xp": 10, "coins": 15}
        ))
        
        # Simple kill quest
        self.add_quest(Quest(
            quest_id="goblin_threat",
            name="Goblin Threat",
            description="The local goblins have been causing trouble. Reduce their numbers to make the caves safer.",
            tasks=[
                {"type": "kill", "target": "goblin", "count": 3}
            ],
            rewards={"xp": 25, "coins": 30, "items": {"healing_potion": 1}}
        ))
        
        # Exploration quest
        self.add_quest(Quest(
            quest_id="cave_explorer",
            name="Cave Explorer",
            description="Explore the cave system to map out the area.",
            tasks=[
                {"type": "visit", "target": "cavern"},
                {"type": "visit", "target": "narrow_passage"},
                {"type": "visit", "target": "underground_lake"}
            ],
            rewards={"xp": 20, "coins": 25, "items": {"torch": 1}}
        ))
        
        # Treasure hunt quest
        self.add_quest(Quest(
            quest_id="treasure_hunt",
            name="Treasure Hunter",
            description="Find valuable treasures hidden throughout the caves.",
            tasks=[
                {"type": "collect", "target": "gem", "count": 2},
                {"type": "collect", "target": "common_treasure_box", "count": 1}
            ],
            rewards={"xp": 30, "coins": 50}
        ))
        
        # Advanced quest - requires completion of earlier quests
        self.add_quest(Quest(
            quest_id="hidden_treasure",
            name="The Ancient Treasure",
            description="Legends speak of an ancient treasure guarded by a powerful key.",
            tasks=[
                {"type": "collect", "target": "ancient_key", "count": 1},
                {"type": "visit", "target": "treasure_room"}
            ],
            rewards={"xp": 50, "coins": 100, "items": {"ancient_blade": 1}},
            prereqs=["goblin_threat", "cave_explorer"]
        ))
    
    def add_quest(self, quest):
        """Add a new quest to the system"""
        self.quests[quest.quest_id] = quest
        return quest
    
    def get_quest(self, quest_id):
        """Get a quest by ID"""
        return self.quests.get(quest_id)
    
    def activate_quest(self, quest_id):
        """Activate a quest if possible"""
        quest = self.get_quest(quest_id)
        if not quest:
            return False, f"Quest '{quest_id}' not found."
            
        if quest.completed:
            return False, f"Quest '{quest.name}' is already completed."
            
        if quest.active:
            return False, f"Quest '{quest.name}' is already active."
            
        if not quest.can_activate(self.completed_quests):
            return False, f"You haven't completed the prerequisites for '{quest.name}'."
            
        quest.activate()
        self.active_quests.add(quest_id)
        return True, f"Quest activated: {quest.name}"
    
    # Update the complete_quest method in the QuestManager class
    def complete_quest(self, quest_id):
        """
        Complete a quest and give rewards
        
        Args:
            quest_id (str): ID of the quest to complete
            
        Returns:
            tuple: (success, message)
        """
        quest = self.get_quest(quest_id)
        if not quest:
            return False, f"Quest '{quest_id}' not found."
            
        if not quest.active:
            return False, f"Quest '{quest.name}' is not active."
            
        if not quest.completed:
            return False, f"Quest '{quest.name}' is not completed yet."
            
        # Remove from active quests
        if quest_id in self.active_quests:
            self.active_quests.remove(quest_id)
            
        # Add to completed quests
        self.completed_quests.add(quest_id)
        
        # Give rewards
        reward_text = []
        
        if "xp" in quest.rewards and quest.rewards["xp"] > 0:
            xp = quest.rewards["xp"]
            leveled_up = self.game_state.player.gain_experience(xp)
            reward_text.append(f"{xp} XP")
            
            if leveled_up:
                reward_text.append(f"Level up! You are now level {self.game_state.player.level}!")
                
        if "coins" in quest.rewards and quest.rewards["coins"] > 0:
            coins = quest.rewards["coins"]
            self.game_state.coins += coins
            reward_text.append(f"{coins} coins")
            
            # Update journal for coins earned
            self.game_state.journal.update_stats("coins_earned", coins)
            
        if "items" in quest.rewards:
            for item_name, quantity in quest.rewards["items"].items():
                for _ in range(quantity):
                    self.game_state.player.add_to_inventory(item_name)
                
                from items.item_factory import ItemFactory
                item = ItemFactory.get_item(item_name)
                if item:
                    if quantity > 1:
                        reward_text.append(f"{quantity}x {item.display_name()}")
                    else:
                        reward_text.append(item.display_name())
                
                # Update journal for reward items
                self.game_state.journal.update_stats("items_collected", quantity, item_name)
        
        # Update journal for quest completion
        self.game_state.journal.update_stats("quests_completed", 1)
        self.game_state.journal.add_entry(f"Completed quest: {quest.name}", "achievement")
        
        # Check for quest-based achievements
        if len(self.completed_quests) >= 5:
            self.game_state.journal.add_achievement(
                "Quest Master", 
                "Completed at least 5 quests in your adventure."
            )
        
        # Format the reward message
        if reward_text:
            rewards = ", ".join(reward_text)
            return True, f"Quest '{quest.name}' completed! Rewards: {rewards}"
        else:
            return True, f"Quest '{quest.name}' completed!"
        
    def update_quest_progress(self, event_type, target, location=None, count=1):
        """
        Update progress on active quests based on player actions
        
        Args:
            event_type (str): Type of event (collect, kill, visit, talk)
            target (str): Target of the event (item name, enemy type, location)
            location (str, optional): Location where event happened
            count (int): Number to increment (default 1)
            
        Returns:
            list: List of quests that were updated
        """
        updated_quests = []
        
        for quest_id in self.active_quests:
            quest = self.get_quest(quest_id)
            if not quest:
                continue
                
            if quest.update_progress(event_type, target, location, count):
                updated_quests.append(quest)
                
                # If quest was completed, notify the player
                if quest.completed:
                    self.game_state.add_to_history(f"Quest '{quest.name}' is ready to turn in!", (255, 220, 0))
        
        return updated_quests
    
    def get_available_quests(self):
        """Get quests that can be started but haven't been yet"""
        available = []
        
        for quest_id, quest in self.quests.items():
            if not quest.active and not quest.completed and quest.can_activate(self.completed_quests):
                available.append(quest_id)
                
        return available
    
    def get_active_quests(self):
        """Get currently active quests"""
        return [self.get_quest(quest_id) for quest_id in self.active_quests if self.get_quest(quest_id)]
    
    def get_completed_quests(self):
        """Get completed quests"""
        return [self.get_quest(quest_id) for quest_id in self.completed_quests if self.get_quest(quest_id)]

    def get_quests_for_location(self, location):
        """
        Get quests that are relevant to a specific location
        This could be used for location-specific quest givers in the future
        
        Args:
            location (str): The room name to check
            
        Returns:
            list: List of quests that can be obtained in this location
        """
        # For now, only return available quests if we're at the town square (notice board)
        if location == "town_square":
            return self.get_available_quests()
        return []
