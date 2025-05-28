"""
Schedule view tab UI
"""
import streamlit as st
import pandas as pd
from models.constants import EVENTS_DATA
from utils.event_utils import get_event_time

def render_schedule_tab():
    """Render the schedule view tab"""
    st.header("Full Schedule")
    
    if not st.session_state.lineups:
        st.info("No lineups created yet. Use the Event Lineups tab to create lineups.")
        return
    
    # Group events by day
    for day, events in EVENTS_DATA.items():
        st.subheader(f"📅 {day}")
        
        day_lineups = []
        for event_num, event_name in events:
            if event_num in st.session_state.lineups:
                lineup = st.session_state.lineups[event_num]
                if lineup['athletes'] or lineup['coxswain']:
                    event_time = get_event_time(event_num, st.session_state.event_spacing_minutes)
                    
                    athletes_str = ", ".join([a.name for a in lineup.get('athletes', []) if a is not None])
                    cox_str = f" + Cox: {lineup['coxswain'].name}" if lineup['coxswain'] else ""
                    
                    day_lineups.append({
                        'Time': event_time.strftime("%H:%M"),
                        'Event': f"{event_num}: {event_name}",
                        'Lineup': athletes_str + cox_str
                    })
        
        if day_lineups:
            df = pd.DataFrame(day_lineups)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.write("No lineups scheduled for this day")