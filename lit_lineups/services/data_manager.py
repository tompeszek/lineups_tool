"""
Data save/load manager for roster, lineups, equipment, and notes
"""
import json
import streamlit as st
from datetime import datetime, time
from models.athlete import Athlete
from models.boat import Boat
import os
from pathlib import Path

class DataManager:
    """Manager for saving and loading all application data"""
    
    def __init__(self):
        # Define preset datasets directory
        self.presets_dir = Path(__file__).parent.parent / "presets"
        self.presets_dir.mkdir(exist_ok=True)
    
    def get_available_presets(self, sort_by_date=True):
        """Get list of available preset files"""
        presets = []
        for file_path in self.presets_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Parse saved_at date for sorting (backwards compatible)
                saved_at_str = data.get('saved_at', 'Unknown')
                saved_at_datetime = None
                if saved_at_str != 'Unknown':
                    try:
                        saved_at_datetime = datetime.fromisoformat(saved_at_str.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        # Fallback to file modification time for older presets
                        saved_at_datetime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        saved_at_str = saved_at_datetime.isoformat()
                
                presets.append({
                    'filename': file_path.name,
                    'filepath': file_path,
                    'name': data.get('preset_name', file_path.stem),
                    'description': data.get('preset_description', 'No description'),
                    'saved_at': saved_at_str,
                    'saved_at_datetime': saved_at_datetime,
                    'athletes_count': len(data.get('athletes', [])),
                    'lineups_count': len(data.get('lineups', {})),
                    'boats_count': len(data.get('boats', [])),
                    'event_statuses_count': len(data.get('event_statuses', {})),
                    'has_notes': bool(data.get('notes', '').strip())
                })
            except Exception as e:
                st.warning(f"Could not read preset {file_path.name}: {e}")
        
        if sort_by_date and presets:
            # Sort by date (newest first), falling back to name for presets without dates
            return sorted(presets, key=lambda x: (x['saved_at_datetime'] or datetime.min, x['name']), reverse=True)
        else:
            return sorted(presets, key=lambda x: x['name'])
    
    def save_data(self, preset_name=None, preset_description=None):
        """Save all data to JSON format"""
        data = {
            "version": "1.2",
            "saved_at": datetime.now().isoformat(),
            "preset_name": preset_name,
            "preset_description": preset_description,
            "parameters": {
                "event_spacing_minutes": st.session_state.event_spacing_minutes,
                "min_gap_minutes": st.session_state.min_gap_minutes,
                "regatta_start_date": st.session_state.regatta_start_date.isoformat(),
                "morning_start_time": st.session_state.morning_start_time.isoformat(),
                "afternoon_start_time": st.session_state.afternoon_start_time.isoformat(),
                "exclude_lightweight": st.session_state.exclude_lightweight,
                "meet_minutes_before": st.session_state.meet_minutes_before,
                "launch_minutes_before": st.session_state.launch_minutes_before,
                "land_minutes_after": getattr(st.session_state, 'land_minutes_after', 15),
                "boats_per_race": getattr(st.session_state, 'boats_per_race', 8)
            },
            "athletes": self._serialize_athletes(),
            "lineups": self._serialize_lineups(),
            "selected_events": list(getattr(st.session_state, 'selected_events', set())),
            "boats": self._serialize_boats(),
            "boat_assignments": self._serialize_boat_assignments(),
            "event_statuses": getattr(st.session_state, 'event_statuses', {}),
            "notes": getattr(st.session_state, 'notes', '')
        }
        
        json_str = json.dumps(data, indent=2)
        return json_str, data
    
    def save_preset(self, preset_name, preset_description=""):
        """Save current state as a preset"""
        try:
            json_str, data = self.save_data(preset_name, preset_description)
            
            # Create safe filename
            safe_filename = "".join(c for c in preset_name if c.isalnum() or c in (' ', '_', '-')).strip()
            safe_filename = safe_filename.replace(' ', '_')
            filename = f"{safe_filename}.json"
            
            preset_path = self.presets_dir / filename
            
            with open(preset_path, 'w') as f:
                f.write(json_str)
            
            return {"success": True, "message": f"Preset '{preset_name}' saved successfully!", "filepath": preset_path}
            
        except Exception as e:
            return {"success": False, "message": f"Error saving preset: {str(e)}"}
    
    def get_most_recent_preset(self):
        """Get the most recently saved preset"""
        presets = self.get_available_presets(sort_by_date=True)
        return presets[0] if presets else None
    
    def load_preset(self, preset_filepath):
        """Load a preset by filepath"""
        try:
            with open(preset_filepath, 'r') as f:
                json_str = f.read()
            return self.load_data(json_str)
        except Exception as e:
            return {"success": False, "message": f"Error loading preset: {str(e)}"}
    
    def auto_load_most_recent_preset(self):
        """Automatically load the most recent preset if no data exists"""
        # Only auto-load if session is essentially empty
        if (len(getattr(st.session_state, 'athletes', [])) == 0 and 
            len(getattr(st.session_state, 'lineups', {})) == 0 and
            len(getattr(st.session_state, 'boats', [])) == 0):
            
            most_recent = self.get_most_recent_preset()
            if most_recent:
                result = self.load_preset(most_recent['filepath'])
                if result["success"]:
                    # Set a flag to indicate auto-loading happened
                    st.session_state.auto_loaded_preset = most_recent['name']
                    return {
                        "success": True, 
                        "message": f"Auto-loaded most recent preset: '{most_recent['name']}'",
                        "preset_name": most_recent['name']
                    }
                else:
                    return {"success": False, "message": f"Failed to auto-load preset: {result['message']}"}
        
        return {"success": False, "message": "Auto-load skipped - session already has data"}
    
    def delete_preset(self, preset_filepath):
        """Delete a preset file"""
        try:
            preset_filepath.unlink()
            return {"success": True, "message": "Preset deleted successfully!"}
        except Exception as e:
            return {"success": False, "message": f"Error deleting preset: {str(e)}"}
    
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
            st.session_state.land_minutes_after = params.get("land_minutes_after", 15)
            st.session_state.boats_per_race = params.get("boats_per_race", 8)
            
            if "regatta_start_date" in params:
                st.session_state.regatta_start_date = datetime.fromisoformat(params["regatta_start_date"]).date()
            
            # Handle both old and new time formats
            if "morning_start_time" in params:
                time_str = params["morning_start_time"]
                if 'T' in time_str:
                    st.session_state.morning_start_time = datetime.fromisoformat(time_str).time()
                else:
                    time_parts = time_str.split(':')
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                    st.session_state.morning_start_time = time(hour, minute, second)
            elif "regatta_start_time" in params:  # Backwards compatibility
                time_str = params["regatta_start_time"]
                if 'T' in time_str:
                    st.session_state.morning_start_time = datetime.fromisoformat(time_str).time()
                else:
                    time_parts = time_str.split(':')
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                    st.session_state.morning_start_time = time(hour, minute, second)
            
            if "afternoon_start_time" in params:
                time_str = params["afternoon_start_time"]
                if 'T' in time_str:
                    st.session_state.afternoon_start_time = datetime.fromisoformat(time_str).time()
                else:
                    time_parts = time_str.split(':')
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                    st.session_state.afternoon_start_time = time(hour, minute, second)
            
            # Load athletes - FORCE new list
            athletes_data = data.get("athletes", [])
            new_athletes = []
            for athlete_data in athletes_data:
                athlete = Athlete(
                    name=athlete_data["name"],
                    gender=athlete_data["gender"],
                    age=athlete_data["age"],
                    weight=athlete_data.get("weight", 160),
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
            
            # Load boats
            boats_data = data.get("boats", [])
            new_boats = []
            for boat_data in boats_data:
                boat = Boat(
                    name=boat_data["name"],
                    boat_type=boat_data["boat_type"],
                    num_seats=boat_data["num_seats"],
                    min_weight=boat_data["min_weight"],
                    max_weight=boat_data["max_weight"]
                )
                new_boats.append(boat)
            
            st.session_state.boats = new_boats
            print(f"Set {len(st.session_state.boats)} boats in session state")
            
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
            
            # Load boat assignments
            boat_assignments_data = data.get("boat_assignments", {})
            new_boat_assignments = {}
            for event_num_str, boat_data in boat_assignments_data.items():
                event_num = int(event_num_str)
                # Find matching boat from our loaded boats
                matching_boat = None
                for boat in st.session_state.boats:
                    if (boat.name == boat_data["name"] and 
                        boat.boat_type == boat_data["boat_type"]):
                        matching_boat = boat
                        break
                
                if matching_boat:
                    new_boat_assignments[event_num] = matching_boat
            
            st.session_state.boat_assignments = new_boat_assignments
            print(f"Set {len(st.session_state.boat_assignments)} boat assignments in session state")
            
            # Load event statuses
            event_statuses_data = data.get("event_statuses", {})
            # Convert string keys back to integers
            st.session_state.event_statuses = {int(k): v for k, v in event_statuses_data.items()}
            print(f"Loaded event statuses: {len(st.session_state.event_statuses)} events")
            
            # Load notes
            st.session_state.notes = data.get("notes", "")
            print(f"Loaded notes: {len(st.session_state.notes)} characters")
            
            # Force UI refresh for notes by incrementing refresh counter
            if 'notes_refresh_counter' not in st.session_state:
                st.session_state.notes_refresh_counter = 0
            st.session_state.notes_refresh_counter += 1
            
            # Load selected events
            if "selected_events" in data:
                st.session_state.selected_events = set(data["selected_events"])
            else:
                st.session_state.selected_events = set(st.session_state.lineups.keys())
            
            print(f"Set {len(st.session_state.selected_events)} selected events")
            
            preset_info = ""
            if data.get("preset_name"):
                preset_info = f" from preset '{data['preset_name']}'"
                # Update the currently loaded preset indicator
                st.session_state.auto_loaded_preset = data['preset_name']
            
            event_statuses_info = f", event statuses ({len(st.session_state.event_statuses)} events)" if st.session_state.event_statuses else ""
            notes_info = f", notes ({len(st.session_state.notes)} chars)" if st.session_state.notes else ""
            
            return {
                "success": True, 
                "message": f"Successfully loaded{preset_info}: {len(st.session_state.athletes)} athletes, {len(st.session_state.lineups)} lineups, {len(st.session_state.boats)} boats, {len(st.session_state.boat_assignments)} boat assignments{event_statuses_info}{notes_info}",
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
                "weight": athlete.weight,
                "can_port": athlete.can_port,
                "can_starboard": athlete.can_starboard,
                "can_scull": athlete.can_scull,
                "can_cox": athlete.can_cox,
                "preferred_events": athlete.preferred_events,
                "available_days": athlete.available_days
            })
        return athletes_data
    
    def _serialize_boats(self):
        """Convert boats to serializable format"""
        boats_data = []
        for boat in getattr(st.session_state, 'boats', []):
            boats_data.append({
                "name": boat.name,
                "boat_type": boat.boat_type,
                "num_seats": boat.num_seats,
                "min_weight": boat.min_weight,
                "max_weight": boat.max_weight
            })
        return boats_data
    
    def _serialize_boat_assignments(self):
        """Convert boat assignments to serializable format"""
        assignments_data = {}
        for event_num, boat in getattr(st.session_state, 'boat_assignments', {}).items():
            assignments_data[str(event_num)] = {
                "name": boat.name,
                "boat_type": boat.boat_type,
                "num_seats": boat.num_seats,
                "min_weight": boat.min_weight,
                "max_weight": boat.max_weight
            }
        return assignments_data
    
    def _serialize_lineups(self):
        """Convert lineups to serializable format"""
        lineups_data = {}
        for event_num, lineup in st.session_state.lineups.items():
            lineups_data[str(event_num)] = {
                "athletes": [self._athlete_to_dict(a) for a in lineup.get("athletes", [])],
                "coxswain": self._athlete_to_dict(lineup["coxswain"]) if lineup.get("coxswain") else None
            }
        return lineups_data
    
    def _athlete_to_dict(self, athlete):
        """Convert athlete object to dictionary"""
        if athlete is None:
            return None
        return {
            "name": athlete.name,
            "gender": athlete.gender,
            "age": athlete.age,
            "weight": athlete.weight,
            "can_port": athlete.can_port,
            "can_starboard": athlete.can_starboard,
            "can_scull": athlete.can_scull,
            "can_cox": athlete.can_cox,
            "preferred_events": athlete.preferred_events,
            "available_days": getattr(athlete, 'available_days', ["Thursday", "Friday", "Saturday", "Sunday"])
        }