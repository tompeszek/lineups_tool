# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Overview

This is a Streamlit-based rowing lineup management application designed for regatta event planning and athlete assignments. The app manages athletes, boats, event lineups, and scheduling for rowing competitions.

## Development Commands

### Running the Application
```bash
cd lit_lineups
streamlit run app.py
```

### Installing Dependencies
```bash
pip install -r lit_lineups/requirements.txt
```

### Environment Setup
The application uses a virtual environment in `venv/`. Activate with:
```bash
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### Deployment
- **Railway**: Configured via `railway.toml` and `Procfile`
- **Heroku**: Uses `Procfile` for deployment
- Port configuration is handled automatically via `$PORT` environment variable

## Architecture

### Core Models (`lit_lineups/models/`)
- **Athlete**: Individual rower with preferences, availability, and physical attributes
- **Boat**: Physical boats with weight limits and rigging configurations  
- **Session State**: Centralized state management for all application data
- **Constants**: Event data, age categories, and regatta information

### Data Flow
1. **Data Management** (`services/data_manager.py`): Handles save/load of presets as JSON
2. **Auto Assignment** (`services/auto_assignment.py`): Automatically assigns athletes to preferred events
3. **Event Utils** (`utils/event_utils.py`): Parses event requirements and boat compatibility
4. **Lineup Validation** (`services/lineup_validator.py`): Ensures lineups meet event requirements

### UI Structure (`lit_lineups/ui/`)
Multi-tab interface with specialized views:
- **Data Tab**: Import/export functionality and preset management
- **Roster Tab**: Athlete management with bulk operations
- **Lineup Tab**: Event-specific athlete assignments
- **Equipment Tab**: Boat fleet management and assignments
- **Schedule Tab**: Timeline view with conflict detection
- **Assignments Overview**: Grid view of all athlete assignments
- **Athlete Tab**: Individual athlete schedule view
- **Issues Tab**: Validation problems and conflicts
- **Notes Tab**: Session notes and comments

### Key Features
- **Event Compatibility**: Automatic checking of athlete eligibility (age, gender, boat type)
- **Weight Validation**: Boat weight limits with color-coded warnings
- **Schedule Conflicts**: Detection of athlete double-bookings
- **Flexible Boat Rigging**: Support for boats that can be rigged as sweep or sculling
- **Preset System**: Save/load complete regatta configurations

### Session State Management
All application data is stored in Streamlit's session state:
- `athletes`: List of Athlete objects
- `boats`: List of Boat objects  
- `lineups`: Dict mapping event numbers to athlete assignments
- `boat_assignments`: Dict mapping events to assigned boats
- `selected_events`: Set of events being actively managed
- `event_statuses`: Dict of event-specific status information
- `notes`: String containing session notes

### Data Persistence
- **JSON Format**: All data serializes to/from JSON for presets
- **Preset Directory**: `lit_lineups/presets/` contains saved configurations
- **Auto-loading**: Most recent preset automatically loads on app startup if session is empty
- **Smart Sorting**: Presets sorted by save date (newest first) with fallback to alphabetical
- **Backwards Compatibility**: Older presets without timestamps use file modification time
- **Sample Data**: Built-in athlete roster and boat fleet for testing

### Preset System Features
- **Auto-load on Startup**: Automatically loads the most recent preset when app starts fresh
- **Date-based Sorting**: Presets displayed newest first by default, with option to sort by name
- **Visual Indicators**: Most recent preset marked with 🌟 in the UI
- **Session Tracking**: Shows which preset is currently loaded
- **Backwards Compatible**: Handles presets from older versions gracefully