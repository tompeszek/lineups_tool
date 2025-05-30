"""
Schedule view tab UI
"""
import streamlit as st
import pandas as pd
from datetime import timedelta
from models.constants import EVENTS_DATA
from utils.event_utils import get_event_time_both_sessions, get_event_entries_2024, will_event_have_heat

def render_schedule_tab():
    """Render the schedule view tab"""
    st.header("Full Schedule")
    
    if not st.session_state.lineups:
        st.info("No lineups created yet. Use the Event Lineups tab to create lineups.")
        return
    
    # Group events by day
    for day, events in EVENTS_DATA.items():
        st.subheader(f"📅 {day}")
        
        # Create tabs for morning and afternoon sessions
        morning_tab, afternoon_tab = st.tabs(["🌅 Morning (Heats)", "🌇 Afternoon (Finals)"])
        
        with morning_tab:
            _render_session_schedule(day, events, 'morning')
        
        with afternoon_tab:
            _render_session_schedule(day, events, 'afternoon')

def _render_session_schedule(day: str, events: list, session: str):
    """Render schedule for a specific session (morning/afternoon)"""
    day_lineups = []
    
    for event_num, event_name in events:
        if event_num in st.session_state.lineups:
            lineup = st.session_state.lineups[event_num]
            if lineup['athletes'] or lineup['coxswain']:
                # Get times for the specified session
                morning_time, afternoon_time = get_event_time_both_sessions(event_num, st.session_state.event_spacing_minutes)
                event_time = afternoon_time if session == 'afternoon' else morning_time
                
                meet_time = event_time - timedelta(minutes=st.session_state.meet_minutes_before)
                launch_time = event_time - timedelta(minutes=st.session_state.launch_minutes_before)
                land_time = event_time + timedelta(minutes=st.session_state.land_minutes_after)
                
                # Get athlete names
                athletes_list = [a.name for a in lineup.get('athletes', []) if a is not None]
                athletes_str = ", ".join(athletes_list)
                cox_str = f" + Cox: {lineup['coxswain'].name}" if lineup['coxswain'] else ""
                
                # Get boat assignment
                boat_name = "Not assigned"
                boat_status = ""
                if hasattr(st.session_state, 'boat_assignments') and event_num in st.session_state.boat_assignments:
                    boat = st.session_state.boat_assignments[event_num]
                    boat_name = boat.name
                    
                    # Check weight compatibility if we have athletes
                    if athletes_list:
                        athletes = [a for a in lineup.get('athletes', []) if a is not None]
                        avg_weight = sum(a.weight for a in athletes) / len(athletes)
                        weight_check = boat.weight_check(avg_weight)
                        
                        if weight_check == "good":
                            boat_status = " ✅"
                        elif weight_check == "warning":
                            boat_status = " ⚠️"
                        else:
                            boat_status = " ❌"
                
                # Get 2024 entries data
                entries_2024 = get_event_entries_2024(event_num)
                entries_str = str(entries_2024) if entries_2024 is not None else "N/A"
                
                # Check if this event will have a heat
                has_heat = will_event_have_heat(event_num)
                
                # Add session indicator to event name
                if session == 'morning':
                    if has_heat:
                        session_name = "Heat"
                    else:
                        session_name = "Heat - if needed"
                else:
                    session_name = "Final"
                
                day_lineups.append({
                    'Meet': meet_time.strftime("%H:%M"),
                    'Launch': launch_time.strftime("%H:%M"),
                    'Race': event_time.strftime("%H:%M"),
                    'Land': land_time.strftime("%H:%M"),
                    'Event': f"{event_num}: {event_name} ({session_name})",
                    'Entries 2024': entries_str,
                    'Boat': boat_name + boat_status,
                    'Lineup': athletes_str + cox_str
                })
    
    if day_lineups:
        # Sort by race time
        day_lineups.sort(key=lambda x: x['Race'])
        df = pd.DataFrame(day_lineups)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        session_display = "morning heats" if session == 'morning' else "afternoon finals"
        st.write(f"No lineups scheduled for {session_display} on this day")