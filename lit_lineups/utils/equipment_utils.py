"""
Equipment calculation utilities
"""
from collections import defaultdict
from typing import Dict
from models.constants import EVENTS_DATA

def calculate_equipment_needs(lineups: Dict) -> Dict:
    """Calculate minimum equipment needed"""
    equipment = defaultdict(int)
    
    for event_num, lineup in lineups.items():
        if not lineup.get('athletes'):
            continue
            
        # Find event name
        event_name = None
        for day_events in EVENTS_DATA.values():
            for num, name in day_events:
                if num == event_num:
                    event_name = name
                    break
        
        if not event_name:
            continue
            
        boat_class = event_name.split()[-1]
        
        # Map boat types to equipment categories
        if 'x' in boat_class:  # Sculling
            if '1x' in boat_class:
                equipment['1x (Single Scull)'] += 1
            elif '2x' in boat_class:
                equipment['2x (Double Scull)'] += 1
            elif '4x' in boat_class:
                equipment['4x (Quad Scull)'] += 1
        else:  # Sweep
            if '2' in boat_class:
                if '+' in boat_class:
                    equipment['2+ (Coxed Pair)'] += 1
                else:
                    equipment['2- (Pair)'] += 1
            elif '4' in boat_class:
                if '+' in boat_class:
                    equipment['4+ (Coxed Four)'] += 1
                else:
                    equipment['4- (Four)'] += 1
            elif '8' in boat_class:
                equipment['8+ (Eight)'] += 1
    
    return dict(equipment)