"""
Event-related utility functions
"""
import re
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict
from models.constants import EVENTS_DATA, ROWFEST_2024_ENTRIES
from models.boat import BoatType

@st.cache_data
def normalize_event_name(event_name: str) -> str:
    """Normalize event name for matching by removing variations"""
    normalized = event_name.lower()
    
    # Remove apostrophes from possessives (men's -> mens, women's -> womens)
    normalized = normalized.replace("'s", "s")
    
    # Remove "masters" and "master" completely
    normalized = re.sub(r'\bmasters?\b', '', normalized)
    
    # Clean up extra spaces
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized

# @st.cache_data
def extract_event_features(event_name: str) -> dict:
    """Extract key features from event name for matching"""
    original_lower = event_name.lower()
    
    # Extract gender
    if 'mixed' in original_lower:
        gender = 'mixed'
    elif 'women' in original_lower:
        gender = 'women'
    else:
        gender = 'men'
    
    # Extract Paralympic class
    paralympic_class = None
    if 'pr1' in original_lower:
        paralympic_class = 'pr1'
    elif 'pr2' in original_lower:
        paralympic_class = 'pr2'
    elif 'pr3' in original_lower:
        paralympic_class = 'pr3'
    
    # Extract boat class
    boat_class_match = re.search(r'(\d+[x\-+]|1x|2-|4\+|8\+|4-|2\+|4x|8x)', original_lower)
    boat_class = boat_class_match.group(1) if boat_class_match else None
    
    # Extract age categories - just split and find single letters
    age_categories = []
    words = original_lower.replace("'s", "").replace("masters", "").replace("master", "").split()
    for word in words:
        if len(word) == 1 and word.isalpha() and word in 'abcdefghijk':
            age_categories.append(word.upper())
        elif '-' in word and len(word) == 3:  # like "a-d"
            parts = word.split('-')
            if len(parts) == 2 and all(len(p) == 1 and p.isalpha() and p in 'abcdefghijk' for p in parts):
                age_categories.append(word.upper())
    
    age_categories = sorted(set(age_categories))
    
    # Event types
    is_club = 'club' in original_lower
    is_open = 'open' in original_lower
    is_lightweight = 'ltwt' in original_lower or 'lightweight' in original_lower
    
    return {
        'boat_class': boat_class,
        'gender': gender,
        'age_categories': age_categories,
        'is_club': is_club,
        'is_open': is_open,
        'paralympic_class': paralympic_class,
        'is_lightweight': is_lightweight
    }

# @st.cache_data
def events_match(event_name_1: str, event_name_2: str) -> bool:
    """Check if two event names refer to the same event"""
    features_1 = extract_event_features(event_name_1)
    features_2 = extract_event_features(event_name_2)
    
    # Must match exactly on all key features
    return (features_1['boat_class'] == features_2['boat_class'] and
            features_1['gender'] == features_2['gender'] and
            features_1['age_categories'] == features_2['age_categories'] and
            features_1['is_club'] == features_2['is_club'] and
            features_1['is_open'] == features_2['is_open'] and
            features_1['paralympic_class'] == features_2['paralympic_class'] and
            features_1['is_lightweight'] == features_2['is_lightweight'])

@st.cache_data
def get_event_entries_2024(event_num: int):
    """Get the number of entries for an event from RowFest 2024 data using name matching only"""
    # Find current event name
    current_event_name = None
    for day, events in EVENTS_DATA.items():
        for num, name in events:
            if num == event_num:
                current_event_name = name
                break
        if current_event_name:
            break
    
    if not current_event_name:
        return None
    
    # Search for matching event in 2024 data by name features only
    for day, events in ROWFEST_2024_ENTRIES.items():
        for num, name, entries in events:
            if events_match(current_event_name, name):
                return entries
    
    return None

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

@st.cache_data
def get_event_time(event_num: int, spacing_minutes: int = 4, session: str = 'morning') -> datetime:
    """Calculate event time based on event number, spacing, and session with race delays"""
    # Get base time from session state
    base_date = st.session_state.regatta_start_date
    
    # Choose morning or afternoon start time
    if session == 'afternoon':
        base_time = st.session_state.afternoon_start_time
    else:
        base_time = st.session_state.morning_start_time
    
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
            
            # Calculate cumulative time delay from previous events
            day_events = [num for num, _ in events]
            target_position = day_events.index(event_num)
            
            cumulative_delay = 0
            for i in range(target_position):
                prev_event_num = day_events[i]
                entries_2024 = get_event_entries_2024(prev_event_num)
                
                if entries_2024 is not None and entries_2024 > st.session_state.boats_per_race:
                    # This event needed multiple races, causing extra delay
                    races_needed = (entries_2024 + st.session_state.boats_per_race - 1) // st.session_state.boats_per_race
                    extra_delay = (races_needed - 1) * spacing_minutes
                    cumulative_delay += extra_delay
            
            # Calculate final event time
            base_time_with_day = base_datetime + timedelta(days=day_offset)
            position_delay = target_position * spacing_minutes
            total_delay = position_delay + cumulative_delay
            
            event_time = base_time_with_day + timedelta(minutes=total_delay)
            return event_time
    
    return base_datetime

def get_event_time_both_sessions(event_num: int, spacing_minutes: int = 4) -> tuple:
    """Get both morning and afternoon times for an event"""
    morning_time = get_event_time(event_num, spacing_minutes, 'morning')
    afternoon_time = get_event_time(event_num, spacing_minutes, 'afternoon')
    return morning_time, afternoon_time

def check_time_conflict(event1_num: int, event2_num: int, spacing_minutes: int, min_gap_minutes: int, session: str = 'morning') -> bool:
    """Check if two events have a time conflict in the specified session"""
    time1 = get_event_time(event1_num, spacing_minutes, session)
    time2 = get_event_time(event2_num, spacing_minutes, session)
    
    return abs((time1 - time2).total_seconds() / 60) < min_gap_minutes

def find_event_details(event_num: int):
    """Find event name and day for a given event number"""
    for day, events in EVENTS_DATA.items():
        for num, name in events:
            if num == event_num:
                return name, day
    return None, None

@st.cache_data
def will_event_have_heat(event_num: int) -> bool:
    """Determine if an event will have a heat based on 2024 entries"""
    entries_2024 = get_event_entries_2024(event_num)
    if entries_2024 is None:
        return True  # Default to having heat if we don't have data
    return entries_2024 > st.session_state.boats_per_race