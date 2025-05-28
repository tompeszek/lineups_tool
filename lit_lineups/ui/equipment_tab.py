"""
Equipment requirements tab UI
"""
import streamlit as st
import pandas as pd
from utils.equipment_utils import calculate_equipment_needs

def render_equipment_tab():
    """Render the equipment requirements tab"""
    st.header("Equipment Requirements")
    
    if not st.session_state.lineups:
        st.info("No lineups created yet.")
        return
    
    equipment_needs = calculate_equipment_needs(st.session_state.lineups)
    
    if not equipment_needs:
        st.info("No equipment requirements yet - create some lineups first!")
        return
    
    st.subheader("Minimum Equipment Needed")
    
    # Display as a nice table
    equipment_data = [{'Boat Type': boat_type, 'Quantity': quantity} 
                    for boat_type, quantity in equipment_needs.items()]
    
    df = pd.DataFrame(equipment_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Equipment substitution notes
    st.subheader("Equipment Substitution Options")
    st.info("""
    **Boat Substitutions:**
    - A 4- (Four) can be used as a 4x (Quad Scull) 
    - A 2x (Double Scull) can be used as a 2- (Pair)
    - Consider these substitutions to minimize total equipment needs
    """)
    
    # Calculate optimized equipment needs
    st.subheader("Optimized Equipment List")
    _show_optimized_equipment(equipment_needs)

def _show_optimized_equipment(equipment_needs):
    """Show optimized equipment list with substitutions"""
    optimized = equipment_needs.copy()
    
    # Apply substitutions
    if '4x (Quad Scull)' in optimized and '4- (Four)' in optimized:
        total_fours = max(optimized['4x (Quad Scull)'], optimized['4- (Four)'])
        st.write(f"• {total_fours} Four-seat boats (can serve as both 4+ and 4x)")
        optimized.pop('4x (Quad Scull)', None)
        optimized.pop('4- (Four)', None)
    
    if '2x (Double Scull)' in optimized and '2- (Pair)' in optimized:
        total_pairs = max(optimized['2x (Double Scull)'], optimized['2- (Pair)'])
        st.write(f"• {total_pairs} Pair boats (can serve as both 2- and 2x)")
        optimized.pop('2x (Double Scull)', None)
        optimized.pop('2- (Pair)', None)
    
    # Show remaining equipment
    for boat_type, quantity in optimized.items():
        st.write(f"• {quantity} {boat_type}")