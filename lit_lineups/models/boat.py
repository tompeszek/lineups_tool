"""
Boat type model and boat fleet management
"""
import re
from typing import List

class BoatType:
    """Original BoatType class for parsing event requirements"""
    def __init__(self, name: str):
        self.name = name
        self.num_rowers = self._extract_num_rowers()
        self.has_cox = self._has_coxswain()
        self.is_sculling = self._is_sculling()
        self.is_sweep = not self.is_sculling
        
    def _extract_num_rowers(self) -> int:
        match = re.search(r'(\d+)', self.name)
        return int(match.group(1)) if match else 1
    
    def _has_coxswain(self) -> bool:
        return '+' in self.name
    
    def _is_sculling(self) -> bool:
        return 'x' in self.name

class Boat:
    """Individual boat with weight specifications and assignment tracking"""
    def __init__(self, name: str, boat_type: str, num_seats: int, min_weight: int, max_weight: int, 
                 manufacturer: str = "", year: int = None, boat_id: int = None, category: str = "Racing"):
        self.name = name
        self.boat_type = boat_type  # e.g., "4+/4x+", "8+", "1x", "2-/2x", etc.
        self.num_seats = num_seats
        self.min_weight = min_weight  # minimum average weight per rower (pounds)
        self.max_weight = max_weight  # maximum average weight per rower (pounds)
        self.manufacturer = manufacturer
        self.year = year
        self.boat_id = boat_id
        self.category = category  # Racing, Training, etc.
        
        # Handle flexible rigging for boats that can be configured both ways
        if '/' in boat_type:
            self.can_be_sculling = True
            self.can_be_sweep = True
            self.is_sculling = False  # Not fixed to either
            self.is_sweep = False     # Not fixed to either
            # Parse cox requirement from either side of the slash
            self.has_cox = '+' in boat_type
        else:
            # Fixed rigging boats
            self.can_be_sculling = 'x' in boat_type
            self.can_be_sweep = '-' in boat_type or ('+' in boat_type and 'x' not in boat_type)
            self.is_sculling = 'x' in boat_type
            self.is_sweep = '-' in boat_type or ('+' in boat_type and 'x' not in boat_type)
            self.has_cox = '+' in boat_type
    
    def weight_check(self, average_weight: float) -> str:
        """Check if average weight is within boat's range"""
        if self.min_weight <= average_weight <= self.max_weight:
            return "good"
        elif average_weight < self.min_weight - 20 or average_weight > self.max_weight + 20:
            return "bad"
        else:
            return "warning"
    
    def is_compatible_with_event(self, event_name: str) -> bool:
        """Check if boat is compatible with an event"""
        from utils.event_utils import parse_event_requirements
        requirements = parse_event_requirements(event_name)
        
        # Check seat count
        if requirements['num_rowers'] != self.num_seats:
            return False
        
        # Check cox requirement
        if requirements['has_cox'] != self.has_cox:
            return False
        
        # Check rigging compatibility - flexible boats can work for either
        if requirements['is_sculling']:
            if not (self.is_sculling or self.can_be_sculling):
                return False
        else:  # sweep
            if not (self.is_sweep or self.can_be_sweep):
                return False
        
        return True

