"""
Issues analysis tab UI
"""
import streamlit as st
import pandas as pd
from datetime import timedelta
from collections import defaultdict
from models.constants import EVENTS_DATA
from utils.event_utils import get_event_time

def render_issues_tab():
    """Render the comprehensive issues analysis tab"""
    st.header("⚠️ Issues Analysis")
    
    if not st.session_state.lineups:
        st.info("No lineups created yet. Create some lineups to see issue analysis.")
        return
    
    # Calculate all issues
    athlete_conflicts = _check_athlete_conflicts()
    boat_conflicts = _check_boat_conflicts()
    unassigned_boats = _check_unassigned_boats()
    incomplete_lineups = _check_incomplete_lineups()
    weight_issues = _check_weight_issues()
    athlete_workload = _analyze_athlete_workload()
    age_category_issues = _check_age_category_issues()
    
    # Summary section at top
    st.subheader("📊 Issues Summary")
    
    total_issues = (len(athlete_conflicts) + len(boat_conflicts) + 
               len(unassigned_boats) + len(incomplete_lineups) + len(weight_issues) + len(age_category_issues))
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if athlete_conflicts:
            st.metric("Athlete Conflicts", len(athlete_conflicts), delta=None)
        else:
            st.metric("Athlete Conflicts", "0 ✅")
    
    with col2:
        if boat_conflicts:
            st.metric("Boat Conflicts", len(boat_conflicts), delta=None)
        else:
            st.metric("Boat Conflicts", "0 ✅")
    
    with col3:

        if incomplete_lineups:
            st.metric("Incomplete Lineups", len(incomplete_lineups), delta=None)
            st.warning(f"Found {len(incomplete_lineups)} incomplete lineups:")
            for lineup_issue in incomplete_lineups:
                st.write(f"• {lineup_issue}")        
        else:
            st.metric("Incomplete Lineups", "0 ✅")
    
    with col4:
        if unassigned_boats:
            st.metric("Missing Boats", len(unassigned_boats), delta=None)
        else:
            st.metric("Missing Boats", "0 ✅")    
    
    with col5:
        if weight_issues:
            st.metric("Weight Issues", len(weight_issues), delta=None)
        else:
            st.metric("Weight Issues", "0 ✅")

    with col6:
        if age_category_issues:
            st.metric("Age Category Issues", len(age_category_issues), delta=None)
        else:
            st.metric("Age Category Issues", "0 ✅")
    
    if total_issues == 0:
        st.success("🎉 No issues found! Your schedule looks good.")
    else:
        st.error(f"Found {total_issues} issues that need attention.")
    
    # Detailed issue sections
    if athlete_conflicts:
        st.subheader("👥 Athlete Scheduling Conflicts")
        st.error(f"Found {len(athlete_conflicts)} athlete conflicts:")
        for conflict in athlete_conflicts:
            st.write(f"• {conflict}")
    
    if boat_conflicts:
        st.subheader("⛵ Boat Assignment Conflicts")
        st.error(f"Found {len(boat_conflicts)} boat conflicts:")
        for conflict in boat_conflicts:
            st.write(f"• {conflict}")
    
    if unassigned_boats:
        st.subheader("🚫 Events Without Boats")
        st.warning(f"Found {len(unassigned_boats)} events without boat assignments:")
        for event in unassigned_boats:
            st.write(f"• {event}")
    
    if weight_issues:
        st.subheader("⚖️ Boat Weight Compatibility Issues")
        
        # Separate by severity
        critical_weight = [issue for issue in weight_issues if "❌" in issue]
        warning_weight = [issue for issue in weight_issues if "⚠️" in issue]
        
        if critical_weight:
            st.error(f"Critical weight mismatches ({len(critical_weight)}):")
            for issue in critical_weight:
                st.write(f"• {issue}")
        
        if warning_weight:
            st.warning(f"Weight warnings ({len(warning_weight)}):")
            for issue in warning_weight:
                st.write(f"• {issue}")
    
    if age_category_issues:
        st.subheader("🎂 Age Category Compatibility Issues")
        
        # Separate by severity
        critical_age = [issue for issue in age_category_issues if "❌" in issue]
        warning_age = [issue for issue in age_category_issues if "⚠️" in issue]
        
        if critical_age:
            st.error(f"Critical age mismatches ({len(critical_age)}):")
            for issue in critical_age:
                st.write(f"• {issue}")
        
        if warning_age:
            st.warning(f"Age warnings ({len(warning_age)}):")
            for issue in warning_age:
                st.write(f"• {issue}")

    # Athlete workload analysis
    st.subheader("👤 Athlete Workload Analysis")
    
    if athlete_workload['overloaded']:
        st.warning("Athletes with heavy schedules (6+ events):")
        workload_df = pd.DataFrame(athlete_workload['overloaded'])
        st.dataframe(workload_df, use_container_width=True, hide_index=True)
    
    # Daily workload breakdown
    if athlete_workload['daily_breakdown']:
        st.write("**Daily event breakdown:**")
        daily_df = pd.DataFrame(athlete_workload['daily_breakdown'])
        st.dataframe(daily_df, use_container_width=True, hide_index=True)
    
    # Show athletes with no events
    if athlete_workload['unused']:
        st.info("Athletes not assigned to any events:")
        for athlete in athlete_workload['unused']:
            st.write(f"• {athlete}")
    
    # Equipment utilization
    st.subheader("⛵ Equipment Utilization")
    
    if hasattr(st.session_state, 'boats') and st.session_state.boats:
        boat_usage = _analyze_boat_usage()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Boat Usage Summary:**")
            if boat_usage['used']:
                for boat_name, events in boat_usage['used'].items():
                    st.write(f"• {boat_name}: {len(events)} events")
            else:
                st.write("No boats currently assigned")
        
        with col2:
            if boat_usage['unused']:
                st.write("**Unused Boats:**")
                for boat in boat_usage['unused']:
                    st.write(f"• {boat}")
            else:
                st.success("All boats are in use!")

