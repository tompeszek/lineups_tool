"""
Roster management tab UI
"""
import streamlit as st
import pandas as pd
from models.athlete import Athlete, create_sample_roster
from models.constants import EVENTS_DATA
from services.auto_assignment import AutoAssignment


def render_roster_tab():
    """Render the roster management tab"""
    st.header("Athlete Roster")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("Load Sample Roster"):
            st.session_state.athletes = create_sample_roster()
            # Clear any existing lineups when loading new roster
            st.session_state.lineups = {}
            st.success("Sample roster loaded!")
    
    with col2:
        if st.button("Auto-Assign Preferred"):
            if st.session_state.athletes:
                auto_assigner = AutoAssignment()
                result = auto_assigner.assign_all_preferred_events()
                
                if result["success"]:
                    st.success(f"Made {result['assignments_made']} automatic assignments!")
                    if result["issues"]:
                        st.warning("Some issues encountered:")
                        for issue in result["issues"]:
                            st.write(f"- {issue}")
                else:
                    st.error(result["message"])
            else:
                st.error("No athletes to assign!")
    
    with col3:
        if st.button("Clear Roster"):
            st.session_state.athletes = []
            st.session_state.lineups = {}  # Clear all lineups since athletes no longer exist
            if hasattr(st.session_state, 'selected_events'):
                st.session_state.selected_events = set()  # Clear selected events
            st.success("Roster cleared! All lineups and event selections have been reset.")
    
    # Add new athlete
    st.subheader("Add New Athlete")
    with st.form("add_athlete"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Name")
            gender = st.selectbox("Gender", ["M", "F"])
        
        with col2:
            age = st.number_input("Age", min_value=18, max_value=100, value=25)
            can_cox = st.checkbox("Can Cox")
        
        with col3:
            can_port = st.checkbox("Can Row Port", value=True)
            can_starboard = st.checkbox("Can Row Starboard", value=True)
            can_scull = st.checkbox("Can Scull", value=True)
        
        # Day availability
        st.write("Available Days:")
        day_col1, day_col2, day_col3, day_col4 = st.columns(4)
        with day_col1:
            thu = st.checkbox("Thursday", value=True, key="thu")
        with day_col2:
            fri = st.checkbox("Friday", value=True, key="fri")
        with day_col3:
            sat = st.checkbox("Saturday", value=True, key="sat")
        with day_col4:
            sun = st.checkbox("Sunday", value=True, key="sun")
        
        preferred_events = st.text_area("Preferred Events (event numbers, one per line)")
        
        if st.form_submit_button("Add Athlete"):
            if name:
                # Parse preferred events as integers
                preferred_list = []
                if preferred_events:
                    for event_str in preferred_events.split('\n'):
                        event_str = event_str.strip()
                        if event_str:
                            try:
                                preferred_list.append(int(event_str))
                            except ValueError:
                                st.error(f"Invalid event number: {event_str}")
                                return
                
                available_days = []
                if thu: available_days.append("Thursday")
                if fri: available_days.append("Friday")
                if sat: available_days.append("Saturday")
                if sun: available_days.append("Sunday")
                
                if not available_days:
                    st.error("Please select at least one available day")
                else:
                    new_athlete = Athlete(name, gender, age, can_port, can_starboard, can_scull, 
                                        can_cox, preferred_list, available_days)
                    st.session_state.athletes.append(new_athlete)
                    st.success(f"Added {name} to roster!")
            else:
                st.error("Please enter a name")
    
    # Display current roster
    if st.session_state.athletes:
        st.subheader("Current Roster")
        roster_data = []
        for i, athlete in enumerate(st.session_state.athletes):
            # Format available days
            day_abbrevs = []
            for day in athlete.available_days:
                day_abbrevs.append(day[:3])  # Thu, Fri, Sat, Sun
            days_str = "/".join(day_abbrevs)
            
            # Format preferred events - show event names instead of numbers
            preferred_names = []
            for event_num in athlete.preferred_events[:2]:
                # Find event name
                for day, events in EVENTS_DATA.items():
                    for num, name in events:
                        if num == event_num:
                            preferred_names.append(f"{num}: {name}")
                            break
            
            preferred_str = ", ".join(preferred_names)
            if len(athlete.preferred_events) > 2:
                preferred_str += "..."
            
            roster_data.append({
                'Name': athlete.name,
                'Gender': athlete.gender,
                'Age': athlete.age,
                'Category': athlete.age_category,
                'Port': '✓' if athlete.can_port else '✗',
                'Starboard': '✓' if athlete.can_starboard else '✗',
                'Scull': '✓' if athlete.can_scull else '✗',
                'Cox': '✓' if athlete.can_cox else '✗',
                'Days': days_str,
                'Preferred Events': preferred_str
            })
        
        df = pd.DataFrame(roster_data)
        st.dataframe(df, use_container_width=True)
        
        # Edit and Delete athlete section
        st.subheader("Manage Athletes")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Edit Athlete**")
            athlete_to_edit = st.selectbox("Select athlete to edit", 
                                         [f"{a.name} ({a.gender}, {a.age})" for a in st.session_state.athletes],
                                         key="edit_selectbox")
            if st.button("Edit Selected Athlete"):
                idx = next(i for i, a in enumerate(st.session_state.athletes) 
                          if f"{a.name} ({a.gender}, {a.age})" == athlete_to_edit)
                st.session_state.editing_athlete_idx = idx
                st.rerun()
        
        with col2:
            st.write("**Remove Athlete**")
            athlete_to_delete = st.selectbox("Select athlete to remove", 
                                           [f"{a.name} ({a.gender}, {a.age})" for a in st.session_state.athletes],
                                           key="delete_selectbox")
            if st.button("Remove Selected Athlete"):
                idx = next(i for i, a in enumerate(st.session_state.athletes) 
                          if f"{a.name} ({a.gender}, {a.age})" == athlete_to_delete)
                removed = st.session_state.athletes.pop(idx)
                st.success(f"Removed {removed.name} from roster!")
                st.rerun()
    
    # Edit athlete form (only shown when editing)
    if hasattr(st.session_state, 'editing_athlete_idx') and st.session_state.editing_athlete_idx is not None:
        athlete = st.session_state.athletes[st.session_state.editing_athlete_idx]
        
        st.subheader(f"Edit {athlete.name}")
        with st.form("edit_athlete"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                edit_name = st.text_input("Name", value=athlete.name)
                edit_gender = st.selectbox("Gender", ["M", "F"], index=0 if athlete.gender == "M" else 1)
            
            with col2:
                edit_age = st.number_input("Age", min_value=18, max_value=100, value=athlete.age)
                edit_can_cox = st.checkbox("Can Cox", value=athlete.can_cox)
            
            with col3:
                edit_can_port = st.checkbox("Can Row Port", value=athlete.can_port)
                edit_can_starboard = st.checkbox("Can Row Starboard", value=athlete.can_starboard)
                edit_can_scull = st.checkbox("Can Scull", value=athlete.can_scull)
            
            # Day availability
            st.write("Available Days:")
            day_col1, day_col2, day_col3, day_col4 = st.columns(4)
            with day_col1:
                edit_thu = st.checkbox("Thursday", value="Thursday" in athlete.available_days, key="edit_thu")
            with day_col2:
                edit_fri = st.checkbox("Friday", value="Friday" in athlete.available_days, key="edit_fri")
            with day_col3:
                edit_sat = st.checkbox("Saturday", value="Saturday" in athlete.available_days, key="edit_sat")
            with day_col4:
                edit_sun = st.checkbox("Sunday", value="Sunday" in athlete.available_days, key="edit_sun")
            
            # Convert preferred events list to string for editing
            preferred_events_str = "\n".join(str(event) for event in athlete.preferred_events)
            edit_preferred_events = st.text_area("Preferred Events (event numbers, one per line)", 
                                               value=preferred_events_str)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Changes"):
                    if edit_name:
                        # Parse preferred events as integers
                        edit_preferred_list = []
                        if edit_preferred_events:
                            for event_str in edit_preferred_events.split('\n'):
                                event_str = event_str.strip()
                                if event_str:
                                    try:
                                        edit_preferred_list.append(int(event_str))
                                    except ValueError:
                                        st.error(f"Invalid event number: {event_str}")
                                        return
                        
                        edit_available_days = []
                        if edit_thu: edit_available_days.append("Thursday")
                        if edit_fri: edit_available_days.append("Friday")
                        if edit_sat: edit_available_days.append("Saturday")
                        if edit_sun: edit_available_days.append("Sunday")
                        
                        if not edit_available_days:
                            st.error("Please select at least one available day")
                        else:
                            # Update the athlete
                            updated_athlete = Athlete(edit_name, edit_gender, edit_age, edit_can_port, 
                                                    edit_can_starboard, edit_can_scull, edit_can_cox, 
                                                    edit_preferred_list, edit_available_days)
                            st.session_state.athletes[st.session_state.editing_athlete_idx] = updated_athlete
                            st.session_state.editing_athlete_idx = None
                            st.success(f"Updated {edit_name}!")
                            st.rerun()
                    else:
                        st.error("Please enter a name")
            
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.editing_athlete_idx = None
                    st.rerun()