def create_sample_boats():
    """Create the actual SDRC boat fleet"""
    return [
        # Eights
        Boat("La Oaxaca", "8+", 8, 150, 180, "Hudson", 2017, 1, "Racing"),
        Boat("Fuego Nuevo", "8+", 8, 145, 175, "Hudson", 2019, 2, "Racing"),
        Boat("She Shell", "8+", 8, 145, 176, "Hudson", 2022, 3, "Racing"),
        Boat("Azja Czajkowski", "8+", 8, 145, 176, "Hudson", 2025, 4, "Racing"),
        Boat("1888", "8+", 8, 165, 204, "Hudson", 2022, 5, "Racing"),
        Boat("Endeavor II", "8+", 8, 165, 205, "Hudson", 2022, 6, "Racing"),
        Boat("The O'Neill", "8+", 8, 145, 176, "Hudson", 2024, 7, "Racing"),
        Boat("Big Red", "8+", 8, 190, 230, "Hudson", 2019, 8, "Racing"),
        Boat("Pieces of Eight", "8+", 8, 150, 180, "Vespoli", 2018, 9, "Racing"),
        Boat("The Office", "8+", 8, 150, 180, "Vespoli", 2017, 10, "Racing"),
        
        # Coxed Fours (sweep only - cannot be rigged as sculling due to cox seat)
        Boat("MaeAnn", "4+", 4, 115, 145, "Hudson", 2017, 11, "Racing"),
        Boat("Susan Francia", "4+", 4, 150, 180, "Hudson", 2014, 12, "Racing"),
        Boat("Stay Classy", "4+", 4, 145, 175, "Hudson", 2019, 13, "Racing"),
        Boat("Amazing Grace", "4+", 4, 145, 175, "Hudson", 2025, 14, "Racing"),
        Boat("Dodd Wragg", "4+", 4, 165, 195, "Hudson", 2019, 15, "Racing"),
        Boat("Douglas Prescott", "4+", 4, 165, 196, "Hudson", 2022, 16, "Racing"),
        Boat("Honey Badger", "4+", 4, 190, 225, "Hudson", 2018, 17, "Racing"),
        
        # Fours without Cox (can be rigged sweep or scull)
        Boat("Henley", "4-/4x", 4, 115, 145, "Hudson", 2022, 18, "Racing"),
        Boat("The Gwynn", "4-/4x", 4, 145, 180, "Hudson", 2017, 19, "Racing"),
        Boat("Ribose Racer", "4-/4x", 4, 145, 175, "Hudson", 2014, 20, "Racing"),
        Boat("The Kraken", "4-/4x", 4, 145, 175, "Hudson", 2022, 21, "Racing"),
        Boat("Crimson Bear", "4-/4x", 4, 145, 176, "Hudson", 2024, 22, "Racing"),
        Boat("La Vitesse", "4-/4x", 4, 145, 176, "Hudson", 2025, 23, "Racing"),
        Boat("Glenn Schweighardt", "4-/4x", 4, 165, 195, "Hudson", 2022, 24, "Racing"),
        
        # Pairs/Doubles (can be rigged sweep or scull)
        Boat("Tiny Dancer", "2-/2x", 2, 115, 150, "Vespoli", 2013, 25, "Racing"),
        Boat("Betsy's Boat", "2-/2x", 2, 115, 145, "Hudson", 2017, 26, "Racing"),
        Boat("Ninja Princess", "2-/2x", 2, 145, 175, "Hudson", 2019, 27, "Racing"),
        Boat("Double Truble", "2-/2x", 2, 150, 180, "Vespoli", 2018, 28, "Racing"),
        Boat("Truth from Ruth", "2-/2x", 2, 145, 175, "Hudson", 2018, 29, "Racing"),
        Boat("B + F", "2-/2x", 2, 165, 195, "Hudson", 2024, 30, "Racing"),
        Boat("Sean Diggity", "2-/2x", 2, 165, 195, "Hudson", 2022, 31, "Racing"),
        Boat("B'Fast Girl", "2-/2x", 2, 165, 195, "Hudson", 2017, 32, "Racing"),
        # Boat("Old Mike Corr Boat", "2-/2x", 2, 160, 200, "Hudson", 2009, 33, "Racing"),
        Boat("Benjamin Patrick II", "2-/2x", 2, 180, 210, "Vespoli", 2015, 34, "Racing"),
        Boat("Robert E Eikel", "2-/2x", 2, 195, 225, "Hudson", 2021, 35, "Racing"),
                
        # Singles
        Boat("Still I Rise", "1x", 1, 115, 145, "Hudson", 2016, 37, "Racing"),
        Boat("Big Poppa", "1x", 1, 115, 145, "Hudson", 2020, 38, "Racing"),
        Boat("Rob Hibler", "1x", 1, 145, 175, "Hudson", 2015, 39, "Racing"),
        Boat("Notorious RBG", "1x", 1, 145, 175, "Hudson", 2020, 40, "Racing"),
        Boat("Yorick", "1x", 1, 150, 180, "Vespoli", 2013, 41, "Racing"),
        Boat("Red Rose", "1x", 1, 150, 180, "Hudson", 2015, 42, "Racing"),
        Boat("Red Zeppelin", "1x", 1, 150, 180, "Hudson", 2020, 43, "Racing"),
        Boat("Kemper Fidelis", "1x", 1, 180, 210, "Hudson", 2019, 44, "Racing"),
        Boat("Light Speed", "1x", 1, 180, 210, "Hudson", 2020, 45, "Racing"),
        Boat("The Callaghan", "1x", 1, 195, 225, "Hudson", 2020, 46, "Racing"),

        # Personal Boats
        Boat("Peszek", "1x", 1, 198, 220, "Empacher", 2016, 47, "Racing"),
    ]