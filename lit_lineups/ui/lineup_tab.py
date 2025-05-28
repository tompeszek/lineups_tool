"""
Event lineup management tab UI
"""
import streamlit as st
from models.constants import EVENTS_DATA
from utils.event_utils import parse_event_requirements

def render_lineup_tab():
    """Render the lineup management tab"""
    st.header("Event Lineups")
    
    if not st.session_state.athletes:
        st.info("No athletes in roster yet. Add athletes in the Roster tab.")
        return
    
    # Initialize selected events if needed
    if 'selected_events' not in st.session_state:
        st.session_state.selected_events = set()
    
    # Event selection section
    st.subheader("Select Events to Race")
    
    # Filter events
    filtered_events_by_day = {}
    for day, events in EVENTS_DATA.items():
        filtered_events = []
        for event_num, event_name in events:
            if _should_show_event(event_name):
                filtered_events.append((event_num, event_name))
        if filtered_events:
            filtered_events_by_day[day] = filtered_events
    
    if not filtered_events_by_day:
        st.warning("No eligible events found for your roster!")
        return
    
    # Group events by day for better organization
    for day, events in filtered_events_by_day.items():
        with st.expander(f"{day} Events ({len(events)} available)", expanded=False):
            day_cols = st.columns(2)
            col_idx = 0
            
            for event_num, event_name in events:
                with day_cols[col_idx % 2]:
                    is_selected = event_num in st.session_state.selected_events
                    
                    if st.checkbox(f"{event_num}: {event_name}", 
                                 value=is_selected, 
                                 key=f"event_select_{event_num}"):
                        st.session_state.selected_events.add(event_num)
                    else:
                        st.session_state.selected_events.discard(event_num)
                        # Clear lineup when event is deselected
                        if event_num in st.session_state.lineups:
                            del st.session_state.lineups[event_num]
                
                col_idx += 1
    
    # Only show lineup management if events are selected
    if not st.session_state.selected_events:
        st.info("Select events above to start creating lineups.")
        return
    
    # Create event list for selectbox from selected events
    selected_event_list = []
    for day, events in filtered_events_by_day.items():
        for event_num, event_name in events:
            if event_num in st.session_state.selected_events:
                selected_event_list.append((event_num, event_name))
    
    if not selected_event_list:
        st.info("No events selected.")
        return
    
    selected_event = st.selectbox("Select Event to Build Lineup", 
                                options=[num for num, _ in selected_event_list],
                                format_func=lambda x: next(f"{x}: {name}" for num, name in selected_event_list if num == x))
    
    # Current lineup section
    if selected_event:
        event_name = next((name for num, name in selected_event_list if num == selected_event), "Unknown Event")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            _render_lineup_management(selected_event, event_name)
        
        with col2:
            _render_seat_assignment_display(selected_event, event_name)

def _should_show_event(event_name):
    """Check if event should be shown based on filtering criteria"""
    # Filter out PR events
    if event_name.startswith('PR'):
        return False
    
    # Filter out inclusive events
    if 'Inclusive' in event_name:
        return False
    
    # Filter out lightweight events if option is enabled
    if st.session_state.exclude_lightweight and 'ltwt' in event_name.lower():
        return False
    
    # Check if we have enough eligible athletes for this event
    return _has_enough_eligible_athletes(event_name)

def _has_enough_eligible_athletes(event_name):
    """Check if we have enough eligible athletes for an event"""
    requirements = parse_event_requirements(event_name)
    eligible_count = sum(1 for athlete in st.session_state.athletes if _athlete_fits_basic_requirements(athlete, event_name))
    return eligible_count >= 1  # At least one athlete needed

def _athlete_fits_basic_requirements(athlete, event_name):
    """Check if athlete meets basic requirements for an event"""
    from models.boat import BoatType
    
    # Gender requirements
    if 'Men\'s' in event_name and athlete.gender != 'M':
        return False
    if 'Women\'s' in event_name and athlete.gender != 'F':
        return False
    
    # Boat type requirements
    boat = BoatType(event_name.split()[-1])
    if boat.is_sculling and not athlete.can_scull:
        return False
    if boat.is_sweep and not (athlete.can_port or athlete.can_starboard):
        return False
    
    return True

def _get_day_from_event_data(event_num):
    """Get the day for a given event number"""
    for day, events in EVENTS_DATA.items():
        for num, name in events:
            if num == event_num:
                return day
    return None