def _check_athlete_conflicts():
    """Check for athlete scheduling conflicts"""
    conflicts = []
    
    # Build athlete event schedule
    athlete_events = defaultdict(list)
    
    for event_num, lineup in st.session_state.lineups.items():
        event_time = get_event_time(event_num, st.session_state.event_spacing_minutes)
        
        # Add rowers
        for athlete in lineup.get('athletes', []):
            if athlete is not None:
                athlete_events[athlete.name].append((event_num, event_time))
        
        # Add coxswain
        if lineup.get('coxswain'):
            athlete_events[lineup['coxswain'].name].append((event_num, event_time))
    
    # Check for conflicts
    for athlete_name, events in athlete_events.items():
        if len(events) <= 1:
            continue
        
        # Sort by time
        events.sort(key=lambda x: x[1])
        
        for i in range(len(events) - 1):
            current_event, current_time = events[i]
            next_event, next_time = events[i + 1]
            
            gap_minutes = (next_time - current_time).total_seconds() / 60
            
            if 0 < gap_minutes < st.session_state.min_gap_minutes:
                conflicts.append(f"{athlete_name}: {gap_minutes:.0f} min gap between events {current_event} and {next_event}")
    
    return conflicts

def _check_boat_conflicts():
    """Check for boat assignment conflicts"""
    conflicts = []
    
    if not hasattr(st.session_state, 'boat_assignments'):
        return conflicts
    
    # Group events by boat
    boat_events = defaultdict(list)
    
    for event_num, boat in st.session_state.boat_assignments.items():
        event_time = get_event_time(event_num, st.session_state.event_spacing_minutes)
        launch_time = event_time - timedelta(minutes=st.session_state.launch_minutes_before)
        land_time = event_time + timedelta(minutes=st.session_state.land_minutes_after)
        
        boat_events[boat.name].append((event_num, launch_time, land_time))
    
    # Check for overlaps
    for boat_name, events in boat_events.items():
        if len(events) <= 1:
            continue
        
        # Sort by launch time
        events.sort(key=lambda x: x[1])
        
        for i in range(len(events) - 1):
            current_event, current_launch, current_land = events[i]
            next_event, next_launch, next_land = events[i + 1]
            
            # Check if there's overlap
            if current_land > next_launch:
                overlap_minutes = (current_land - next_launch).total_seconds() / 60
                conflicts.append(f"{boat_name}: {overlap_minutes:.0f} min overlap between events {current_event} and {next_event}")
    
    return conflicts

