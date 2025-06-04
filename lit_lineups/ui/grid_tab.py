"""
Assignments overview tab UI
"""
import streamlit as st
import pandas as pd
from models.constants import EVENTS_DATA

def render_assignments_overview_tab():
    """Render the assignments overview tab showing athlete assignments across all events"""
    st.header("Assignments Overview")
    
    if not st.session_state.lineups:
        st.info("No lineups created yet. Create lineups in the Lineup tab.")
        return
    
    # Get all events that have lineups with athletes
    events_with_lineups = []
    for event_num, lineup in st.session_state.lineups.items():
        athletes = [a for a in lineup.get('athletes', []) if a is not None]
        coxswain = lineup.get('coxswain')
        if athletes or coxswain:
            # Find event name and day
            event_name = "Unknown Event"
            event_day = "Unknown Day"
            for day, day_events in EVENTS_DATA.items():
                for num, name in day_events:
                    if num == event_num:
                        event_name = name
                        event_day = day
                        break
                if event_name != "Unknown Event":
                    break
            
            events_with_lineups.append({
                'event_num': event_num,
                'event_name': event_name,
                'event_day': event_day,
                'lineup': lineup
            })
    
    if not events_with_lineups:
        st.info("No events have athletes assigned yet.")
        return
    
    # Sort events by day then by event number
    day_order = {'Thursday': 0, 'Friday': 1, 'Saturday': 2, 'Sunday': 3, 'Monday': 4}
    events_with_lineups.sort(key=lambda x: (day_order.get(x['event_day'], 999), x['event_num']))
    
    # Get all unique athletes across all events
    all_athletes = set()
    for event_info in events_with_lineups:
        lineup = event_info['lineup']
        athletes = [a for a in lineup.get('athletes', []) if a is not None]
        coxswain = lineup.get('coxswain')
        
        for athlete in athletes:
            all_athletes.add(athlete)
        if coxswain:
            all_athletes.add(coxswain)
    
    # Sort athletes by name
    sorted_athletes = sorted(all_athletes, key=lambda x: x.name)
    
    # Create the dataframe for athletes
    athlete_data = []
    
    for athlete in sorted_athletes:
        row = {'Type': 'Athlete', 'Name': athlete.name}
        event_count = 0
        
        for event_info in events_with_lineups:
            event_num = event_info['event_num']
            lineup = event_info['lineup']
            athletes = lineup.get('athletes', [])
            coxswain = lineup.get('coxswain')
            
            # Check if athlete is in this event
            is_rower = athlete in athletes
            is_cox = athlete == coxswain
            
            if is_cox:
                row[str(event_num)] = "C"
                event_count += 1
            elif is_rower:
                row[str(event_num)] = "X"
                event_count += 1
            else:
                row[str(event_num)] = ""
        
        row['Total Events'] = event_count
        athlete_data.append(row)
    
    # Create the dataframe for boats (if boat assignments exist)
    boat_data = []
    if hasattr(st.session_state, 'boat_assignments') and st.session_state.boat_assignments:
        # Get all boats that are assigned
        assigned_boats = set(st.session_state.boat_assignments.values())
        sorted_boats = sorted(assigned_boats, key=lambda x: x.name)
        
        for boat in sorted_boats:
            row = {'Type': 'Boat', 'Name': boat.name}
            event_count = 0
            
            for event_info in events_with_lineups:
                event_num = event_info['event_num']
                assigned_boat = st.session_state.boat_assignments.get(event_num)
                
                if assigned_boat == boat:
                    row[str(event_num)] = "B"
                    event_count += 1
                else:
                    row[str(event_num)] = ""
            
            row['Total Events'] = event_count
            boat_data.append(row)
    
    # Combine athlete and boat data
    all_data = athlete_data + boat_data
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Create multi-level column headers
    # First, group events by day to create the header structure
    events_by_day = {}
    for event_info in events_with_lineups:
        day = event_info['event_day']
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event_info['event_num'])
    
    # Display day headers above the table
    st.markdown("### Event Assignments")
    
    # Calculate total number of event columns
    total_event_columns = len(events_with_lineups)
    
    # Create CSS for consistent grid layout
    grid_css = f"""
    <style>
    .assignment-grid {{
        display: grid;
        grid-template-columns: 150px repeat({total_event_columns}, 80px) 100px;
        gap: 1px;
        background-color: var(--text-color);
        margin: 10px 0;
    }}
    .grid-cell {{
        padding: 8px;
        text-align: center;
        background-color: var(--background-color);
        color: var(--text-color);
        font-size: 14px;
    }}
    .grid-header {{
        background-color: var(--secondary-background-color);
        font-weight: bold;
    }}
    .grid-name {{
        text-align: left;
    }}
    .grid-rower {{
        background-color: #2196f3;
        color: white;
        font-weight: bold;
    }}
    .grid-cox {{
        background-color: #ff9800;
        color: white;
        font-weight: bold;
    }}
    .grid-boat {{
        background-color: #4caf50;
        color: white;
        font-weight: bold;
    }}
    .grid-unavailable {{
        position: relative;
        color: #999;
    }}
    .grid-unavailable::after {{
        content: '';
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 2px;
        background-color: red;
        transform: translateY(-50%);
    }}
    .grid-total {{
        font-weight: bold;
    }}
    .grid-athlete-row {{
        background-color: var(--background-color);
    }}
    .grid-boat-row {{
        background-color: var(--secondary-background-color);
    }}
    </style>
    """
    st.markdown(grid_css, unsafe_allow_html=True)
    
    # Create the main grid container
    grid_html = "<div class='assignment-grid'>"
    
    # Day header row (spanning multiple columns)
    grid_html += "<div class='grid-cell grid-header'>Name</div>"
    
    # Group consecutive events by day for spanning
    current_day = None
    day_span_start = 0
    i = 0
    
    for event_info in events_with_lineups:
        day = event_info['event_day']
        if current_day != day:
            if current_day is not None:
                # Close previous day span
                span_count = i - day_span_start
                grid_html += f"<div class='grid-cell grid-header' style='grid-column: span {span_count};'>{current_day.upper()}</div>"
            current_day = day
            day_span_start = i
        i += 1
    
    # Close the last day span
    if current_day is not None:
        span_count = i - day_span_start
        grid_html += f"<div class='grid-cell grid-header' style='grid-column: span {span_count};'>{current_day.upper()}</div>"
    
    grid_html += "<div class='grid-cell grid-header'>Total</div>"
    
    # Event number header row
    grid_html += "<div class='grid-cell grid-header'></div>"  # Empty cell under "Name"
    
    for event_info in events_with_lineups:
        event_num = event_info['event_num']
        grid_html += f"<div class='grid-cell grid-header'>{event_num}</div>"
    
    grid_html += "<div class='grid-cell grid-header'>Events</div>"
    
    # Data rows
    for _, row in df.iterrows():
        row_type = row['Type']
        
        # Name cell with type indicator
        if row_type == 'Athlete':
            grid_html += f"<div class='grid-cell grid-name grid-athlete-row'>{row['Name']}</div>"
        else:  # Boat
            grid_html += f"<div class='grid-cell grid-name grid-boat-row'>🚣 {row['Name']}</div>"
        
        # Event assignments
        for event_info in events_with_lineups:
            event_num = event_info['event_num']
            event_day = event_info['event_day']
            value = row.get(str(event_num), "")
            
            # Check if this is an athlete row and if they're unavailable for this day
            is_unavailable = False
            if row_type == 'Athlete':
                # Find the athlete object to check availability
                athlete = next((a for a in sorted_athletes if a.name == row['Name']), None)
                if athlete and not athlete.is_available_on_day(event_day):
                    is_unavailable = True
            
            if value == "C":
                cell_class = "grid-cell grid-cox"
            elif value == "X":
                cell_class = "grid-cell grid-rower"
            elif value == "B":
                cell_class = "grid-cell grid-boat"
            else:
                # Use appropriate background for empty cells
                if row_type == 'Athlete':
                    cell_class = "grid-cell grid-athlete-row"
                else:
                    cell_class = "grid-cell grid-boat-row"
            
            # Add unavailable class if needed
            if is_unavailable:
                cell_class += " grid-unavailable"
            
            grid_html += f"<div class='{cell_class}'>{value}</div>"
        
        # Total events
        if row_type == 'Athlete':
            grid_html += f"<div class='grid-cell grid-total grid-athlete-row'>{row['Total Events']}</div>"
        else:
            grid_html += f"<div class='grid-cell grid-total grid-boat-row'>{row['Total Events']}</div>"
    
    grid_html += "</div>"
    
    st.markdown(grid_html, unsafe_allow_html=True)
    
    # Legend
    st.markdown("---")
    st.markdown("**Legend:** 🔵 X = Rower, 🟠 C = Coxswain, 🟢 B = Boat")
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Athletes", len(sorted_athletes))
    
    with col2:
        st.metric("Total Events", len(events_with_lineups))
    
    with col3:
        total_boats = len(boat_data) if boat_data else 0
        st.metric("Total Boats Used", total_boats)