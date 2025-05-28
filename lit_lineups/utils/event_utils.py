"""
Event-related utility functions
"""
import re
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict
from models.constants import EVENTS_DATA
from models.boat import BoatType

def parse_event_requirements(event_name: str) -> Dict:
    """Parse event requirements from event name"""
    boat_class = event_name.split()[-1]
    boat = BoatType(boat_class)
    
    # Determine gender requirements
    gender_req = 'Mixed' if 'Mixed' in event_name else ('M' if 'Men\'s' in event_name else 'F')
    
    # Parse age categories
    age_cats = re.findall(r'\b([A-K]{1,2}(?:-[A-K]{1,2})?)\b', event_name)
    
    return {
        'num_rowers': boat.num_rowers,
        'has_cox': boat.has_cox,
        'is_sculling': boat.is_sculling,
        'gender_req': gender_req,
        'age_categories': age_cats,
        'boat_class': boat_class
    }

def get_event_time(event_num: int, spacing_minutes: int = 4) -> datetime:
    """Calculate event time based on event number and spacing"""
    # Get base time from session state
    base_date = st.session_state.regatta_start_date
    base_time = st.session_state.regatta_start_time
    base_datetime = datetime.combine(base_date, base_time)
    
    # Find which day the event is on
    day_offset = 0
    
    for day, events in EVENTS_DATA.items():
        if any(num == event_num for num, _ in events):
            if day == 'Friday':
                day_offset = 1
            elif day == 'Saturday':
                day_offset = 2
            elif day == 'Sunday':
                day_offset = 3
            
            # Find position within the day
            day_events = [num for num, _ in events]
            position = day_events.index(event_num)
            
            event_time = base_datetime + timedelta(days=day_offset, minutes=position * spacing_minutes)
            return event_time
    
    return base_datetime

def check_time_conflict(event1_num: int, event2_num: int, spacing_minutes: int, min_gap_minutes: int) -> bool:
    """Check if two events have a time conflict"""
    time1 = get_event_time(event1_num, spacing_minutes)
    time2 = get_event_time(event2_num, spacing_minutes)
    
    return abs((time1 - time2).total_seconds() / 60) < min_gap_minutes

def find_event_details(event_num: int):
    """Find event name and day for a given event number"""
    for day, events in EVENTS_DATA.items():
        for num, name in events:
            if num == event_num:
                return name, day
    return None, None