def _format_athlete_info(athlete):
    """Format athlete info string"""
    boat_types = []
    if athlete.can_scull:
        boat_types.append("SX")
    if athlete.can_port and athlete.can_starboard:
        boat_types.append("SW")
    elif athlete.can_port:
        boat_types.append("P")
    elif athlete.can_starboard:
        boat_types.append("S")
    
    boat_str = "-".join(boat_types)
    return f"{athlete.gender}-{boat_str}-{athlete.age}({athlete.age_category})"

def _render_lineup_management(selected_event, event_name):
    """Render the athlete selection with seat buttons"""
    st.subheader("Available Athletes")
    
    requirements = parse_event_requirements(event_name)
    event_day = _get_day_from_event_data(selected_event)
    
    # Initialize lineup if needed
    if selected_event not in st.session_state.lineups:
        st.session_state.lineups[selected_event] = {'athletes': [None] * requirements['num_rowers'], 'coxswain': None}
    
    current_lineup = st.session_state.lineups[selected_event]
    
    # Ensure the athletes list has the right length
    if len(current_lineup.get('athletes', [])) != requirements['num_rowers']:
        current_lineup['athletes'] = [None] * requirements['num_rowers']
    
    # Get eligible athletes not already in the lineup
    eligible_athletes = [a for a in st.session_state.athletes if _athlete_fits_basic_requirements(a, event_name)]
    day_available_athletes = [a for a in eligible_athletes if a.is_available_on_day(event_day)]
    
    # Remove athletes already in lineup
    assigned_athletes = set([a for a in current_lineup.get('athletes', []) if a is not None])
    if current_lineup.get('coxswain'):
        assigned_athletes.add(current_lineup['coxswain'])
    
    available_athletes = [a for a in day_available_athletes if a not in assigned_athletes]
    
    if not available_athletes:
        st.write("No available athletes for this event/day")
        return
    
    # Show each available athlete with seat buttons in compact format
    for athlete in available_athletes:
        # Check if preferred
        is_preferred = selected_event in athlete.preferred_events
        prefix = "⭐ " if is_preferred else ""
        athlete_info = _format_athlete_info(athlete)
        
        # Create a container for this athlete
        with st.container():
            # Athlete name and info on one line, buttons below
            st.write(f"{prefix}**{athlete.name}** ({athlete_info})")
            
            # All seat buttons in one row
            button_cols = st.columns(requirements['num_rowers'] + (1 if requirements['has_cox'] and athlete.can_cox else 0))
            
            # Rower seat buttons
            for i in range(requirements['num_rowers']):
                with button_cols[i]:
                    seat_name = _get_seat_name(i, requirements)
                    current_occupant = current_lineup['athletes'][i]
                    
                    # Shorter button text
                    if current_occupant:
                        button_text = f"{seat_name}*"  # * indicates occupied
                    else:
                        button_text = seat_name
                    
                    if st.button(button_text, key=f"{athlete.name}_{selected_event}_seat_{i}"):
                        current_lineup['athletes'][i] = athlete
                        st.rerun()
            
            # Coxswain button
            if requirements['has_cox'] and athlete.can_cox:
                with button_cols[requirements['num_rowers']]:
                    current_cox = current_lineup.get('coxswain')
                    cox_text = "Cox*" if current_cox else "Cox"
                    
                    if st.button(cox_text, key=f"{athlete.name}_{selected_event}_cox"):
                        current_lineup['coxswain'] = athlete
                        st.rerun()
    
    # Clear lineup button
    if st.button("Clear Entire Lineup", key=f"clear_{selected_event}"):
        current_lineup['athletes'] = [None] * requirements['num_rowers']
        current_lineup['coxswain'] = None
        st.rerun()

