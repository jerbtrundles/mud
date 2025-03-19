# quest.py
class Quest:
    def __init__(self, quest_id, name, description, tasks, rewards, prereqs=None):
        """
        Initialize a new quest
        
        Args:
            quest_id (str): Unique identifier for this quest
            name (str): Display name of the quest
            description (str): Detailed description of the quest
            tasks (list): List of task dictionaries defining completion requirements
            rewards (dict): Rewards given when quest is completed
            prereqs (list, optional): List of quest IDs that must be completed first
        """
        self.quest_id = quest_id
        self.name = name
        self.description = description
        self.tasks = tasks  # [{type: "collect", target: "gem", count: 3}, {type: "kill", target: "goblin", count: 5}]
        self.rewards = rewards  # {"xp": 50, "coins": 100, "items": {"healing_potion": 2}}
        self.prereqs = prereqs or []
        
        # State tracking
        self.active = False
        self.completed = False
        self.progress = {}  # Will track progress on each task
        
        # Initialize progress counters for each task
        for task in self.tasks:
            if task.get("count", 1) > 1:
                self.progress[self._get_task_key(task)] = 0
    
    def _get_task_key(self, task):
        """Generate a unique key for a task for progress tracking"""
        task_type = task["type"]
        target = task.get("target", "")
        location = task.get("location", "")
        return f"{task_type}:{target}:{location}"
    
    def can_activate(self, completed_quests):
        """Check if this quest's prerequisites are met"""
        if not self.prereqs:
            return True
        return all(quest_id in completed_quests for quest_id in self.prereqs)
    
    def activate(self):
        """Mark the quest as active"""
        self.active = True
        return True
    
    def update_progress(self, event_type, target, location=None, count=1):
        """
        Update progress on a quest based on player actions
        
        Args:
            event_type (str): Type of event (collect, kill, visit, talk)
            target (str): Target of the event (item name, enemy type, location)
            location (str, optional): Location where event happened
            count (int): Number to increment (default 1)
            
        Returns:
            bool: True if any progress was made, False otherwise
        """
        if not self.active or self.completed:
            return False
        
        made_progress = False
        
        for task in self.tasks:
            if task["type"] != event_type:
                continue
                
            # Check if this action matches this task
            if "target" in task and task["target"] != target:
                continue
                
            # Check location constraint if specified
            if "location" in task and location and task["location"] != location:
                continue
            
            # Match found - update progress
            task_key = self._get_task_key(task)
            required_count = task.get("count", 1)
            
            if required_count == 1:
                # Simple completion task (no counter)
                self.progress[task_key] = True
                made_progress = True
            else:
                # Increment counter
                if task_key not in self.progress:
                    self.progress[task_key] = 0
                
                self.progress[task_key] = min(required_count, self.progress[task_key] + count)
                made_progress = True
        
        # Check if quest is now complete
        self._check_completion()
        
        return made_progress
    
    def _check_completion(self):
        """Check if all tasks are completed"""
        if self.completed:
            return True
            
        all_complete = True
        
        for task in self.tasks:
            task_key = self._get_task_key(task)
            required_count = task.get("count", 1)
            
            if required_count == 1:
                # Simple completion task
                if task_key not in self.progress or not self.progress[task_key]:
                    all_complete = False
                    break
            else:
                # Counter task
                if task_key not in self.progress or self.progress[task_key] < required_count:
                    all_complete = False
                    break
        
        self.completed = all_complete
        return all_complete
    
    def get_task_progress(self):
        """Get formatted progress for all tasks"""
        progress_text = []
        
        for task in self.tasks:
            task_key = self._get_task_key(task)
            required_count = task.get("count", 1)
            
            # Format based on task type
            if task["type"] == "kill":
                description = f"Defeat {required_count}x {task['target'].replace('_', ' ')}"
            elif task["type"] == "collect":
                description = f"Collect {required_count}x {task['target'].replace('_', ' ')}"
            elif task["type"] == "visit":
                description = f"Visit {task['target'].replace('_', ' ')}"
            elif task["type"] == "talk":
                description = f"Talk to {task['target'].replace('_', ' ')}"
            else:
                description = f"{task['type'].capitalize()} {task['target'].replace('_', ' ')}"
            
            # Add location if specified
            if "location" in task:
                description += f" in {task['location'].replace('_', ' ')}"
            
            # Add progress
            if required_count == 1:
                status = "✓" if task_key in self.progress and self.progress[task_key] else "□"
                progress_text.append(f"{status} {description}")
            else:
                current = self.progress.get(task_key, 0)
                status = "✓" if current >= required_count else f"{current}/{required_count}"
                progress_text.append(f"[{status}] {description}")
        
        return progress_text
    
    def get_rewards_text(self):
        """Get formatted text describing rewards"""
        reward_texts = []
        
        if "xp" in self.rewards and self.rewards["xp"] > 0:
            reward_texts.append(f"{self.rewards['xp']} XP")
            
        if "coins" in self.rewards and self.rewards["coins"] > 0:
            reward_texts.append(f"{self.rewards['coins']} coins")
            
        if "items" in self.rewards:
            from items.item_factory import ItemFactory
            for item_name, quantity in self.rewards["items"].items():
                item = ItemFactory.get_item(item_name)
                if item:
                    if quantity > 1:
                        reward_texts.append(f"{quantity}x {item.display_name()}")
                    else:
                        reward_texts.append(item.display_name())
                else:
                    reward_texts.append(f"{quantity}x {item_name.replace('_', ' ')}")
        
        return reward_texts
    
    def get_status(self):
        """Get the quest status (not started, in progress, complete)"""
        if self.completed:
            return "complete"
        elif self.active:
            return "active"
        else:
            return "inactive"
