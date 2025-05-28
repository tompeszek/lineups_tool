"""
Boat type model and related functionality
"""
import re

class BoatType:
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