def _check_incomplete_lineups():
    """Check for lineups with empty seats"""
    incomplete = []
    
    for event_num, lineup in st.session_state.lineups.items():
        # Find event name and requirements
        event_name = "Unknown"
        for day, events in EVENTS_DATA.items():
            for num, name in events:
                if num == event_num:
                    event_name = name
                    break
        
        # Parse event requirements
        from utils.event_utils import parse_event_requirements
        try:
            requirements = parse_event_requirements(event_name)
        except:
            continue  # Skip if we can't parse requirements
        
        athletes = lineup.get('athletes', [])
        coxswain = lineup.get('coxswain')
        
        # Check if lineup has any athletes at all
        if not athletes and not coxswain:
            continue  # Skip completely empty lineups (not an issue)
        
        # Check for empty rower seats
        empty_seats = 0
        filled_seats = 0
        
        for i, athlete in enumerate(athletes):
            if athlete is None:
                empty_seats += 1
            else:
                filled_seats += 1
        
        # Only report if lineup is partially filled but incomplete
        if filled_seats > 0:  # Only check lineups that have at least one athlete
            if empty_seats > 0:
                incomplete.append(f"Event {event_num} ({event_name}): {empty_seats} empty rower seat{'s' if empty_seats != 1 else ''}")
            
            # Check for missing coxswain if required
            if requirements.get('has_cox', False) and not coxswain:
                incomplete.append(f"Event {event_num} ({event_name}): Missing required coxswain")
    
    return incomplete

def _check_unassigned_boats():
    """Check for events without boat assignments"""
    unassigned = []
    
    for event_num, lineup in st.session_state.lineups.items():
        # Only check events with athletes
        if lineup.get('athletes') and any(a is not None for a in lineup['athletes']):
            if not hasattr(st.session_state, 'boat_assignments') or event_num not in st.session_state.boat_assignments:
                # Find event name
                event_name = "Unknown"
                for day, events in EVENTS_DATA.items():
                    for num, name in events:
                        if num == event_num:
                            event_name = name
                            break
                
                unassigned.append(f"Event {event_num}: {event_name}")
    
    return unassigned

def _check_weight_issues():
    """Check for boat weight compatibility issues"""
    issues = []
    
    if not hasattr(st.session_state, 'boat_assignments'):
        return issues
    
    for event_num, boat in st.session_state.boat_assignments.items():
        lineup = st.session_state.lineups.get(event_num, {})
        athletes = [a for a in lineup.get('athletes', []) if a is not None]
        
        if not athletes:
            continue
        
        avg_weight = sum(a.weight for a in athletes) / len(athletes)
        weight_check = boat.weight_check(avg_weight)
        
        # Find event name
        event_name = "Unknown"
        for day, events in EVENTS_DATA.items():
            for num, name in events:
                if num == event_num:
                    event_name = name
                    break
        
        if weight_check == "bad":
            issues.append(f"❌ Event {event_num} ({event_name}): {boat.name} - avg weight {avg_weight:.1f}lbs outside range {boat.min_weight}-{boat.max_weight}lbs")
        elif weight_check == "warning":
            issues.append(f"⚠️ Event {event_num} ({event_name}): {boat.name} - avg weight {avg_weight:.1f}lbs near range limits {boat.min_weight}-{boat.max_weight}lbs")
    
    return issues

def _analyze_athlete_workload():
    """Analyze athlete workload and distribution"""
    athlete_events = defaultdict(list)
    athlete_daily_events = defaultdict(lambda: defaultdict(int))
    
    # Count events per athlete
    for event_num, lineup in st.session_state.lineups.items():
        # Find event day
        event_day = None
        for day, events in EVENTS_DATA.items():
            for num, name in events:
                if num == event_num:
                    event_day = day
                    break
            if event_day:
                break
        
        # Count rowers
        for athlete in lineup.get('athletes', []):
            if athlete is not None:
                athlete_events[athlete.name].append(event_num)
                if event_day:
                    athlete_daily_events[athlete.name][event_day] += 1
        
        # Count coxswain
        if lineup.get('coxswain'):
            athlete_events[lineup['coxswain'].name].append(event_num)
            if event_day:
                athlete_daily_events[lineup['coxswain'].name][event_day] += 1
    
    # Find overloaded athletes (6+ events)
    overloaded = []
    for athlete_name, events in athlete_events.items():
        if len(events) >= 6:
            overloaded.append({
                'Athlete': athlete_name,
                'Total Events': len(events),
                'Events': ', '.join(map(str, sorted(events)))
            })
    
    # Daily breakdown for busy athletes
    daily_breakdown = []
    for athlete_name, daily_counts in athlete_daily_events.items():
        if sum(daily_counts.values()) >= 2:  # Athletes with 2+ events
            row = {'Athlete': athlete_name}
            for day in ['Thursday', 'Friday', 'Saturday', 'Sunday']:
                row[day] = daily_counts.get(day, 0)
            row['Total'] = sum(daily_counts.values())
            daily_breakdown.append(row)
    
    # Sort by total events
    daily_breakdown.sort(key=lambda x: x['Total'], reverse=True)
    
    # Find unused athletes
    all_athlete_names = {a.name for a in st.session_state.athletes}
    used_athlete_names = set(athlete_events.keys())
    unused = list(all_athlete_names - used_athlete_names)
    
    return {
        'overloaded': overloaded,
        'daily_breakdown': daily_breakdown,
        'unused': unused
    }

