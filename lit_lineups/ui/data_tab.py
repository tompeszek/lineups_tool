import streamlit as st
from datetime import datetime
from services.data_manager import DataManager

def render_data_tab():
    """Render the data management tab"""
    st.header("Data Management")
    
    data_manager = DataManager()
    
    # Create three columns for the main sections
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.subheader("💾 Save Data")
        st.write("Export current state to a JSON file")
        
        if st.button("Generate Save File", use_container_width=True):
            json_data, _ = data_manager.save_data()
            st.download_button(
                label="📥 Download File",
                data=json_data,
                file_name=f"rowing_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        st.subheader("📤 Load Data")
        st.write("Upload a previously saved JSON file")
        
        uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])
        if uploaded_file is not None:
            # Create a unique identifier for this file
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            
            if file_id not in st.session_state.get('processed_files', set()):
                json_str = uploaded_file.read().decode('utf-8')
                result = data_manager.load_data(json_str)
                if result["success"]:
                    st.session_state.load_success_message = result["message"]
                    st.session_state.load_error_message = None
                    
                    # Track that we've processed this file
                    if 'processed_files' not in st.session_state:
                        st.session_state.processed_files = set()
                    st.session_state.processed_files.add(file_id)
                    
                    st.rerun()
                else:
                    st.session_state.load_error_message = result["message"] + "\n\n" + result.get("traceback", "")
                    st.session_state.load_success_message = None
    
    with col3:
        st.subheader("⭐ Save as Preset")
        st.write("Save current state as a reusable preset")
        
        with st.form("save_preset_form"):
            preset_name = st.text_input("Preset Name", placeholder="e.g., 'RowFest 2025 Base Setup'")
            preset_description = st.text_area("Description (optional)", placeholder="Brief description of this preset...")
            
            if st.form_submit_button("Save Preset", use_container_width=True):
                if preset_name.strip():
                    result = data_manager.save_preset(preset_name.strip(), preset_description.strip())
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
                else:
                    st.error("Please enter a preset name")
    
    st.divider()
    
    # Presets section
    st.subheader("📋 Available Presets")
    
    presets = data_manager.get_available_presets()
    
    if not presets:
        st.info("No presets available. Save your current state as a preset to get started!")
    else:
        # Display presets in a nice grid
        cols_per_row = 2
        for i in range(0, len(presets), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, preset in enumerate(presets[i:i+cols_per_row]):
                with cols[j]:
                    with st.container(border=True):
                        st.write(f"**{preset['name']}**")
                        if preset['description']:
                            st.write(f"*{preset['description']}*")
                        
                        st.write(f"📊 {preset['athletes_count']} athletes, {preset['lineups_count']} lineups, {preset['boats_count']} boats")
                        st.write(f"🕒 Saved: {preset['saved_at'][:10] if len(preset['saved_at']) > 10 else preset['saved_at']}")
                        
                        col_load, col_delete = st.columns(2)
                        
                        with col_load:
                            if st.button(f"Load", key=f"load_{preset['filename']}", use_container_width=True):
                                result = data_manager.load_preset(preset['filepath'])
                                if result["success"]:
                                    st.session_state.load_success_message = f"Loaded preset '{preset['name']}' successfully!"
                                    st.session_state.load_error_message = None
                                    st.rerun()
                                else:
                                    st.session_state.load_error_message = result["message"]
                                    st.session_state.load_success_message = None
                        
                        with col_delete:
                            confirm_key = f"confirm_delete_{preset['filename']}"
                            
                            # Check if we're in confirmation mode for this preset
                            if st.session_state.get(confirm_key, False):
                                # Show confirmation button
                                if st.button("✅ Confirm Delete", key=f"confirm_del_{preset['filename']}", 
                                           use_container_width=True, type="primary"):
                                    result = data_manager.delete_preset(preset['filepath'])
                                    if result["success"]:
                                        st.success(result["message"])
                                        # Clear the confirmation state
                                        st.session_state[confirm_key] = False
                                        st.rerun()
                                    else:
                                        st.error(result["message"])
                                        st.session_state[confirm_key] = False
                                
                                # Also show a cancel button
                                if st.button("❌ Cancel", key=f"cancel_del_{preset['filename']}", 
                                           use_container_width=True):
                                    st.session_state[confirm_key] = False
                                    st.rerun()
                            else:
                                # Show initial delete button
                                if st.button("🗑️", key=f"delete_{preset['filename']}", use_container_width=True, 
                                           help="Delete this preset"):
                                    st.session_state[confirm_key] = True
                                    st.rerun()
    
    st.divider()
    
    # Show messages
    if hasattr(st.session_state, 'load_success_message') and st.session_state.load_success_message:
        st.success(st.session_state.load_success_message)
        if st.button("Clear message"):
            st.session_state.load_success_message = None
            st.rerun()

    if hasattr(st.session_state, 'load_error_message') and st.session_state.load_error_message:
        st.error("**Error loading data:**")
        st.code(st.session_state.load_error_message)
        if st.button("Clear error"):
            st.session_state.load_error_message = None
            st.rerun()