# autosave.py
# AutosaveSettings for save_load.py
import time
import os
from core.utils import ensure_dir_exists, format_time_delta

class AutosaveSettings:
    """Global settings for autosave functionality"""
    last_autosave_time = time.time()
    autosave_interval = 300  # 5 minutes (in seconds)
    backup_interval = 3600   # 1 hour (in seconds)
    enabled = True
    max_slots = 3
    autosave_dir = "saves/autosaves"
    
    @classmethod
    def initialize(cls):
        """Initialize autosave system, creating necessary directories"""
        ensure_dir_exists(cls.autosave_dir)
        return cls
    
    @classmethod
    def toggle(cls, enable=None):
        """
        Toggle or set autosave functionality
        
        Args:
            enable (bool, optional): If provided, set to this value; if None, toggle current value
            
        Returns:
            bool: The new enabled state
        """
        if enable is None:
            cls.enabled = not cls.enabled
        else:
            cls.enabled = bool(enable)
        return cls.enabled
    
    @classmethod
    def set_interval(cls, minutes):
        """
        Set autosave interval in minutes
        
        Args:
            minutes (int): Minutes between autosaves
            
        Returns:
            int: The new interval in seconds
        """
        # Limit to reasonable values
        if minutes < 1:
            minutes = 1
        elif minutes > 60:
            minutes = 60
            
        cls.autosave_interval = minutes * 60
        return cls.autosave_interval
    
    @classmethod
    def get_next_slot(cls):
        """
        Get the next autosave slot number
        
        Returns:
            int: Slot number (1 to max_slots)
        """
        slot = int((time.time() // cls.autosave_interval) % cls.max_slots) + 1
        return slot
    
    @classmethod
    def get_autosave_filename(cls, slot=None):
        """
        Get the filename for an autosave slot
        
        Args:
            slot (int, optional): Slot number, or None for next slot
            
        Returns:
            str: Autosave filename
        """
        if slot is None:
            slot = cls.get_next_slot()
            
        return os.path.join(cls.autosave_dir, f"autosave_{slot}.json")
    
    @classmethod
    def get_backup_filename(cls):
        """
        Get a unique backup filename with timestamp
        
        Returns:
            str: Backup filename
        """
        from core.utils import get_timestamp
        return os.path.join(cls.autosave_dir, f"backup_{get_timestamp()}.json")
    
    @classmethod
    def should_autosave(cls, current_time=None):
        """
        Check if it's time to perform an autosave
        
        Args:
            current_time (float, optional): Current time, or None to use time.time()
            
        Returns:
            bool: True if autosave should be performed
        """
        if not cls.enabled:
            return False
            
        if current_time is None:
            current_time = time.time()
            
        return (current_time - cls.last_autosave_time) >= cls.autosave_interval
    
    @classmethod
    def should_backup(cls, current_time=None):
        """
        Check if it's time to perform a backup
        
        Args:
            current_time (float, optional): Current time, or None to use time.time()
            
        Returns:
            bool: True if backup should be performed
        """
        if not cls.enabled:
            return False
            
        if current_time is None:
            current_time = time.time()
            
        return (current_time - cls.last_autosave_time) >= cls.backup_interval
    
    @classmethod
    def mark_saved(cls, current_time=None):
        """
        Mark the current time as the last autosave time
        
        Args:
            current_time (float, optional): Current time, or None to use time.time()
        """
        if current_time is None:
            current_time = time.time()
            
        cls.last_autosave_time = current_time
    
    @classmethod
    def get_status(cls):
        """
        Get the current status of autosave functionality
        
        Returns:
            dict: Status information
        """
        current_time = time.time()
        next_save_time = cls.last_autosave_time + cls.autosave_interval if cls.enabled else None
        time_until_next = max(0, next_save_time - current_time) if next_save_time else None
        
        return {
            "enabled": cls.enabled,
            "interval_seconds": cls.autosave_interval,
            "interval_text": format_time_delta(cls.autosave_interval),
            "next_save_time": next_save_time,
            "time_until_next": time_until_next,
            "time_until_next_text": format_time_delta(time_until_next) if time_until_next else "N/A",
            "last_save_time": cls.last_autosave_time,
            "next_slot": cls.get_next_slot()
        }