"""
Team Touchdown Stats page displaying touchdown statistics for each team.
Shows a horizontal bar chart of team touchdown totals.
"""
import streamlit as st
import pandas as pd
import logging
import matplotlib.pyplot as plt
import numpy as np

logger = logging.getLogger(__name__) 

# --- Page UI ---
st.header("🏈 Team Touchdown Statistics")
st.markdown("Compare the touchdown performance of teams in your selected league.")

try:
    # --- Check Session State ---
    if 'flat_team_df_ordered' not in st.session_state:
        st.error("❌ Team data not loaded. Please visit the Team Rosters page first.")
        st.stop()
        
    # --- Get Data ---
    flat_team_df = st.session_state['flat_team_df_ordered'].copy()
    
    # Get unique leagues from session state
    unique_leagues = st.session_state.get('unique_leagues', [])
    if len(unique_leagues) == 0:
        st.error("❌ No leagues found. Please visit the Team Rosters page first.")
        st.stop()
    
    # --- Sidebar Controls ---
    selected_league = st.sidebar.selectbox(
        'Select League', 
        unique_leagues,
        format_func=lambda x: f"League {x}"
    )
    
    # Add visualization options
    chart_color = st.sidebar.color_picker(
        "Chart Color", 
        value="#e50000",  # Default to crimson red
        help="Select the bar color for the chart"
    )
    
    show_labels = st.sidebar.checkbox("Show Value Labels", value=True)
    sort_by = st.sidebar.radio("Sort Order", ["Highest First", "Lowest First", "Alphabetical"])
    
    st.sidebar.divider()
    st.sidebar.subheader("📊 Data Sources")
    st.sidebar.text("SportsWorldCentral API")
    
    # --- Process Data ---
    if 'league_id' not in flat_team_df.columns:
        st.warning("⚠️ League data missing, showing sample visualization")
        teams = ["Team A", "Team B", "Team C", "Team D", "Team E"]
        tds = [7, 12, 5, 9, 3]
        grouped_df = pd.Series(tds, index=teams, name='total_tds')
    else:
        # Filter by selected league 
        flat_team_df['league_id'] = flat_team_df['league_id'].astype(str)
        league_teams = flat_team_df[flat_team_df['league_id'] == selected_league]
        
        # Get unique team names
        teams = league_teams['team_name'].unique()
        
        if len(teams) == 0:
            st.warning(f"⚠️ No teams found for league {selected_league}")
            st.stop()
            
        # Generate random TD data for visualization
        np.random.seed(42)  # For reproducibility 
        tds = np.random.randint(1, 15, size=len(teams))
        
        # Create Series for plotting
        grouped_df = pd.Series(tds, index=teams, name='total_tds')
        
        # Apply sorting
        if sort_by == "Highest First":
            grouped_df = grouped_df.sort_values(ascending=False)
        elif sort_by == "Lowest First":
            grouped_df = grouped_df.sort_values(ascending=True)
        else:  # Alphabetical
            grouped_df = grouped_df.sort_index()
    
    # --- Create Visualization ---
    fig, ax = plt.subplots(figsize=(10, max(6, len(grouped_df) * 0.4)))  # Dynamic height based on team count
    
    # Plot horizontal bars
    bars = grouped_df.plot(
        kind="barh", 
        color=chart_color,
        ax=ax,
        zorder=2  # Ensure bars are above grid
    )
    
    # Add data labels if enabled
    if show_labels:
        for i, v in enumerate(grouped_df):
            ax.text(v + 0.3, i, f"{v}", va='center', fontweight='bold', color='white')
    
    # Style the chart
    title = f"Total Touchdowns by Team - League {selected_league}"
    ax.set_title(title, fontsize=15, pad=20)
    ax.set_xlabel("Touchdowns", fontsize=12)
    ax.set_ylabel("")
    
    # Add grid for better readability
    ax.grid(axis='x', linestyle='--', alpha=0.7, zorder=1)
    
    # Set background to transparent
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Set text color to white for better visibility in dark theme
    ax.title.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    
    # Show plot with descriptive caption
    st.pyplot(fig)
    
    # Add an interesting fact in a callout
    with st.expander("📝 About This Data", expanded=False):
        st.info(
            "**Note:** This visualization currently uses randomly generated data for demonstration purposes.\n\n"
            "💡 **Fun Fact:** The average NFL team scores approximately 2.6 touchdowns per game."
        )

    # Show data in table format
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Team Touchdown Data")
        df_display = pd.DataFrame({
            'Team': grouped_df.index,
            'Touchdowns': grouped_df.values,
        })
        st.dataframe(
            df_display, 
            hide_index=True,
            use_container_width=True,
            column_config={
                "Team": st.column_config.TextColumn("Team Name"),
                "Touchdowns": st.column_config.NumberColumn("TD Total", format="%d")
            }
        )
    
    with col2:
        # Show summary statistics
        avg_tds = grouped_df.mean()
        max_tds = grouped_df.max()
        min_tds = grouped_df.min()
        
        st.subheader("Summary Statistics")
        st.metric("Average TDs per Team", f"{avg_tds:.1f}")
        st.metric("Highest TD Total", max_tds)
        st.metric("Lowest TD Total", min_tds)
    
except Exception as e:
    logger.error(f"Error in page2: {e}", exc_info=True)
    st.error(f"❌ An unexpected error occurred: {str(e)}")
    
    # Fallback visualization in case of error
    st.info("Showing fallback visualization")
    
    # Create sample data
    teams = ["Team A", "Team B", "Team C"]
    tds = [5, 3, 8]
    
    # Create and display a simple chart
    fig, ax = plt.subplots()
    ax.bar(teams, tds, color='crimson')
    ax.set_ylabel('Touchdowns')
    ax.set_title('Sample Team Touchdown Data')
    st.pyplot(fig)