"""
Session state initialization and management
"""
import streamlit as st
from datetime import datetime, time

def initialize_session_state():
    """Initialize all session state variables"""
    if 'athletes' not in st.session_state:
        st.session_state.athletes = []
    if 'lineups' not in st.session_state:
        st.session_state.lineups = {}
    if 'boats' not in st.session_state:
        st.session_state.boats = []
    if 'boat_assignments' not in st.session_state:
        st.session_state.boat_assignments = {}
    if 'event_spacing_minutes' not in st.session_state:
        st.session_state.event_spacing_minutes = 4
    if 'min_gap_minutes' not in st.session_state:
        st.session_state.min_gap_minutes = 30
    if 'regatta_start_date' not in st.session_state:
        st.session_state.regatta_start_date = datetime(2024, 7, 17).date()
    if 'morning_start_time' not in st.session_state:  # Renamed from regatta_start_time
        st.session_state.morning_start_time = time(8, 0)
    if 'afternoon_start_time' not in st.session_state:  # New parameter
        st.session_state.afternoon_start_time = time(13, 0)  # 1:00 PM default
    if 'exclude_lightweight' not in st.session_state:
        st.session_state.exclude_lightweight = True
    if 'meet_minutes_before' not in st.session_state:
        st.session_state.meet_minutes_before = 40
    if 'launch_minutes_before' not in st.session_state:
        st.session_state.launch_minutes_before = 30
    if 'land_minutes_after' not in st.session_state:
        st.session_state.land_minutes_after = 15
    if 'boats_per_race' not in st.session_state:
        st.session_state.boats_per_race = 8
    
    # Auto-load most recent preset if this is a fresh session
    if 'session_initialized' not in st.session_state:
        st.session_state.session_initialized = True
        from services.data_manager import DataManager
        data_manager = DataManager()
        auto_load_result = data_manager.auto_load_most_recent_preset()
        
        if auto_load_result["success"]:
            st.session_state.auto_load_message = auto_load_result["message"]
        elif "no data" not in auto_load_result["message"].lower():
            # Only show error if it's not just "no data to auto-load"
            st.session_state.auto_load_error = auto_load_result["message"]