def _render_seat_assignment_display(selected_event, event_name):
    """Render a thin display of current seat assignments"""
    
    st.subheader("Current Lineup")
    st.write(f"**Event {selected_event}: {event_name}**")
    
    event_day = _get_day_from_event_data(selected_event)
    requirements = parse_event_requirements(event_name)
    
    # Initialize lineup if needed
    if selected_event not in st.session_state.lineups:
        st.session_state.lineups[selected_event] = {'athletes': [None] * requirements['num_rowers'], 'coxswain': None}
    
    current_lineup = st.session_state.lineups[selected_event]
    
    # Ensure the athletes list has the right length
    if len(current_lineup.get('athletes', [])) != requirements['num_rowers']:
        current_lineup['athletes'] = [None] * requirements['num_rowers']
    
    # Show race time
    from utils.event_utils import get_event_time
    event_time = get_event_time(selected_event, st.session_state.event_spacing_minutes)
    st.write(f"*{event_day} at {event_time.strftime('%H:%M')}*")
    
    # Show each seat compactly
    for seat_idx in range(requirements['num_rowers']):
        seat_name = _get_seat_name(seat_idx, requirements)
        current_athlete = current_lineup['athletes'][seat_idx]
        
        if current_athlete:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{seat_name}:** {current_athlete.name}")
            with col2:
                if st.button("Remove", key=f"remove_seat_display_{selected_event}_{seat_idx}"):
                    current_lineup['athletes'][seat_idx] = None
                    st.rerun()
        else:
            st.write(f"**{seat_name}:** *Empty*")
    
    # Show coxswain
    if requirements['has_cox']:
        current_cox = current_lineup.get('coxswain')
        if current_cox:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Cox:** {current_cox.name}")
            with col2:
                if st.button("Remove", key=f"remove_cox_display_{selected_event}"):
                    current_lineup['coxswain'] = None
                    st.rerun()
        else:
            st.write(f"**Cox:** *Empty*")
    
    # Show more helpful status
    athletes = [a for a in current_lineup.get('athletes', []) if a is not None]
    filled_seats = len(athletes)
    total_seats = requirements['num_rowers']
    
    if filled_seats == total_seats:
        st.success("✅ Lineup complete!")
    elif filled_seats == 0:
        st.info(f"Need {total_seats} athletes")
    else:
        remaining = total_seats - filled_seats
        st.warning(f"⚠️ {remaining} more athlete{'s' if remaining != 1 else ''} needed")
    
    # Show average age if we have athletes
    if athletes:
        avg_age = sum(a.age for a in athletes) / len(athletes)
        st.write(f"Average age: **{avg_age:.1f}**")
    
    # Clear all button
    if athletes or current_lineup.get('coxswain'):
        if st.button("Clear All", key=f"clear_display_{selected_event}"):
            current_lineup['athletes'] = [None] * requirements['num_rowers']
            current_lineup['coxswain'] = None
            st.rerun()

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

def _get_available_athletes_for_seat(event_num, seat_idx, requirements, event_day):
    """Get athletes available for a specific seat"""
    available = []
    current_lineup = st.session_state.lineups[event_num]
    
    for athlete in st.session_state.athletes:
        # Check if already assigned in this event
        if (athlete in current_lineup.get('athletes', []) or 
            athlete == current_lineup.get('coxswain')):
            continue
        
        # Check day availability
        if not athlete.is_available_on_day(event_day):
            continue
        
        # Check basic eligibility
        if not _athlete_fits_basic_requirements_for_assignment(athlete, requirements):
            continue
        
        available.append(athlete)
    
    return available

def _get_available_coxswains(event_num, event_day):
    """Get available coxswains for an event"""
    available = []
    current_lineup = st.session_state.lineups[event_num]
    
    for athlete in st.session_state.athletes:
        if not athlete.can_cox:
            continue
        
        # Check if already assigned in this event
        if (athlete in current_lineup.get('athletes', []) or 
            athlete == current_lineup.get('coxswain')):
            continue
        
        # Check day availability
        if not athlete.is_available_on_day(event_day):
            continue
        
        available.append(athlete)
    
    return available

def _athlete_fits_basic_requirements_for_assignment(athlete, requirements):
    """Check basic requirements for seat assignment"""
    # Gender check
    if requirements['gender_req'] == 'M' and athlete.gender != 'M':
        return False
    if requirements['gender_req'] == 'F' and athlete.gender != 'F':
        return False
    
    # Boat type compatibility
    if requirements['is_sculling'] and not athlete.can_scull:
        return False
    if not requirements['is_sculling'] and not (athlete.can_port or athlete.can_starboard):
        return False
    
    return True

def _remove_athlete_from_lineup(lineup, athlete):
    """Remove an athlete from all positions in a lineup"""
    # Remove from rower positions
    for i, rower in enumerate(lineup.get('athletes', [])):
        if rower == athlete:
            lineup['athletes'][i] = None
    
    # Remove from coxswain position
    if lineup.get('coxswain') == athlete:
        lineup['coxswain'] = None