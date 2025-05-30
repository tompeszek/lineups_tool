"""
Individual athlete view tab UI
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from models.constants import EVENTS_DATA
from utils.event_utils import get_event_time_both_sessions, parse_event_requirements, get_event_entries_2024, will_event_have_heat

def render_athlete_tab():
    """Render the individual athlete view tab"""
    st.header("Individual Athlete Schedules")
    
    if not st.session_state.athletes:
        st.info("No athletes in roster yet.")
        return
    
    if not st.session_state.lineups:
        st.info("No lineups created yet.")
        return
    
    # Sort athletes alphabetically by name
    sorted_athletes = sorted(enumerate(st.session_state.athletes), key=lambda x: x[1].name)
    sorted_indices = [idx for idx, athlete in sorted_athletes]
    
    selected_athlete_index = st.selectbox("Select Athlete", 
                                         options=sorted_indices,
                                         format_func=lambda x: f"{st.session_state.athletes[x].name}")# ({st.session_state.athletes[x].gender}, {st.session_state.athletes[x].age}, {st.session_state.athletes[x].weight}lbs)")
    
    if selected_athlete_index is not None:
        selected_athlete = st.session_state.athletes[selected_athlete_index]
        
        st.subheader(f"Schedule for {selected_athlete.name}")
        
        athlete_events = _get_athlete_events(selected_athlete)
        
        if athlete_events:
            # Add 2024 entries data to each event
            for event in athlete_events:
                # Extract event number from the event string
                event_num_str = event['Event'].split(':')[0]
                event_num = int(event_num_str)
                
                # Get 2024 entries data
                entries_2024 = get_event_entries_2024(event_num)
                event['Entries 2024'] = str(entries_2024) if entries_2024 is not None else "N/A"
            
            # Group events by day
            events_by_day = {'Thursday': [], 'Friday': [], 'Saturday': [], 'Sunday': []}
            for event in athlete_events:
                # Determine day from event number lookup
                event_day = None
                event_num_str = event['Event'].split(':')[0]
                event_num = int(event_num_str)
                
                for day, events in EVENTS_DATA.items():
                    for num, name in events:
                        if num == event_num:
                            event_day = day
                            break
                    if event_day:
                        break
                
                if event_day:
                    events_by_day[event_day].append(event)
            
            # Display each day separately
            total_events = 0
            for day in ['Thursday', 'Friday', 'Saturday', 'Sunday']:
                day_events = events_by_day[day]
                if day_events:
                    st.subheader(f"{day} Schedule")
                    # Sort by race time within the day
                    day_events.sort(key=lambda x: x['event_time_obj'])
                    
                    # Check for quick turnarounds and prepare data
                    styled_events = []
                    for i, event in enumerate(day_events):
                        # Check if this event has a quick turnaround from previous
                        has_quick_turnaround = False
                        if i > 0:
                            prev_time = day_events[i-1]['event_time_obj']
                            curr_time = event['event_time_obj']
                            time_diff_minutes = (curr_time - prev_time).total_seconds() / 60
                            
                            # Check if less than 60 minutes and positive (same day or next day)
                            if 0 < time_diff_minutes < 60:
                                has_quick_turnaround = True
                        
                        # Create display data - KEEP the Entries 2024 column
                        display_event = {k: v for k, v in event.items() if k != 'event_time_obj'}
                        styled_events.append((display_event, has_quick_turnaround))
                    
                    # Create DataFrame and apply styling
                    df_data = [event for event, _ in styled_events]
                    df = pd.DataFrame(df_data)
                    
                    # Reorder columns to make sure Entries 2024 is visible
                    desired_columns = ['Meet Time', 'Launch Time', 'Race Time', 'Land Time', 'Event', 'Entries 2024', 'Role', 'Boat', 'Crew']
                    # Only include columns that actually exist in the data
                    available_columns = [col for col in desired_columns if col in df.columns]
                    if available_columns:
                        df = df[available_columns]
                    
                    # Apply styling for quick turnarounds
                    def highlight_quick_turnaround(row):
                        try:
                            row_dict = row.to_dict()
                            idx = next(i for i, event in enumerate(df_data) if event == row_dict)
                            if styled_events[idx][1]:  # has_quick_turnaround
                                return ['border-left: 4px solid #f44336; font-weight: bold; background-color: rgba(244, 67, 54, 0.1)'] * len(row)
                            return [''] * len(row)
                        except:
                            return [''] * len(row)
                    
                    styled_df = df.style.apply(highlight_quick_turnaround, axis=1)
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                    total_events += len(day_events)
            
            st.write(f"**Total events: {total_events}**")
            
            # Check for potential issues across all days
            all_events = []
            for day, day_events in events_by_day.items():
                # Add day info back for sorting and issue checking
                for event in day_events:
                    event_with_day = event.copy()
                    event_with_day['Day'] = day
                    all_events.append(event_with_day)
            
            all_events.sort(key=lambda x: (x['Day'], x['event_time_obj']))
            
            issues = _check_athlete_schedule_issues(all_events)
            if issues:
                issue_text = "**Potential Issues:**\n\n"
                for issue in issues:
                    issue_text += f"• {issue}\n"
                st.warning(issue_text)
        else:
            st.info(f"{selected_athlete.name} is not currently assigned to any events.")
            _show_preferred_events(selected_athlete)

def _get_athlete_events(athlete):
    """Get all events for a specific athlete (both morning and afternoon sessions)"""
    athlete_events = []
    
    # Find all events this athlete is in
    for event_num, lineup in st.session_state.lineups.items():
        role = None
        seat_name = None
        
        # Check if athlete is a rower
        for i, rower in enumerate(lineup.get('athletes', [])):
            if rower == athlete:
                role = "Rower"
                # Get seat name
                event_name = None
                for day, events in EVENTS_DATA.items():
                    for num, name in events:
                        if num == event_num:
                            event_name = name
                            break
                    if event_name:
                        break
                
                if event_name:
                    requirements = parse_event_requirements(event_name)
                    seat_name = _get_seat_name(i, requirements)
                    role = seat_name
                break
        
        # Check if athlete is coxswain
        if not role and lineup.get('coxswain') == athlete:
            role = "Coxswain"
        
        if role:
            # Find event name and day by searching through EVENTS_DATA
            event_name = None
            event_day = None
            
            for day, events in EVENTS_DATA.items():
                for num, name in events:
                    if num == event_num:
                        event_name = name
                        event_day = day
                        break
                if event_name:
                    break
            
            if event_name and event_day:
                # Get times for both sessions
                morning_time, afternoon_time = get_event_time_both_sessions(event_num, st.session_state.event_spacing_minutes)
                
                # Get crew members (other people in the boat)
                crew_members = _get_crew_members(event_num, athlete)
                
                # Get boat assignment
                boat_name = "Not assigned"
                if hasattr(st.session_state, 'boat_assignments') and event_num in st.session_state.boat_assignments:
                    boat = st.session_state.boat_assignments[event_num]
                    boat_name = boat.name
                
                # Add morning session (Heat)
                morning_meet = morning_time - timedelta(minutes=st.session_state.meet_minutes_before)
                morning_launch = morning_time - timedelta(minutes=st.session_state.launch_minutes_before)
                morning_land = morning_time + timedelta(minutes=st.session_state.land_minutes_after)
                
                athlete_events.append({
                    'Meet Time': morning_meet.strftime("%H:%M"),
                    'Launch Time': morning_launch.strftime("%H:%M"),
                    'Race Time': morning_time.strftime("%H:%M"),
                    'Land Time': morning_land.strftime("%H:%M"),
                    'Event': f"{event_num}: {event_name} (Heat)",
                    'Role': role,
                    'Boat': boat_name,
                    'Crew': crew_members,
                    'event_time_obj': morning_time  # For sorting and quick turnaround detection
                })
                
                # Add afternoon session (Final)
                afternoon_meet = afternoon_time - timedelta(minutes=st.session_state.meet_minutes_before)
                afternoon_launch = afternoon_time - timedelta(minutes=st.session_state.launch_minutes_before)
                afternoon_land = afternoon_time + timedelta(minutes=st.session_state.land_minutes_after)
                
                athlete_events.append({
                    'Meet Time': afternoon_meet.strftime("%H:%M"),
                    'Launch Time': afternoon_launch.strftime("%H:%M"),
                    'Race Time': afternoon_time.strftime("%H:%M"),
                    'Land Time': afternoon_land.strftime("%H:%M"),
                    'Event': f"{event_num}: {event_name} (Final)",
                    'Role': role,
                    'Boat': boat_name,
                    'Crew': crew_members,
                    'event_time_obj': afternoon_time  # For sorting and quick turnaround detection
                })
    
    return athlete_events

def _get_crew_members(event_num, selected_athlete):
    """Get list of other crew members in the same boat for an event"""
    if event_num not in st.session_state.lineups:
        return "No lineup"
    
    lineup = st.session_state.lineups[event_num]
    crew_names = []
    
    # Add rowers (excluding the selected athlete)
    for athlete in lineup.get('athletes', []):
        if athlete is not None and athlete != selected_athlete:
            crew_names.append(athlete.name)
    
    # Add coxswain (excluding the selected athlete if they are cox)
    coxswain = lineup.get('coxswain')
    if coxswain is not None and coxswain != selected_athlete:
        crew_names.append(f"{coxswain.name} (Cox)")
    
    if not crew_names:
        return "Solo"
    
    return ", ".join(crew_names)

def _get_seat_name(seat_idx, requirements):
    """Get the name for a seat position"""
    if requirements['is_sculling']:
        return f"Seat {seat_idx + 1}"
    else:
        if requirements['num_rowers'] == 8:
            positions = ["Bow", "2", "3", "4", "5", "6", "7", "Stroke"]
        elif requirements['num_rowers'] == 4:
            positions = ["Bow", "2", "3", "Stroke"]
        elif requirements['num_rowers'] == 2:
            positions = ["Bow", "Stroke"]
        else:
            positions = [f"Seat {i+1}" for i in range(requirements['num_rowers'])]
        
        return positions[seat_idx] if seat_idx < len(positions) else f"Seat {seat_idx + 1}"

def _check_athlete_schedule_issues(athlete_events):
    """Check for scheduling issues for an athlete"""
    issues = []
    
    if len(athlete_events) <= 1:
        return issues
    
    # Sort by event time object first to ensure proper order
    sorted_events = sorted(athlete_events, key=lambda x: x['event_time_obj'])
    
    for i in range(len(sorted_events) - 1):
        current_event = sorted_events[i]
        next_event = sorted_events[i+1]
        
        current_time_obj = current_event['event_time_obj']
        next_time_obj = next_event['event_time_obj']
        
        # Calculate time difference in minutes using datetime objects
        gap_minutes = (next_time_obj - current_time_obj).total_seconds() / 60
        
        # Only flag issues for events on the same day or very close together
        if gap_minutes < st.session_state.min_gap_minutes and gap_minutes > 0:
            current_event_num = int(current_event['Event'].split(':')[0])
            next_event_num = int(next_event['Event'].split(':')[0])
            
            # Get day for the issue
            event_day = current_event.get('Day', 'Unknown Day')
            
            issues.append(f"Short gap ({gap_minutes:.0f} min) between events {current_event_num} and {next_event_num} on {event_day}")
    
    return issues

def _show_preferred_events(athlete):
    """Show preferred events that athlete could be added to"""
    if not athlete.preferred_events:
        return
    
    st.write("**Preferred events:**")
    for pref_event_num in athlete.preferred_events:
        # Find the event by number
        event_found = False
        for day, events in EVENTS_DATA.items():
            for num, name in events:
                if num == pref_event_num:
                    event_found = True
                    lineup_status = "Empty"
                    if num in st.session_state.lineups:
                        lineup = st.session_state.lineups[num]
                        if lineup.get('athletes') or lineup.get('coxswain'):
                            lineup_status = "Has lineup"
                    
                    st.write(f"- Event {num}: {name} ({day}) - {lineup_status}")
                    break
            if event_found:
                break
        
        if not event_found:
            st.write(f"- Event {pref_event_num}: Not found")