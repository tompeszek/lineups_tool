"""
Equipment management tab UI
"""
import streamlit as st
import pandas as pd
from datetime import timedelta
from models.boat import Boat, create_sample_boats
from models.constants import EVENTS_DATA
from utils.event_utils import get_event_time, get_event_time_both_sessions, parse_event_requirements

def render_equipment_tab():
    """Render the equipment management tab"""
    st.header("Equipment Management")
    
    # Initialize boats if needed
    if 'boats' not in st.session_state:
        st.session_state.boats = []
    
    # Initialize boat assignments if needed
    if 'boat_assignments' not in st.session_state:
        st.session_state.boat_assignments = {}  # {event_num: boat_object}
    
    # Load sample boats section
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("Load Sample Boat Fleet"):
            st.session_state.boats = create_sample_boats()
            st.success(f"Loaded {len(st.session_state.boats)} boats!")
    
    with col2:
        if st.button("Auto-Assign Boats"):
            if st.session_state.boats and st.session_state.lineups:
                result = _auto_assign_boats()
                if result["success"]:
                    st.success(f"Auto-assigned {result['assigned']} boats! Using {result['boats_used']} total boats.")
                    if result["issues"]:
                        st.warning("Some issues during assignment:")
                        for issue in result["issues"]:
                            st.write(f"- {issue}")
                    st.rerun()
                else:
                    st.error(result["message"])
            else:
                st.error("Need boats and lineups to auto-assign!")
    
    with col3:
        if st.button("Clear All Boats"):
            st.session_state.boats = []
            st.session_state.boat_assignments = {}
            st.success("All boats cleared!")
    
    # Display current boat fleet
    if st.session_state.boats:
        st.subheader("Available Boats")
        boat_data = []
        for boat in st.session_state.boats:
            # Check if boat is assigned
            assigned_events = [event_num for event_num, assigned_boat in st.session_state.boat_assignments.items() 
                             if assigned_boat == boat]
            status = f"Assigned to Event {assigned_events[0]}" if assigned_events else "Available"
            
            boat_data.append({
                'ID': boat.boat_id or '',
                'Name': boat.name,
                'Type': boat.boat_type,
                'Seats': boat.num_seats,
                'Weight Range': f"{boat.min_weight}-{boat.max_weight}",
                'Manufacturer': boat.manufacturer,
                'Year': boat.year or '',
                'Status': status
            })
        
        df = pd.DataFrame(boat_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No boats available. Load the sample fleet to get started.")
        return
    
    # Only show boat assignment if we have lineups
    if not st.session_state.lineups:
        st.info("Create some lineups first to assign boats.")
        return
    
    st.subheader("Boat Assignments")
    
    # Show events that need boats (ordered by event number)
    events_needing_boats = []
    for event_num, lineup in st.session_state.lineups.items():
        if lineup.get('athletes') and any(a is not None for a in lineup['athletes']):
            events_needing_boats.append(event_num)
    
    if not events_needing_boats:
        st.info("No lineups with athletes to assign boats to.")
        return
    
    # Show boat assignment for each event (ordered by event number)
    for event_num in sorted(events_needing_boats):
        _render_boat_assignment_for_event(event_num)
    
    # Show boat conflicts
    _show_boat_conflicts()

def _render_boat_assignment_for_event(event_num):
    """Render boat assignment section for a specific event"""
    # Find event name
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
    
    if not event_name:
        return
    
    lineup = st.session_state.lineups[event_num]
    athletes = [a for a in lineup.get('athletes', []) if a is not None]
    
    if not athletes:
        return
    
    # Calculate average weight
    avg_weight = sum(a.weight for a in athletes) / len(athletes)
    
    # Get compatible boats
    compatible_boats = [boat for boat in st.session_state.boats 
                       if boat.is_compatible_with_event(event_name)]
    
    # Filter out boats that are assigned to conflicting events
    available_boats = []
    for boat in compatible_boats:
        if boat not in st.session_state.boat_assignments.values():
            available_boats.append(boat)
        else:
            # Check if assigned to a conflicting time
            assigned_event = next(e for e, b in st.session_state.boat_assignments.items() if b == boat)
            if not _boats_conflict(event_num, assigned_event):
                available_boats.append(boat)
    
    with st.expander(f"Event {event_num}: {event_name} (Avg weight: {avg_weight:.1f} lbs)", 
                     expanded=event_num not in st.session_state.boat_assignments):
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Show current assignment
            current_boat = st.session_state.boat_assignments.get(event_num)
            if current_boat:
                weight_status = current_boat.weight_check(avg_weight)
                
                # Create boat details string
                boat_details = f"{current_boat.name}"
                if current_boat.manufacturer:
                    boat_details += f" ({current_boat.manufacturer}"
                    if current_boat.year:
                        boat_details += f" {current_boat.year}"
                    boat_details += ")"
                elif current_boat.year:
                    boat_details += f" ({current_boat.year})"
                
                if weight_status == "good":
                    st.success(f"✅ Currently assigned: **{boat_details}**")
                elif weight_status == "warning":
                    st.warning(f"⚠️ Currently assigned: **{boat_details}** (weight outside ideal range)")
                else:
                    st.error(f"❌ Currently assigned: **{boat_details}** (weight significantly outside range)")
                
                st.write(f"Weight range: {current_boat.min_weight}-{current_boat.max_weight} lbs | Type: {current_boat.boat_type}")
            else:
                st.info("No boat assigned")
            
            # Show boat options (excluding currently assigned boat)
            if available_boats:
                st.write("**Available compatible boats:**")
                for boat in available_boats:
                    # Skip the currently assigned boat to avoid showing it as a button
                    if current_boat and boat == current_boat:
                        continue
                        
                    weight_status = boat.weight_check(avg_weight)
                    if weight_status == "good":
                        status_icon = "✅"
                    elif weight_status == "warning":
                        status_icon = "⚠️"
                    else:
                        status_icon = "❌"
                    
                    # Create boat button text with manufacturer and year
                    boat_text = f"{boat.name}"
                    if boat.manufacturer or boat.year:
                        boat_text += " ("
                        if boat.manufacturer:
                            boat_text += boat.manufacturer
                        if boat.year:
                            if boat.manufacturer:
                                boat_text += f" {boat.year}"
                            else:
                                boat_text += str(boat.year)
                        boat_text += ")"
                    
                    boat_text += f" | {boat.min_weight}-{boat.max_weight} lbs"
                    
                    if st.button(f"{status_icon} {boat_text}", 
                               key=f"assign_{event_num}_{boat.name}"):
                        st.session_state.boat_assignments[event_num] = boat
                        st.rerun()
            else:
                if current_boat:
                    st.info("Current boat is the only compatible option available")
                else:
                    st.warning("No compatible boats available (may be assigned to conflicting events)")
        
        with col2:
            # Show lineup details in a table
            st.write("**Lineup:**")
            lineup_data = []
            for i, athlete in enumerate(athletes, 1):
                lineup_data.append({
                    'Position': f"{i}",
                    'Name': athlete.name,
                    'Gender': athlete.gender[0],
                    'Weight': f"{athlete.weight}lbs"
                })
            
            coxswain = lineup.get('coxswain')
            if coxswain:
                lineup_data.append({
                    'Position': 'Cox',
                    'Name': coxswain.name,
                    'Gender': coxswain.gender[0],
                    'Weight': f"{coxswain.weight}lbs"
                })
            
            lineup_df = pd.DataFrame(lineup_data)
            st.dataframe(lineup_df, use_container_width=True, hide_index=True)
            
            # Show event timing for both sessions in tables
            st.write(f"**{event_day} Schedule:**")
            
            # Get times for both sessions
            morning_time, afternoon_time = get_event_time_both_sessions(event_num, st.session_state.event_spacing_minutes)
            
            # Create schedule table
            schedule_data = []
            
            # Morning session (Heat)
            morning_launch = morning_time - timedelta(minutes=st.session_state.launch_minutes_before)
            morning_land = morning_time + timedelta(minutes=st.session_state.land_minutes_after)
            
            schedule_data.append({
                'Session': '🌅 Heat',
                'Launch': morning_launch.strftime('%H:%M'),
                'Race': morning_time.strftime('%H:%M'),
                'Land': morning_land.strftime('%H:%M')
            })
            
            # Afternoon session (Final)
            afternoon_launch = afternoon_time - timedelta(minutes=st.session_state.launch_minutes_before)
            afternoon_land = afternoon_time + timedelta(minutes=st.session_state.land_minutes_after)
            
            schedule_data.append({
                'Session': '🌇 Final',
                'Launch': afternoon_launch.strftime('%H:%M'),
                'Race': afternoon_time.strftime('%H:%M'),
                'Land': afternoon_land.strftime('%H:%M')
            })
            
            schedule_df = pd.DataFrame(schedule_data)
            st.dataframe(schedule_df, use_container_width=True, hide_index=True)
            
            # Unassign button
            if current_boat:
                st.write("")  # Add some spacing
                if st.button("Unassign Boat", key=f"unassign_{event_num}"):
                    del st.session_state.boat_assignments[event_num]
                    st.rerun()

def _boats_conflict(event1_num, event2_num):
    """Check if two events have conflicting boat usage times"""
    # Get timing for both events
    event1_time = get_event_time(event1_num, st.session_state.event_spacing_minutes)
    event2_time = get_event_time(event2_num, st.session_state.event_spacing_minutes)
    
    # Calculate launch and land times
    event1_launch = event1_time - timedelta(minutes=st.session_state.launch_minutes_before)
    event1_land = event1_time + timedelta(minutes=st.session_state.land_minutes_after)
    
    event2_launch = event2_time - timedelta(minutes=st.session_state.launch_minutes_before)
    event2_land = event2_time + timedelta(minutes=st.session_state.land_minutes_after)
    
    # Check for overlap
    return not (event1_land <= event2_launch or event2_land <= event1_launch)

def _show_boat_conflicts():
    """Show any boat assignment conflicts"""
    conflicts = []
    
    # Check all boat assignments for conflicts
    assigned_events = list(st.session_state.boat_assignments.keys())
    for i, event1 in enumerate(assigned_events):
        for event2 in assigned_events[i+1:]:
            boat1 = st.session_state.boat_assignments[event1]
            boat2 = st.session_state.boat_assignments[event2]
            
            if boat1 == boat2 and _boats_conflict(event1, event2):
                conflicts.append(f"Boat {boat1.name} assigned to conflicting events {event1} and {event2}")
    
    if conflicts:
        st.subheader("⚠️ Boat Conflicts")
        for conflict in conflicts:
            st.error(conflict)
    
    # Show boat utilization summary
    if st.session_state.boat_assignments:
        st.subheader("Boat Utilization Summary")
        
        boat_usage = {}
        for event_num, boat in st.session_state.boat_assignments.items():
            if boat.name not in boat_usage:
                boat_usage[boat.name] = []
            boat_usage[boat.name].append(event_num)
        
        # Sort boats by number of seats (descending), then by average weight (descending)
        sorted_boats = []
        for boat_name, events in boat_usage.items():
            boat = next((b for b in st.session_state.boats if b.name == boat_name), None)
            if boat:
                avg_weight = (boat.min_weight + boat.max_weight) / 2
                sorted_boats.append((boat.num_seats, avg_weight, boat_name, boat, events))
        
        # Sort by seats descending, then avg weight descending
        sorted_boats.sort(key=lambda x: (-x[0], -x[1]))
        
        for num_seats, avg_weight, boat_name, boat, events in sorted_boats:
            boat_details = f"{boat.boat_type} | {boat.manufacturer} {boat.year or ''} | {boat.min_weight}-{boat.max_weight}lbs"
            st.markdown(f"### {boat_name}")
            st.write(f"*{boat_details}*")
            
            # List events as bullets with event names (ordered by event number)
            for event_num in sorted(events):
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
                
                st.write(f"  • {event_day} - Event {event_num}: {event_name}")
            
            st.write("")  # Add spacing between boats
        
        # Handle boats without details (fallback)
        for boat_name, events in boat_usage.items():
            if not any(boat_name == name for _, _, name, _, _ in sorted_boats):
                st.markdown(f"### {boat_name}")
                for event_num in sorted(events):
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
                    
                    st.write(f"  • {event_day} - Event {event_num}: {event_name}")
                
                st.write("")  # Add spacing between boats

def _auto_assign_boats():
    """Auto-assign boats to events to minimize boat count while avoiding conflicts"""
    from datetime import timedelta
    from utils.event_utils import get_event_time, parse_event_requirements
    
    # Clear existing assignments
    st.session_state.boat_assignments = {}
    
    # Get all events that need boats
    events_needing_boats = []
    for event_num, lineup in st.session_state.lineups.items():
        if lineup.get('athletes') and any(a is not None for a in lineup['athletes']):
            # Find event name
            event_name = None
            for day, events in EVENTS_DATA.items():
                for num, name in events:
                    if num == event_num:
                        event_name = name
                        break
                if event_name:
                    break
            
            if event_name:
                athletes = [a for a in lineup.get('athletes', []) if a is not None]
                avg_weight = sum(a.weight for a in athletes) / len(athletes)
                event_time = get_event_time(event_num, st.session_state.event_spacing_minutes)
                launch_time = event_time - timedelta(minutes=st.session_state.launch_minutes_before)
                land_time = event_time + timedelta(minutes=st.session_state.land_minutes_after)
                
                events_needing_boats.append({
                    'event_num': event_num,
                    'event_name': event_name,
                    'avg_weight': avg_weight,
                    'launch_time': launch_time,
                    'land_time': land_time,
                    'requirements': parse_event_requirements(event_name)
                })
    
    if not events_needing_boats:
        return {"success": False, "message": "No events need boat assignments"}
    
    # Sort events by launch time to assign in chronological order
    events_needing_boats.sort(key=lambda x: x['launch_time'])
    
    assigned_count = 0
    issues = []
    boats_used = set()
    
    for event_info in events_needing_boats:
        event_num = event_info['event_num']
        event_name = event_info['event_name']
        avg_weight = event_info['avg_weight']
        launch_time = event_info['launch_time']
        land_time = event_info['land_time']
        requirements = event_info['requirements']
        
        # Find compatible boats
        compatible_boats = []
        for boat in st.session_state.boats:
            if boat.is_compatible_with_event(event_name):
                compatible_boats.append(boat)
        
        if not compatible_boats:
            issues.append(f"No compatible boats found for Event {event_num}")
            continue
        
        # Score boats by preference:
        # 1. Weight compatibility (good > warning > bad)
        # 2. Whether boat is already in use (prefer reusing boats)
        # 3. Availability (no time conflicts)
        
        boat_scores = []
        for boat in compatible_boats:
            # Check if boat is available (no time conflicts)
            available = True
            for assigned_event, assigned_boat in st.session_state.boat_assignments.items():
                if assigned_boat == boat:
                    # Check for time conflict
                    other_event_time = get_event_time(assigned_event, st.session_state.event_spacing_minutes)
                    other_launch = other_event_time - timedelta(minutes=st.session_state.launch_minutes_before)
                    other_land = other_event_time + timedelta(minutes=st.session_state.land_minutes_after)
                    
                    # Check for overlap
                    if not (land_time <= other_launch or other_land <= launch_time):
                        available = False
                        break
            
            if not available:
                continue  # Skip boats that would cause conflicts
            
            # Calculate score
            score = 0
            
            # Weight compatibility score (most important)
            weight_check = boat.weight_check(avg_weight)
            if weight_check == "good":
                score += 100
            elif weight_check == "warning":
                score += 50
            else:
                score += 10  # Still usable but not ideal
            
            # Prefer boats already in use (to minimize total boats needed)
            if boat.name in boats_used:
                score += 20
            
            boat_scores.append((score, boat))
        
        if not boat_scores:
            issues.append(f"No available boats for Event {event_num} (all compatible boats have conflicts)")
            continue
        
        # Sort by score (highest first) and assign best boat
        boat_scores.sort(key=lambda x: x[0], reverse=True)
        best_score, best_boat = boat_scores[0]
        
        st.session_state.boat_assignments[event_num] = best_boat
        boats_used.add(best_boat.name)
        assigned_count += 1
        
        # Check if weight is outside ideal range
        weight_check = best_boat.weight_check(avg_weight)
        if weight_check == "bad":
            issues.append(f"Event {event_num}: Weight {avg_weight:.1f}lbs significantly outside {best_boat.name} range ({best_boat.min_weight}-{best_boat.max_weight}lbs)")
        elif weight_check == "warning":
            issues.append(f"Event {event_num}: Weight {avg_weight:.1f}lbs near limits for {best_boat.name} ({best_boat.min_weight}-{best_boat.max_weight}lbs)")
    
    return {
        "success": True,
        "assigned": assigned_count,
        "boats_used": len(boats_used),
        "issues": issues
    }

def _add_boat_to_lineup_display():
    """Helper to add boat info to lineup displays"""
    # This function can be called from other tabs to show boat assignments
    pass