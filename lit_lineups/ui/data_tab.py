import streamlit as st
from datetime import datetime
from services.data_manager import DataManager

def render_data_tab():
    """Render the data management tab"""
    st.header("Data Management")
    
    data_manager = DataManager()
    
    # Save section
    st.subheader("Save Data")
    st.write("Export all your roster, lineups, and settings to a JSON file.")

    if st.button("💾 Generate Save File", use_container_width=False):
        json_data = data_manager.save_data()
        st.download_button(
            label="📥 Download File",
            data=json_data,
            file_name=f"rowing_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            # use_container_width=False
        )
    
    st.divider()
    
    # Load section
    st.subheader("Load Data")
    st.write("Upload a previously saved JSON file to restore your data.")
    
    uploaded_file = st.file_uploader("Choose a JSON file", type=['json'])
    if uploaded_file is not None:
        # Create a unique identifier for this file
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        
        if file_id not in st.session_state.get('processed_files', set()):
            json_str = uploaded_file.read().decode('utf-8')
            result = data_manager.load_data(json_str)
            if result["success"]:
                st.session_state.load_success_message = f"Data loaded from {result.get('timestamp', 'file')}!"
                st.session_state.load_error_message = None
                
                # Track that we've processed this file
                if 'processed_files' not in st.session_state:
                    st.session_state.processed_files = set()
                st.session_state.processed_files.add(file_id)
                
                st.rerun()
            else:
                st.session_state.load_error_message = result["message"] + "\n\n" + result.get("traceback", "")
                st.session_state.load_success_message = None
    
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