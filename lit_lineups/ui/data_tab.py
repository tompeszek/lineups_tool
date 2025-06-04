import streamlit as st
from datetime import datetime
from services.data_manager import DataManager

def render_data_tab():
    """Render the data management tab"""
    st.header("💾 Data Management")
    
    data_manager = DataManager()
    
    # Show currently loaded preset info
    if hasattr(st.session_state, 'auto_loaded_preset') and st.session_state.auto_loaded_preset:
        st.info(f"📂 **{st.session_state.auto_loaded_preset}** is currently loaded")
    
    # Show auto-load messages compactly
    if hasattr(st.session_state, 'auto_load_message') and st.session_state.auto_load_message:
        col_msg, col_clear = st.columns([4, 1])
        with col_msg:
            st.success(st.session_state.auto_load_message)
        with col_clear:
            if st.button("✕", key="clear_auto_msg", help="Clear message"):
                del st.session_state.auto_load_message
                st.rerun()
    
    if hasattr(st.session_state, 'auto_load_error') and st.session_state.auto_load_error:
        col_err, col_clear = st.columns([4, 1])
        with col_err:
            st.error(f"Auto-load issue: {st.session_state.auto_load_error}")
        with col_clear:
            if st.button("✕", key="clear_auto_err", help="Clear error"):
                del st.session_state.auto_load_error
                st.rerun()
    
    # === PRESETS SECTION (TOP PRIORITY) ===
    st.subheader("📋 Presets")
    
    # Sort dropdown directly under the label
    sort_option = st.selectbox(
        "Sort by:",
        ["Most Recent", "Name"],
        key="preset_sort_option"
    )
    
    # LOAD EXISTING PRESETS SUBSECTION
    st.markdown("### 📂 Load Existing Presets")
    
    presets = data_manager.get_available_presets(sort_by_date=(sort_option == "Most Recent"))
    
    if not presets:
        st.info("💡 No saved presets found. Create your first preset below!")
    else:
        # Compact preset display - 3 per row
        cols_per_row = 3
        for i in range(0, len(presets), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, preset in enumerate(presets[i:i+cols_per_row]):
                with cols[j]:
                    with st.container(border=True):
                        # Compact preset info
                        most_recent_indicator = " 🌟" if i == 0 and j == 0 and sort_option == "Most Recent" else ""
                        st.markdown(f"**{preset['name']}**{most_recent_indicator}")
                        
                        # Compact stats
                        st.caption(f"👥 {preset['athletes_count']} • 🚣 {preset['lineups_count']} • ⛵ {preset['boats_count']}")
                        
                        # Compact date
                        if preset['saved_at'] != 'Unknown':
                            try:
                                saved_datetime = datetime.fromisoformat(preset['saved_at'].replace('Z', '+00:00'))
                                date_str = saved_datetime.strftime("%m/%d %H:%M")
                            except:
                                date_str = preset['saved_at'][:10]
                            st.caption(f"🕒 {date_str}")
                        
                        # Action buttons
                        col_load, col_del = st.columns([2, 1])
                        with col_load:
                            if st.button("Load", key=f"load_{preset['filename']}", use_container_width=True, type="primary"):
                                result = data_manager.load_preset(preset['filepath'])
                                if result["success"]:
                                    st.session_state.load_success_message = f"Loaded '{preset['name']}'!"
                                    st.rerun()
                                else:
                                    st.session_state.load_error_message = result["message"]
                        
                        with col_del:
                            confirm_key = f"confirm_delete_{preset['filename']}"
                            if st.session_state.get(confirm_key, False):
                                if st.button("✅", key=f"confirm_del_{preset['filename']}", use_container_width=True, help="Confirm delete"):
                                    result = data_manager.delete_preset(preset['filepath'])
                                    if result["success"]:
                                        st.success("Deleted!")
                                        st.session_state[confirm_key] = False
                                        st.rerun()
                            else:
                                if st.button("🗑️", key=f"delete_{preset['filename']}", use_container_width=True, help="Delete preset"):
                                    st.session_state[confirm_key] = True
                                    st.rerun()
    
    # Clear visual separation
    st.markdown("---")
    
    # SAVE NEW PRESET SUBSECTION
    st.markdown("### 💾 Save Current State as New Preset")
    
    with st.container(border=True):
        st.write("**Create a new preset from your current athlete roster, lineups, and boat assignments**")
        
        with st.form("save_preset_form", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                preset_name = st.text_input("Preset Name", placeholder="e.g., RowFest 2025 Setup")
            with col2:
                preset_description = st.text_input("Description (optional)", placeholder="Brief description...")
            with col3:
                save_button = st.form_submit_button("⭐ Save Preset", use_container_width=True, type="primary")
            
            if save_button:
                if preset_name.strip():
                    result = data_manager.save_preset(preset_name.strip(), preset_description.strip())
                    if result["success"]:
                        st.success("✅ Preset saved successfully!")
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.error("⚠️ Please enter a preset name")
    
    st.divider()
    
    # === IMPORT/EXPORT SECTION ===
    st.subheader("💾 Import & Export")
    
    # Two column layout for import/export
    import_col, export_col = st.columns(2)
    
    with import_col:
        st.markdown("**📤 Import Data**")
        uploaded_file = st.file_uploader("Upload a previously saved JSON file", type=['json'])
        if uploaded_file is not None:
            file_id = f"{uploaded_file.name}_{uploaded_file.size}"
            if file_id not in st.session_state.get('processed_files', set()):
                json_str = uploaded_file.read().decode('utf-8')
                result = data_manager.load_data(json_str)
                if result["success"]:
                    st.session_state.load_success_message = result["message"]
                    if 'processed_files' not in st.session_state:
                        st.session_state.processed_files = set()
                    st.session_state.processed_files.add(file_id)
                    st.rerun()
                else:
                    st.session_state.load_error_message = result["message"]
    
    with export_col:
        st.markdown("**📥 Export Data**")
        st.write("Download current state as a JSON file")
        if st.button("📥 Generate Download File", use_container_width=True):
            json_data, _ = data_manager.save_data()
            st.download_button(
                label="💾 Download JSON",
                data=json_data,
                file_name=f"rowing_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    
    # Show messages compactly at bottom
    if hasattr(st.session_state, 'load_success_message') and st.session_state.load_success_message:
        success_col, clear_col = st.columns([4, 1])
        with success_col:
            st.success(st.session_state.load_success_message)
        with clear_col:
            if st.button("✕", key="clear_success", help="Clear message"):
                st.session_state.load_success_message = None
                st.rerun()

    if hasattr(st.session_state, 'load_error_message') and st.session_state.load_error_message:
        error_col, clear_col = st.columns([4, 1])
        with error_col:
            st.error(f"Error: {st.session_state.load_error_message}")
        with clear_col:
            if st.button("✕", key="clear_error", help="Clear error"):
                st.session_state.load_error_message = None
                st.rerun()