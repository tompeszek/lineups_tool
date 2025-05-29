"""
Athlete model and related functionality
"""
import re
from typing import List
from .constants import AGE_CATEGORIES

class Athlete:
    def __init__(self, name: str, gender: str, age: int, weight: int = 160, can_port: bool = True, 
                 can_starboard: bool = True, can_scull: bool = True, can_cox: bool = False,
                 preferred_events: List[str] = None, available_days: List[str] = None):
        self.name = name
        self.gender = gender
        self.age = age
        self.weight = weight  # weight in pounds
        self.can_port = can_port
        self.can_starboard = can_starboard
        self.can_scull = can_scull
        self.can_cox = can_cox
        self.preferred_events = preferred_events or []
        self.available_days = available_days or ['Thursday', 'Friday', 'Saturday', 'Sunday']
        self.age_category = self._get_age_category()
    
    def _get_age_category(self) -> str:
        for cat, (min_age, max_age) in AGE_CATEGORIES.items():
            if min_age <= self.age <= max_age:
                return cat
        return 'K'  # Default to oldest category
    
    def is_available_on_day(self, day: str) -> bool:
        """Check if athlete is available on a specific day"""
        return day in self.available_days
    
    def fits_event(self, event_name: str) -> bool:
        """Check if athlete fits basic requirements for an event"""
        from .boat import BoatType
        
        # Gender check
        if 'Men\'s' in event_name and self.gender != 'M':
            return False
        if 'Women\'s' in event_name and self.gender != 'F':
            return False
        
        # Age category check
        age_cats_in_event = re.findall(r'\b([A-K]{1,2})\b', event_name)
        if age_cats_in_event:
            valid_cats = []
            for cat_group in age_cats_in_event:
                if '-' in cat_group:
                    start, end = cat_group.split('-')
                    cat_keys = list(AGE_CATEGORIES.keys())
                    start_idx = cat_keys.index(start) if start in cat_keys else 0
                    end_idx = cat_keys.index(end) if end in cat_keys else len(cat_keys) - 1
                    valid_cats.extend(cat_keys[start_idx:end_idx + 1])
                else:
                    valid_cats.append(cat_group)
            
            if valid_cats and self.age_category not in valid_cats:
                return False
        
        # Boat type compatibility
        boat = BoatType(event_name.split()[-1])
        if boat.is_sculling and not self.can_scull:
            return False
        if boat.is_sweep and not (self.can_port or self.can_starboard):
            return False
            
        return True

def create_sample_roster():
    """Create a sample roster of athletes with weights"""
    # P - S - X - C
    return [
        # Yeses
        Athlete("Tom Peszek", "M", 40, 205, False, True, True, False, [385,230,292,315,243,183,158,160], ['Thursday', 'Friday', 'Saturday', 'Sunday']), # not in 300 (b8+)
        Athlete("Dmitriy Yakubov", "M", 35, 190, True, True, True, False, [243,222,300, 362], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Weronika Yakubov", "F", 29, 135, True, True, True, False, [222], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Mabel Gomes", "F", 43, 145, False, True, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Shane Farmer", "M", 40, 190, True, False, False, False, [385,230, 243,300, 362], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Doug Brayton", "M", 43, 190, True, True, True, False, [385,230, 243, 284,300, 362], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Kathy Hughes", "F", 72, 150, True, True, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Susan Minkema", "F", 65, 155, False, False, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Donna Pili", "F", 54, 142, True, True, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Mary Kaleta", "F", 40, 140, True, True, True, False, [183, 204, 284, 340], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Christine Flowers", "F", 63, 148, True, True, True, False, [225], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Jan de Jong", "M", 64, 165, True, True, True, False, [], ['Friday', 'Saturday', 'Sunday']),        
        Athlete("Will Bastien", "M", 40, 170, False, True, True, False, [385,230, 243,300, 362], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Caitlin Turner", "F", 35, 125, False, False, False, True, [230, 243], ['Thursday', 'Friday', 'Saturday', 'Sunday']),        
        Athlete("Aimee Wessel", "F", 56, 138, True, False, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Hunter Butler", "M", 70, 160, True, True, True, False, [180, 266], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        
        # Maybes
        Athlete("Elizabeth Hale", "F", 56, 160, True, False, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),        
        Athlete("Tara Mallis", "F", 42, 160, True, True, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Julie Talbot", "F", 26, 160, False, True, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Ellen Minteer", "F", 58, 160, True, True, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Susan Gjerset", "F", 71, 138, True, False, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Mary Ewing", "F", 56, 138, True, True, True, False, [], ['Saturday', 'Sunday']),
        Athlete("Ralph Johnson", "M", 77, 160, True, True, True, False, [180, 266], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Seth Burns", "M", 58, 175, True, False, True, False, [355, 254, 266], ['Friday', 'Saturday', 'Sunday']),
        Athlete("Curt Mazur", "M", 62, 175, True, True, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),

        ## Doubtfuls
        Athlete("Sasha Foster", "F", 53, 138, False, True, True, False, [], ['Thursday', 'Friday', 'Saturday', 'Sunday']),

        ## Unlisted maybes
        Athlete("Glynn Bolitho", "M", 60, 190, True, True, True, False, [355, 254, 266], ['Thursday', 'Friday', 'Saturday', 'Sunday']), # guessing everything

        # Out
        #Athlete("Lisa Roth", "F", 66, 130, True, True, True, True, [385], ['Thursday', 'Friday', 'Saturday', 'Sunday']),

        # Ringers
        Athlete("Stephen Kasprzyk", "M", 43, 210, False, True, False, False, [243, 300], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Donna Peszek", "F", 69, 140, True, True, True, False, [158, 183], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
        Athlete("Larry Peszek", "M", 71, 175, True, True, True, False, [292, 183], ['Thursday', 'Friday', 'Saturday', 'Sunday']),
    ]