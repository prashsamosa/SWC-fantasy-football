"""
Team Rosters page showing players on each team in the selected league.
This is the first page users should visit to load data into session state.
"""
import streamlit as st
import simple_api_client as swc
import pandas as pd
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__) 

# --- Page UI ---
st.header("🏈 Fantasy Football Team Rosters")
st.markdown("View all players on teams in your selected league.")

# Retrieve API base URL from session state
base_url = st.session_state['base_url']

# --- Data Loading ---
try:
    # Show a spinner while loading data
    with st.spinner("Loading team data..."):
        team_api_response = swc.call_api_endpoint(base_url, swc.LIST_TEAMS_ENDPOINT)

    if team_api_response.status_code == 200:
        team_data: List[Dict[str, Any]] = team_api_response.json()
        
        # Process the team data
        teams_df = pd.DataFrame.from_dict(team_data)
        
        # Extract unique leagues and sort them
        unique_leagues = sorted(teams_df['league_id'].astype(str).unique())
        
        # Store leagues in session state for other pages to use
        st.session_state['unique_leagues'] = unique_leagues
        
        # --- Sidebar Controls ---
        selected_league = st.sidebar.selectbox(
            'Select League', 
            unique_leagues,
            format_func=lambda x: f"League {x}"
        )
        
        # Add team filter if there are multiple teams
        teams_in_league = teams_df[teams_df['league_id'].astype(str) == selected_league]['team_name'].unique()
        if len(teams_in_league) > 1:
            selected_team = st.sidebar.multiselect(
                'Filter by Team', 
                options=teams_in_league,
                default=[]
            )
        else:
            selected_team = []
        
        # Add position filter
        positions = ["QB", "RB", "WR", "TE", "K", "DEF"]
        selected_positions = st.sidebar.multiselect(
            'Filter by Position',
            options=positions,
            default=[]
        )
  
        st.sidebar.divider()
        st.sidebar.subheader("📊 Data Sources")
        st.sidebar.text("SportsWorldCentral API")
        
        # --- Create flattened player dataframe ---
        flat_team_df = pd.json_normalize(
            team_data, 'players', ['team_id', 'team_name', 'league_id']
        )
        
        # Order columns logically
        column_order = [
            'league_id', 'team_id', 'team_name', 'position',
            'player_id', 'gsis_id', 'first_name', 'last_name'
        ]
        flat_team_df_ordered = flat_team_df[column_order]
        
        # Store complete dataset in session state for other pages to use
        st.session_state['flat_team_df_ordered'] = flat_team_df_ordered

        # --- Display Data ---
        # Create display dataframe (remove internal IDs)
        display_df = flat_team_df_ordered.copy()
        display_df['league_id'] = display_df['league_id'].astype(str)
        
        # Apply filters
        display_df = display_df[display_df['league_id'] == selected_league]
        
        if selected_team:
            display_df = display_df[display_df['team_name'].isin(selected_team)]
            
        if selected_positions:
            display_df = display_df[display_df['position'].isin(selected_positions)]
            
        # Add player full name column
        display_df['player'] = display_df['first_name'] + ' ' + display_df['last_name']
        
        # Reorder and select columns for display
        final_display_cols = ['team_name', 'position', 'player']
        
        # Show player count
        st.subheader(f"Showing {len(display_df)} Players")
        
        # Display the dataframe with formatting
        st.dataframe(
            display_df[final_display_cols],
            hide_index=True, 
            use_container_width=True,
            column_config={
                "team_name": st.column_config.TextColumn("Team"),
                "position": st.column_config.TextColumn("Pos"),
                "player": st.column_config.TextColumn("Player Name"),
            }
        )
        
        # Display stats about the league
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Teams", len(teams_in_league))
        with col2:
            st.metric("Total Players", len(display_df))
        with col3:
            pos_counts = display_df['position'].value_counts()
            most_common_pos = pos_counts.idxmax() if not pos_counts.empty else "N/A"
            #st.metric("Most Common Position", most_common_pos, pos_counts.max() if not pos_counts.empty else 0)
            # using st.metric() to display the most common position, but passing a NumPy integer (numpy.int64) value for the delta parameter. 
            # Streamlit doesn't accept NumPy number types directly - they need to be converted to Python native types.
            # The int() conversion will convert the NumPy int64 to a Python integer, which Streamlit accepts.
            # # If you're using pandas/numpy in other metrics, you might want to check for similar issues by adding conversion to native Python types:
            # For integers: int(numpy_value)
            # For floats: float(numpy_value)
            # For strings: str(numpy_value)

            st.metric("Most Common Position", most_common_pos, int(pos_counts.max()) if not pos_counts.empty else 0) 
    
    else:
        st.error(f"❌ Error accessing data: HTTP {team_api_response.status_code}")
        logger.error(f"API error: {team_api_response.status_code} {team_api_response.text}")

except Exception as e:
    logger.error(f"Exception: {str(e)}", exc_info=True)
    st.error("❌ An unexpected error occurred while loading team data.")
    st.info("💡 Tip: Make sure the API server is running at the correct URL.")