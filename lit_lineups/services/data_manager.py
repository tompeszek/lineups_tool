"""
Data save/load manager for roster and lineups
"""
import json
import streamlit as st
from datetime import datetime, time
from models.athlete import Athlete

class DataManager:
    """Manager for saving and loading all application data"""
    
    def save_data(self):
        """Save all data to JSON format"""
        data = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "parameters": {
                "event_spacing_minutes": st.session_state.event_spacing_minutes,
                "min_gap_minutes": st.session_state.min_gap_minutes,
                "regatta_start_date": st.session_state.regatta_start_date.isoformat(),
                "regatta_start_time": st.session_state.regatta_start_time.isoformat(),
                "exclude_lightweight": st.session_state.exclude_lightweight,
                "meet_minutes_before": st.session_state.meet_minutes_before,
                "launch_minutes_before": st.session_state.launch_minutes_before
            },
            "athletes": self._serialize_athletes(),
            "lineups": self._serialize_lineups(),
            "selected_events": list(getattr(st.session_state, 'selected_events', set()))
        }
        
        json_str = json.dumps(data, indent=2)
        return json_str
    
    def load_data(self, json_str):
        """Load data from JSON string"""
        import traceback
        
        try:
            data = json.loads(json_str)
            
            # Debug: Print what we're trying to load
            print(f"Loading data with {len(data.get('athletes', []))} athletes and {len(data.get('lineups', {}))} lineups")
            
            # Load parameters first
            params = data.get("parameters", {})
            st.session_state.event_spacing_minutes = params.get("event_spacing_minutes", 4)
            st.session_state.min_gap_minutes = params.get("min_gap_minutes", 30)
            st.session_state.exclude_lightweight = params.get("exclude_lightweight", True)
            st.session_state.meet_minutes_before = params.get("meet_minutes_before", 40)
            st.session_state.launch_minutes_before = params.get("launch_minutes_before", 30)
            
            if "regatta_start_date" in params:
                st.session_state.regatta_start_date = datetime.fromisoformat(params["regatta_start_date"]).date()
            if "regatta_start_time" in params:
                time_str = params["regatta_start_time"]
                if 'T' in time_str:
                    st.session_state.regatta_start_time = datetime.fromisoformat(time_str).time()
                else:
                    time_parts = time_str.split(':')
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                    st.session_state.regatta_start_time = time(hour, minute, second)
            
            # Load athletes - FORCE new list
            athletes_data = data.get("athletes", [])
            new_athletes = []
            for athlete_data in athletes_data:
                athlete = Athlete(
                    name=athlete_data["name"],
                    gender=athlete_data["gender"],
                    age=athlete_data["age"],
                    can_port=athlete_data.get("can_port", True),
                    can_starboard=athlete_data.get("can_starboard", True),
                    can_scull=athlete_data.get("can_scull", True),
                    can_cox=athlete_data.get("can_cox", False),
                    preferred_events=athlete_data.get("preferred_events", []),
                    available_days=athlete_data.get("available_days", ["Thursday", "Friday", "Saturday", "Sunday"])
                )
                new_athletes.append(athlete)
            
            st.session_state.athletes = new_athletes
            print(f"Set {len(st.session_state.athletes)} athletes in session state")
            
            # Load lineups - FORCE new dict
            lineups_data = data.get("lineups", {})
            new_lineups = {}
            for event_num_str, lineup_data in lineups_data.items():
                event_num = int(event_num_str)
                
                # Reconstruct athletes list for this lineup
                athletes_in_lineup = []
                for athlete_dict in lineup_data.get("athletes", []):
                    if athlete_dict is None:
                        athletes_in_lineup.append(None)
                    else:
                        # Find matching athlete from our loaded roster
                        matching_athlete = None
                        for athlete in st.session_state.athletes:
                            if (athlete.name == athlete_dict["name"] and 
                                athlete.gender == athlete_dict["gender"] and 
                                athlete.age == athlete_dict["age"]):
                                matching_athlete = athlete
                                break
                        athletes_in_lineup.append(matching_athlete)
                
                # Reconstruct coxswain
                cox_data = lineup_data.get("coxswain")
                coxswain = None
                if cox_data:
                    for athlete in st.session_state.athletes:
                        if (athlete.name == cox_data["name"] and 
                            athlete.gender == cox_data["gender"] and 
                            athlete.age == cox_data["age"]):
                            coxswain = athlete
                            break
                
                new_lineups[event_num] = {
                    "athletes": athletes_in_lineup,
                    "coxswain": coxswain
                }
            
            st.session_state.lineups = new_lineups
            print(f"Set {len(st.session_state.lineups)} lineups in session state")
            
            # Load selected events
            if "selected_events" in data:
                st.session_state.selected_events = set(data["selected_events"])
            else:
                st.session_state.selected_events = set(st.session_state.lineups.keys())
            
            print(f"Set {len(st.session_state.selected_events)} selected events")
            
            return {
                "success": True, 
                "message": f"Successfully loaded {len(st.session_state.athletes)} athletes, {len(st.session_state.lineups)} lineups, and {len(st.session_state.selected_events)} selected events",
                "timestamp": data.get('saved_at', 'unknown time')
            }
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            print(traceback.format_exc())
            return {
                "success": False, 
                "message": f"Error loading data: {str(e)}",
                "traceback": traceback.format_exc()
            }
    
    def _serialize_athletes(self):
        """Convert athletes to serializable format"""
        athletes_data = []
        for athlete in st.session_state.athletes:
            athletes_data.append({
                "name": athlete.name,
                "gender": athlete.gender,
                "age": athlete.age,
                "can_port": athlete.can_port,
                "can_starboard": athlete.can_starboard,
                "can_scull": athlete.can_scull,
                "can_cox": athlete.can_cox,
                "preferred_events": athlete.preferred_events,
                "available_days": athlete.available_days
            })
        return athletes_data
    
    def _deserialize_athletes(self, athletes_data):
        """Convert serialized data back to Athlete objects"""
        athletes = []
        for data in athletes_data:
            athlete = Athlete(
                name=data["name"],
                gender=data["gender"],
                age=data["age"],
                can_port=data.get("can_port", True),
                can_starboard=data.get("can_starboard", True),
                can_scull=data.get("can_scull", True),
                can_cox=data.get("can_cox", False),
                preferred_events=data.get("preferred_events", []),
                available_days=data.get("available_days", ["Thursday", "Friday", "Saturday", "Sunday"])
            )
            athletes.append(athlete)
        return athletes
    
    def _serialize_lineups(self):
        """Convert lineups to serializable format"""
        lineups_data = {}
        for event_num, lineup in st.session_state.lineups.items():
            lineups_data[str(event_num)] = {
                "athletes": [self._athlete_to_dict(a) for a in lineup.get("athletes", [])],
                "coxswain": self._athlete_to_dict(lineup["coxswain"]) if lineup.get("coxswain") else None
            }
        return lineups_data
    
    def _deserialize_lineups(self, lineups_data):
        """Convert serialized lineups back to lineup format"""
        lineups = {}
        for event_num_str, lineup_data in lineups_data.items():
            event_num = int(event_num_str)
            lineups[event_num] = {
                "athletes": [self._dict_to_athlete(a_dict) for a_dict in lineup_data.get("athletes", [])],
                "coxswain": self._dict_to_athlete(lineup_data["coxswain"]) if lineup_data.get("coxswain") else None
            }
        return lineups
    
    def _athlete_to_dict(self, athlete):
        """Convert athlete object to dictionary"""
        if athlete is None:
            return None
        return {
            "name": athlete.name,
            "gender": athlete.gender,
            "age": athlete.age,
            "can_port": athlete.can_port,
            "can_starboard": athlete.can_starboard,
            "can_scull": athlete.can_scull,
            "can_cox": athlete.can_cox,
            "preferred_events": athlete.preferred_events,
            "available_days": getattr(athlete, 'available_days', ["Thursday", "Friday", "Saturday", "Sunday"])
        }
    
    def _dict_to_athlete(self, athlete_dict):
        """Convert dictionary back to athlete object"""
        if athlete_dict is None:
            return None
        
        # Find the corresponding athlete in the current roster
        for athlete in st.session_state.athletes:
            if (athlete.name == athlete_dict["name"] and 
                athlete.gender == athlete_dict["gender"] and 
                athlete.age == athlete_dict["age"]):
                return athlete
        
        # If not found, create a new athlete (shouldn't happen with proper workflow)
        return Athlete(
            name=athlete_dict["name"],
            gender=athlete_dict["gender"],
            age=athlete_dict["age"],
            can_port=athlete_dict.get("can_port", True),
            can_starboard=athlete_dict.get("can_starboard", True),
            can_scull=athlete_dict.get("can_scull", True),
            can_cox=athlete_dict.get("can_cox", False),
            preferred_events=athlete_dict.get("preferred_events", []),
            available_days=athlete_dict.get("available_days", ["Thursday", "Friday", "Saturday", "Sunday"])
        )