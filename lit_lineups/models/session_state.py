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
    if 'regatta_start_time' not in st.session_state:
        st.session_state.regatta_start_time = time(8, 0)
    if 'exclude_lightweight' not in st.session_state:
        st.session_state.exclude_lightweight = True
    if 'meet_minutes_before' not in st.session_state:
        st.session_state.meet_minutes_before = 40
    if 'launch_minutes_before' not in st.session_state:
        st.session_state.launch_minutes_before = 30
    if 'land_minutes_after' not in st.session_state:
        st.session_state.land_minutes_after = 15  # New parameter for when boats land after racing