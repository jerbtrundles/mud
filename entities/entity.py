# entities/entity.py
"""
Base entity class for all living beings in the game.
"""

from core.game_object import GameObject

class Entity(GameObject):
    """Base class for all living entities in the game"""
    
    def __init__(self, name, description, health=10, attack=1, defense=0, level=1, **kwargs):
        """
        Initialize a base entity
        
        Args:
            name (str): Entity's internal name
            description (str): Entity description
            health (int): Starting/maximum health
            attack (int): Base attack power
            defense (int): Base defense
            level (int): Entity level
            **kwargs: Additional attributes
        """
        super().__init__(name, description, **kwargs)
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.level = level
        self.is_alive_flag = True
        self.experience = level * 5  # Default XP value
        self.initiative_bonus = 0  # Used for combat turn order
        
        # Status effect tracking
        self.status_effects = {}  # {effect_name: effect_obj}
        
        # Add base entity tag
        self.add_tag("entity")
    
    def is_alive(self):
        """Check if entity is alive"""
        return self.health > 0 and self.is_alive_flag
    
    def heal(self, amount):
        """
        Heal the entity
        
        Args:
            amount (int): Amount of health to restore
            
        Returns:
            int: Actual amount healed
        """
        if not self.is_alive():
            return 0
            
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - old_health
    
    def take_damage(self, amount):
        """
        Apply damage to the entity
        
        Args:
            amount (int): Amount of damage to apply
            
        Returns:
            int: Actual damage taken
        """
        if not self.is_alive():
            return 0
            
        # Apply defense reduction (if applicable)
        actual_damage = max(1, amount - self.get_defense())
        old_health = self.health
        self.health = max(0, self.health - actual_damage)
        
        # Check for death
        if self.health <= 0:
            self._on_death()
            
        return min(old_health, actual_damage)  # Can't take more damage than current health
    
    def _on_death(self):
        """Handle death event - to be overridden"""
        self.is_alive_flag = False
    
    def get_attack(self):
        """Get total attack power including equipment and status effects"""
        total_attack = self.attack
        
        # Add bonuses from status effects
        for effect in self.status_effects.values():
            if hasattr(effect, 'attack_modifier'):
                total_attack += effect.attack_modifier
        
        return max(0, total_attack)
    
    def get_defense(self):
        """Get total defense including equipment and status effects"""
        total_defense = self.defense
        
        # Add bonuses from status effects
        for effect in self.status_effects.values():
            if hasattr(effect, 'defense_modifier'):
                total_defense += effect.defense_modifier
        
        return max(0, total_defense)
    
    def add_status_effect(self, effect):
        """
        Add a status effect to this entity
        
        Args:
            effect: The status effect to add
            
        Returns:
            bool: True if added, False if replaced
        """
        # Check if already affected by this type
        if effect.name in self.status_effects:
            existing = self.status_effects[effect.name]
            
            # If new effect is stronger, replace
            if effect.strength > existing.strength:
                self.status_effects[effect.name] = effect
                effect.apply_initial(self)
                return False
            
            # If new effect lasts longer, extend duration
            if effect.get_time_remaining() > existing.get_time_remaining():
                existing.duration = effect.duration
                existing.start_time = effect.start_time
                return False
            
            # Otherwise do nothing
            return False
        
        # Apply new effect
        self.status_effects[effect.name] = effect
        effect.apply_initial(self)
        return True
    
    def remove_status_effect(self, effect_name):
        """
        Remove a status effect
        
        Args:
            effect_name: Name of effect to remove
            
        Returns:
            bool: True if removed
        """
        if effect_name in self.status_effects:
            effect = self.status_effects[effect_name]
            effect.apply_removal(self)
            del self.status_effects[effect_name]
            return True
        return False
    
    def update_status_effects(self, current_time):
        """
        Update all status effects
        
        Args:
            current_time: Current game time
        """
        effects_to_remove = []
        
        for name, effect in self.status_effects.items():
            # Check if effect has expired
            if effect.is_expired(current_time):
                effects_to_remove.append(name)
                continue
            
            # Apply effect tick
            effect.apply_tick(self, current_time)
        
        # Remove expired effects
        for name in effects_to_remove:
            self.remove_status_effect(name)
    
    def get_health_percentage(self):
        """Get current health as a percentage of max health"""
        if self.max_health <= 0:
            return 0
        return self.health / self.max_health
    
    def to_dict(self):
        """Convert entity to dictionary for serialization"""
        data = super().to_dict()
        data.update({
            "health": self.health,
            "max_health": self.max_health,
            "attack": self.attack,
            "defense": self.defense,
            "level": self.level,
            "is_alive": self.is_alive_flag,
            "experience": self.experience,
            "initiative_bonus": self.initiative_bonus
        })
        
        # Serialize status effects
        status_effects = {}
        for name, effect in self.status_effects.items():
            if hasattr(effect, 'to_dict'):
                status_effects[name] = effect.to_dict()
        
        if status_effects:
            data["status_effects"] = status_effects
            
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create an entity from dictionary data"""
        # Create basic entity
        entity = cls(
            name=data["name"],
            description=data["description"],
            health=data["max_health"],
            attack=data["attack"],
            defense=data["defense"],
            level=data["level"]
        )
        
        # Set additional properties
        entity.health = data["health"]
        entity.is_alive_flag = data.get("is_alive", True)
        entity.experience = data.get("experience", entity.level * 5)
        entity.initiative_bonus = data.get("initiative_bonus", 0)
        
        # Restore tags
        for tag in data.get("tags", []):
            entity.add_tag(tag)
        
        # Restore any attributes
        for key, value in data.get("attributes", {}).items():
            setattr(entity, key, value)
        
        # Restore status effects (requires separate StatusEffect module)
        if "status_effects" in data and hasattr(entity, 'add_status_effect'):
            for effect_name, effect_data in data["status_effects"].items():
                # This assumes there's a function to create effects from data
                # Would be implemented in the StatusEffect module
                pass
        
        return entity