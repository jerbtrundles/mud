# enemy.py
import random
import time

class Enemy:
    def __init__(self, name, health, attack, experience, allowed_rooms, respawn_delay=60, special_attacks=None):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.experience = experience
        self.allowed_rooms = allowed_rooms
        self.current_room = random.choice(allowed_rooms)
        self.last_move_time = time.time()
        self.death_time = None
        self.respawn_delay = respawn_delay  # seconds until respawn after death
        self.special_attacks = special_attacks or {}
    
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health == 0 and self.death_time is None:
            self.death_time = time.time()
        return amount
    
    def is_alive(self):
        return self.health > 0
    
    def move(self):
        """Move enemy to a random room within its allowed rooms"""
        if len(self.allowed_rooms) > 1 and self.is_alive():
            # Choose a different room than the current one
            new_room = random.choice([room for room in self.allowed_rooms if room != self.current_room])
            self.current_room = new_room
            return True
        return False
    
    def check_respawn(self):
        """Check if it's time to respawn this enemy"""
        if not self.is_alive() and self.death_time is not None:
            current_time = time.time()
            if current_time - self.death_time >= self.respawn_delay:
                self.respawn()
                return True
        return False
    
    def respawn(self):
        """Respawn the enemy"""
        self.health = self.max_health
        self.current_room = random.choice(self.allowed_rooms)
        self.death_time = None
        return True