import streamlit as st
import os
from datetime import datetime
from debug_utils import enable_debugging
from ui.roster_tab import render_roster_tab
from ui.lineup_tab import render_lineup_tab
from ui.schedule_tab import render_schedule_tab
from ui.athlete_tab import render_athlete_tab
from ui.equipment_tab import render_equipment_tab
from ui.data_tab import render_data_tab  # Add this import
from models.session_state import initialize_session_state

# Set page config for wide layout
st.set_page_config(
    page_title="Rowing Lineup Management",
    page_icon="🚣",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enable debugging in development
if os.getenv("STREAMLIT_DEBUG", "false").lower() == "true":
    enable_debugging()

# Initialize session state
initialize_session_state()

# Main UI
st.title("Rowing Lineup Management")

# Sidebar for parameters
st.sidebar.header("⚙️ Parameters")

st.sidebar.subheader("Event Filtering")
st.session_state.exclude_lightweight = st.sidebar.checkbox(
    "Exclude Lightweight Events",
    value=st.session_state.exclude_lightweight,
    help="Filter out events with 'ltwt' in the name"
)

st.sidebar.subheader("Regatta Schedule")
st.session_state.regatta_start_date = st.sidebar.date_input(
    "Start Date (Thursday)",
    value=st.session_state.regatta_start_date
)

st.session_state.regatta_start_time = st.sidebar.time_input(
    "Start Time",
    value=st.session_state.regatta_start_time
)

st.sidebar.subheader("Athlete Timing")
st.session_state.meet_minutes_before = st.sidebar.number_input(
    "Minutes before race to meet", 
    min_value=15, 
    max_value=90, 
    value=st.session_state.meet_minutes_before
)

st.session_state.launch_minutes_before = st.sidebar.number_input(
    "Minutes before race to launch", 
    min_value=10, 
    max_value=60, 
    value=st.session_state.launch_minutes_before
)

st.sidebar.subheader("Event Timing")
st.session_state.event_spacing_minutes = st.sidebar.number_input(
    "Event Spacing (minutes)", 
    min_value=1, 
    max_value=10, 
    value=st.session_state.event_spacing_minutes
)

st.session_state.min_gap_minutes = st.sidebar.number_input(
    "Minimum Gap Between Events (minutes)", 
    min_value=15, 
    max_value=120, 
    value=st.session_state.min_gap_minutes
)

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💾 Data Management",  # Moved to first
    "📋 Roster Management", 
    "🏁 Event Lineups", 
    "📅 Schedule View", 
    "👤 Athlete View", 
    "⛵ Equipment"
])

with tab1:
    render_data_tab()  # Now first

with tab2:
    render_roster_tab()

with tab3:
    render_lineup_tab()

with tab4:
    render_schedule_tab()

with tab5:
    render_athlete_tab()

with tab6:
    render_equipment_tab()