def _analyze_boat_usage():
    """Analyze boat usage and availability"""
    used_boats = defaultdict(list)
    
    if hasattr(st.session_state, 'boat_assignments'):
        for event_num, boat in st.session_state.boat_assignments.items():
            used_boats[boat.name].append(event_num)
    
    # Find unused boats
    all_boat_names = {boat.name for boat in getattr(st.session_state, 'boats', [])}
    used_boat_names = set(used_boats.keys())
    unused_boats = list(all_boat_names - used_boat_names)
    
    return {
        'used': dict(used_boats),
        'unused': unused_boats
    }

def _check_age_category_issues():
    """Check for age category mismatches with boats"""
    issues = []
    
    if not hasattr(st.session_state, 'boat_assignments'):
        return issues
    
    for event_num, boat in st.session_state.boat_assignments.items():
        lineup = st.session_state.lineups.get(event_num, {})
        
        # Find event name and parse age category
        event_name = "Unknown"
        for day, events in EVENTS_DATA.items():
            for num, name in events:
                if num == event_num:
                    event_name = name
                    break
        
        if event_name == "Unknown":
            continue
        
        # Extract age category from event name (e.g., "Master E", "Master B", etc.)
        event_age_category = None
        if "Master" in event_name:
            # Look for patterns like "Master E", "Master B", etc.
            parts = event_name.split()
            for i, part in enumerate(parts):
                if part == "Master" and i + 1 < len(parts):
                    next_part = parts[i + 1]
                    if len(next_part) == 1 and next_part.isalpha():
                        event_age_category = next_part.upper()
                        break
        
        if not event_age_category or not boat.year:
            continue  # Skip if we can't determine age category or boat year
        
        # Calculate boat age (assuming current year is 2025)
        current_year = 2025
        boat_age = current_year - boat.year
        
        # Define age category requirements (approximate boat age ranges)
        # These are typical masters rowing age categories and corresponding boat age limits
        age_category_limits = {
            'A': {'min_boat_age': 0, 'max_boat_age': 15},    # 27-35: Can use newer boats
            'B': {'min_boat_age': 0, 'max_boat_age': 20},    # 36-42: Can use fairly new boats
            'C': {'min_boat_age': 0, 'max_boat_age': 25},    # 43-49: Can use moderately aged boats
            'D': {'min_boat_age': 0, 'max_boat_age': 30},    # 50-56: Can use older boats
            'E': {'min_boat_age': 0, 'max_boat_age': 35},    # 57-63: Can use quite old boats
            'F': {'min_boat_age': 0, 'max_boat_age': 40},    # 64-70: Can use very old boats
            'G': {'min_boat_age': 0, 'max_boat_age': 50},    # 71+: Can use any age boat
        }
        
        if event_age_category in age_category_limits:
            limits = age_category_limits[event_age_category]
            
            if boat_age < limits['min_boat_age']:
                # Boat is too new/young for this age category (critical)
                issues.append(f"❌ Event {event_num} ({event_name}): {boat.name} ({boat.year}) is too new for Master {event_age_category} category")
            elif boat_age > limits['max_boat_age']:
                # Boat is too old for this age category (warning)
                issues.append(f"⚠️ Event {event_num} ({event_name}): {boat.name} ({boat.year}) may be too old for Master {event_age_category} category")
    
    return issues