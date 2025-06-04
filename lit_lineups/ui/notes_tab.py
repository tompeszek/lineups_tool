"""
Notes tab UI for free-form note taking
"""
import streamlit as st

def render_notes_tab():
    """Render the notes tab for free-form note taking"""
    st.header("Notes")
    
    # Initialize notes if needed
    if 'notes' not in st.session_state:
        st.session_state.notes = ""
    
    # Force widget refresh counter - increment when data loads
    if 'notes_refresh_counter' not in st.session_state:
        st.session_state.notes_refresh_counter = 0
    
    st.write("Use this space for free-form notes about your regatta, lineups, strategy, or anything else.")
    
    # Text area for notes - unique key based on refresh counter
    notes = st.text_area(
        "Notes",
        value=st.session_state.notes,
        height=400,
        help="Notes are automatically saved and will be included in presets and data exports",
        label_visibility="collapsed",
        key=f"notes_text_area_{st.session_state.notes_refresh_counter}"
    )
    
    # Update session state when notes change
    st.session_state.notes = notes
    
    # Show character count
    char_count = len(st.session_state.notes)
    st.caption(f"Characters: {char_count:,}")
    
    # Quick action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear Notes"):
            st.session_state.notes = ""
            st.rerun()
    
    with col2:
        # Copy to clipboard (uses markdown)
        if st.button("Copy Notes"):
            st.write("📋 Copy the text above manually")
    
    with col3:
        # Word count
        word_count = len(st.session_state.notes.split()) if st.session_state.notes.strip() else 0
        st.metric("Words", word_count)
    
    # Tips section
    with st.expander("💡 Notes Tips"):
        st.markdown("""
        **Your notes support:**
        - Plain text formatting
        - Line breaks and paragraphs
        - Lists and bullet points
        - Event planning and strategy notes
        - Boat assignment rationale
        - Weather or logistics considerations
        
        **Notes are automatically:**
        - Saved with your session
        - Included in preset saves
        - Exported with JSON downloads
        - Imported when loading presets
        """)