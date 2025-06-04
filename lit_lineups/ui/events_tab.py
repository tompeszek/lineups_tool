"""
Event planning tab UI for tracking event entry status - compact grid layout
"""
import streamlit as st
from models.constants import EVENTS_DATA

def render_event_planning_tab():
    """Render the event planning tab for tracking event entry decisions"""
    st.header("Event Planning")
    
    # Initialize event statuses if needed
    if 'event_statuses' not in st.session_state:
        st.session_state.event_statuses = {}
    
    # Compact legend
    st.markdown("**🟢** Athlete Requested • **🟡** Coaches Suggested • **🟣** Contingent • Click to change status")
    
    # Filter events by eligibility
    filtered_events_by_day = {}
    for day, events in EVENTS_DATA.items():
        filtered_events = []
        for event_num, event_name in events:
            if _should_show_event_for_planning(event_name):
                filtered_events.append((event_num, event_name))
        if filtered_events:
            filtered_events_by_day[day] = filtered_events
    
    if not filtered_events_by_day:
        st.warning("No eligible events found!")
        return
    
    # Create grid layout using CSS
    st.markdown("""
    <style>
    .event-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin: 20px 0;
    }
    .day-column {
        border: 1px solid #ddd;
        border-radius: 5px;
        overflow: hidden;
    }
    .day-header {
        background-color: #f0f2f6;
        padding: 10px;
        font-weight: bold;
        text-align: center;
        border-bottom: 1px solid #ddd;
    }
    .event-item {
        padding: 8px;
        border-bottom: 1px solid #eee;
        cursor: pointer;
        font-size: 12px;
        line-height: 1.3;
    }
    .event-item:last-child {
        border-bottom: none;
    }
    .event-item:hover {
        background-color: #f8f9fa;
    }
    .status-athlete { background-color: #4CAF50; color: white; }
    .status-coaches { background-color: #FFC107; color: black; }
    .status-contingent { background-color: #9C27B0; color: white; }
    .status-none { background-color: transparent; }
    .event-num { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
    
    # Create the grid HTML
    grid_html = '<div class="event-grid">'
    
    for day, events in filtered_events_by_day.items():
        grid_html += f'''
        <div class="day-column">
            <div class="day-header">{day}<br><small>({len(events)} events)</small></div>
        '''
        
        for event_num, event_name in events:
            current_status = st.session_state.event_statuses.get(event_num, "none")
            status_class = f"status-{current_status.replace('_', '-')}"
            
            # Shorten event name for display
            display_name = event_name.replace("Men's ", "M ").replace("Women's ", "W ").replace("Mixed ", "X ")
            if len(display_name) > 35:
                display_name = display_name[:32] + "..."
            
            grid_html += f'''
            <div class="event-item {status_class}" onclick="changeEventStatus({event_num})">
                <span class="event-num">{event_num}</span><br>
                {display_name}
            </div>
            '''
        
        grid_html += '</div>'
    
    grid_html += '</div>'
    
    # Display the grid
    st.markdown(grid_html, unsafe_allow_html=True)
    
    # JavaScript for handling clicks
    st.markdown("""
    <script>
    function changeEventStatus(eventNum) {
        // This will be handled by Streamlit buttons below
        console.log('Clicked event', eventNum);
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Status change interface (compact)
    st.markdown("### Change Event Status")
    
    # Get all events in a flat list for the selectbox
    all_events = []
    for day, events in filtered_events_by_day.items():
        for event_num, event_name in events:
            all_events.append((event_num, f"{event_num}: {event_name}", day))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_event = st.selectbox(
            "Select event to change:",
            options=[e[0] for e in all_events],
            format_func=lambda x: next(e[1] for e in all_events if e[0] == x),
            key="event_selector"
        )
    
    with col2:
        if selected_event:
            current_status = st.session_state.event_statuses.get(selected_event, "none")
            
            # Status buttons in a row
            status_cols = st.columns(4)
            
            with status_cols[0]:
                if st.button("🟢 Athlete", key=f"btn_athlete_{selected_event}",
                           type="primary" if current_status == "athlete_requested" else "secondary"):
                    st.session_state.event_statuses[selected_event] = "athlete_requested"
                    st.rerun()
            
            with status_cols[1]:
                if st.button("🟡 Coaches", key=f"btn_coaches_{selected_event}",
                           type="primary" if current_status == "coaches_suggested" else "secondary"):
                    st.session_state.event_statuses[selected_event] = "coaches_suggested"
                    st.rerun()
            
            with status_cols[2]:
                if st.button("🟣 Contingent", key=f"btn_contingent_{selected_event}",
                           type="primary" if current_status == "contingent" else "secondary"):
                    st.session_state.event_statuses[selected_event] = "contingent"
                    st.rerun()
            
            with status_cols[3]:
                if st.button("⚪ Clear", key=f"btn_clear_{selected_event}",
                           type="primary" if current_status == "none" else "secondary"):
                    st.session_state.event_statuses[selected_event] = "none"
                    st.rerun()
    
    # Summary
    st.markdown("### Summary")
    
    # Count events by status
    status_counts = {"athlete_requested": 0, "coaches_suggested": 0, "contingent": 0, "none": 0}
    
    all_eligible_events = set()
    for events in filtered_events_by_day.values():
        for event_num, _ in events:
            all_eligible_events.add(event_num)
    
    for event_num in all_eligible_events:
        status = st.session_state.event_statuses.get(event_num, "none")
        status_counts[status] += 1
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🟢 Athlete Requested", status_counts["athlete_requested"])
    with col2:
        st.metric("🟡 Coaches Suggested", status_counts["coaches_suggested"])
    with col3:
        st.metric("🟣 Contingent", status_counts["contingent"])
    with col4:
        st.metric("⚪ Not Considered", status_counts["none"])

def _should_show_event_for_planning(event_name):
    """Check if event should be shown in planning"""
    if event_name.startswith('PR'):
        return False
    if 'Inclusive' in event_name:
        return False
    if st.session_state.exclude_lightweight and 'ltwt' in event_name.lower():
        return False
    return True