"""
Automatic lineup assignment service
"""
import streamlit as st
from collections import defaultdict
from utils.event_utils import parse_event_requirements, find_event_details
from models.constants import EVENTS_DATA

class AutoAssignment:
    """Service for automatically assigning athletes to their preferred events"""
    
    def assign_all_preferred_events(self):
        """Automatically assign all athletes to their preferred events"""
        if not st.session_state.athletes:
            return {"success": False, "message": "No athletes to assign"}
        
        # Initialize selected_events if needed
        if 'selected_events' not in st.session_state:
            st.session_state.selected_events = set()
        
        # Clear existing lineups
        st.session_state.lineups = {}
        
        # Group athletes by preferred events
        event_preferences = defaultdict(list)
        for athlete in st.session_state.athletes:
            for event_num in athlete.preferred_events:
                event_preferences[event_num].append(athlete)
        
        assignments_made = 0
        issues = []
        
        # Process each preferred event
        for event_num, interested_athletes in event_preferences.items():
            result = self._assign_event(event_num, interested_athletes)
            if result["success"]:
                assignments_made += 1
                # Add event to selected events so it shows up in the lineup tab
                st.session_state.selected_events.add(event_num)
            else:
                issues.append(f"Event {event_num}: {result['message']}")
        
        return {
            "success": True,
            "assignments_made": assignments_made,
            "issues": issues
        }
    
    def _assign_event(self, event_num, interested_athletes):
        """Assign athletes to a specific event"""
        # Check if event exists and get details
        event_name, event_day = find_event_details(event_num)
        if not event_name:
            return {"success": False, "message": "Event not found"}
        
        # Get event requirements
        requirements = parse_event_requirements(event_name)
        
        # Filter athletes who are eligible and available
        eligible_athletes = []
        for athlete in interested_athletes:
            if (self._athlete_fits_basic_requirements(athlete, event_name) and 
                athlete.is_available_on_day(event_day)):
                eligible_athletes.append(athlete)
        
        # Allow partial lineups - just need at least 1 athlete
        if not eligible_athletes:
            return {"success": False, "message": "No eligible athletes available"}
        
        # Assign athletes
        lineup = {'athletes': [], 'coxswain': None}
        
        # Take as many athletes as we can, up to the requirement
        athletes_to_assign = min(len(eligible_athletes), requirements['num_rowers'])
        
        # For mixed events, try to balance genders if possible
        if requirements['gender_req'] == 'Mixed':
            men = [a for a in eligible_athletes if a.gender == 'M']
            women = [a for a in eligible_athletes if a.gender == 'F']
            needed_per_gender = requirements['num_rowers'] // 2
            
            # Take what we can get, preferring balance
            men_to_take = min(len(men), needed_per_gender, athletes_to_assign // 2)
            women_to_take = min(len(women), needed_per_gender, athletes_to_assign - men_to_take)
            
            lineup['athletes'].extend(men[:men_to_take])
            lineup['athletes'].extend(women[:women_to_take])
            
            # Fill remaining spots with any gender if we're short
            remaining_spots = athletes_to_assign - len(lineup['athletes'])
            remaining_athletes = [a for a in eligible_athletes if a not in lineup['athletes']]
            lineup['athletes'].extend(remaining_athletes[:remaining_spots])
        else:
            # For single-gender events or if age matters, try to optimize
            if self._check_age_eligibility(eligible_athletes, event_name, athletes_to_assign):
                best_combo = self._find_best_age_combination(eligible_athletes, athletes_to_assign, event_name)
                if best_combo:
                    lineup['athletes'] = best_combo
                else:
                    lineup['athletes'] = eligible_athletes[:athletes_to_assign]
            else:
                lineup['athletes'] = eligible_athletes[:athletes_to_assign]
        
        # Assign coxswain if needed - coxswain can be any gender/age
        if requirements['has_cox']:
            # Find ALL athletes who can cox and are available on this day (not just from interested_athletes)
            all_available_coxes = []
            for athlete in st.session_state.athletes:
                if (athlete.can_cox and 
                    athlete.is_available_on_day(event_day) and 
                    athlete not in lineup['athletes']):
                    all_available_coxes.append(athlete)
            
            if all_available_coxes:
                lineup['coxswain'] = all_available_coxes[0]
            else:
                # If no available cox, try to swap someone from the crew
                crew_coxes = [a for a in lineup['athletes'] if a.can_cox]
                if crew_coxes:
                    # Move a cox from crew to coxswain position, don't replace them
                    cox_to_move = crew_coxes[0]
                    lineup['athletes'].remove(cox_to_move)
                    lineup['coxswain'] = cox_to_move
        
        # Save the lineup with proper structure (array with None placeholders)
        final_lineup = {'athletes': [None] * requirements['num_rowers'], 'coxswain': None}
        
        # Fill in the assigned athletes
        for i, athlete in enumerate(lineup['athletes']):
            if i < len(final_lineup['athletes']):
                final_lineup['athletes'][i] = athlete
        
        final_lineup['coxswain'] = lineup.get('coxswain')
        
        st.session_state.lineups[event_num] = final_lineup
        
        rower_count = len([a for a in final_lineup['athletes'] if a is not None])
        cox_text = " + coxswain" if final_lineup['coxswain'] else ""
        partial_text = f" (partial: {rower_count}/{requirements['num_rowers']})" if rower_count < requirements['num_rowers'] else ""
        
        return {"success": True, "message": f"Assigned {rower_count} rowers{cox_text}{partial_text}"}
    
    def _athlete_fits_basic_requirements(self, athlete, event_name):
        """Check basic athlete eligibility for event"""
        from models.boat import BoatType
        
        # Gender check
        if 'Men\'s' in event_name and athlete.gender != 'M':
            return False
        if 'Women\'s' in event_name and athlete.gender != 'F':
            return False
        
        # Boat type compatibility
        boat = BoatType(event_name.split()[-1])
        if boat.is_sculling and not athlete.can_scull:
            return False
        if boat.is_sweep and not (athlete.can_port or athlete.can_starboard):
            return False
            
        return True
    
    def _check_age_eligibility(self, athletes, event_name, num_rowers):
        """Check if we can form a crew meeting age requirements"""
        import re
        from models.constants import AGE_CATEGORIES
        
        # Extract age requirements
        age_cats_in_event = re.findall(r'\b([A-K]{1,2}(?:-[A-K]{1,2})?)\b', event_name)
        if not age_cats_in_event:
            return True  # No age restriction
        
        # Find minimum age requirement
        min_required_age = None
        for cat_group in age_cats_in_event:
            if '-' in cat_group:
                start_cat = cat_group.split('-')[0]
            else:
                start_cat = cat_group
            
            if start_cat in AGE_CATEGORIES:
                cat_min_age = AGE_CATEGORIES[start_cat][0]
                if min_required_age is None or cat_min_age < min_required_age:
                    min_required_age = cat_min_age
        
        if min_required_age is None:
            return True
        
        # Check if any combination can meet the requirement
        from itertools import combinations
        for combo in combinations(athletes, num_rowers):
            avg_age = sum(a.age for a in combo) / len(combo)
            if avg_age >= min_required_age:
                return True
        
        return False
    
    def _find_best_age_combination(self, athletes, num_rowers, event_name):
        """Find the best combination of athletes that meets age requirements"""
        import re
        from itertools import combinations
        from models.constants import AGE_CATEGORIES
        
        # Extract age requirements
        age_cats_in_event = re.findall(r'\b([A-K]{1,2}(?:-[A-K]{1,2})?)\b', event_name)
        if not age_cats_in_event:
            return athletes[:num_rowers]  # No age restriction, take first N
        
        # Find minimum age requirement
        min_required_age = None
        for cat_group in age_cats_in_event:
            if '-' in cat_group:
                start_cat = cat_group.split('-')[0]
            else:
                start_cat = cat_group
            
            if start_cat in AGE_CATEGORIES:
                cat_min_age = AGE_CATEGORIES[start_cat][0]
                if min_required_age is None or cat_min_age < min_required_age:
                    min_required_age = cat_min_age
        
        if min_required_age is None:
            return athletes[:num_rowers]
        
        # Find valid combinations, prefer those closer to the minimum age
        valid_combos = []
        for combo in combinations(athletes, num_rowers):
            avg_age = sum(a.age for a in combo) / len(combo)
            if avg_age >= min_required_age:
                valid_combos.append((combo, avg_age))
        
        if valid_combos:
            # Sort by average age (closest to minimum first)
            valid_combos.sort(key=lambda x: x[1])
            return list(valid_combos[0][0])
        
        return None
    
    def _check_sweep_balance(self, athletes, num_rowers):
        """Check if we have adequate port/starboard coverage for sweep events"""
        port_capable = [a for a in athletes if a.can_port]
        starboard_capable = [a for a in athletes if a.can_starboard]
        
        needed_per_side = num_rowers // 2
        return len(port_capable) >= needed_per_side and len(starboard_capable) >= needed_per_side