"""
Cumulative Points Race page showing animated race charts of fantasy points over time.
Visualizes how teams accumulate points throughout the season in an engaging race format.
"""
import streamlit as st
import pandas as pd
import logging
import simple_api_client as swc
import numpy as np

logger = logging.getLogger(__name__)

# Check for raceplotly package
try:
    from raceplotly.plots import barplot
    RACEPLOTLY_AVAILABLE = True
except ImportError:
    RACEPLOTLY_AVAILABLE = False
    st.error("❌ The 'raceplotly' package is required for this page. Please install it with: pip install raceplotly")
    st.stop()

# --- Page UI ---
st.header("🏎️ Cumulative Points Race")
st.markdown(
    "Watch the teams race to accumulate fantasy points over the weeks! "
    "This animated chart shows which teams started strong and which made late comebacks."
)

# --- Configuration ---
API_ENDPOINT = swc.LIST_TEAMS_ENDPOINT

# --- Helper Functions ---
def get_team_weekly_scores_for_race(base_url: str) -> pd.DataFrame:
    """
    Fetches team data and prepares it for the race chart.
    
    Args:
        base_url: Base URL of the API
        
    Returns:
        DataFrame ready for race chart visualization
    """
    all_scores = []
    try:
        with st.spinner("Loading team scores..."):
            response = swc.call_api_endpoint(base_url, API_ENDPOINT)
            
        if response.status_code == 200:
            teams_data = response.json()
            
            # Process each team's weekly scores
            for team in teams_data:
                team_id = team.get('team_id')
                team_name = team.get('team_name')
                league_id = team.get('league_id')
                weekly_scores = team.get('weekly_scores', [])
                
                if not weekly_scores:
                    continue
                    
                for score in weekly_scores:
                    # Parse week number for sorting
                    week_str = str(score.get('week_number', '0'))
                    try:
                        if '_' in week_str:
                            year, week = map(int, week_str.split('_'))
                        else:
                            # Default year if not specified
                            year = 2023
                            week = int(week_str)
                        # Create a sortable time value (e.g., YYYYWW)
                        time_val = year * 100 + week
                    except ValueError:
                        logger.warning(f"Could not parse week_number '{week_str}' for team {team_id}. Skipping score.")
                        continue

                    all_scores.append({
                        'league_id': league_id,
                        'team_id': team_id,
                        'team_name': team_name,
                        'time_val': time_val,
                        'week_number': week_str,
                        'year': year,
                        'week': week,
                        'fantasy_points': score.get('fantasy_points', 0)
                    })
                    
            if not all_scores:
                return pd.DataFrame()

            # Create DataFrame and clean data
            df = pd.DataFrame(all_scores)
            df['fantasy_points'] = pd.to_numeric(df['fantasy_points'], errors='coerce').fillna(0)
            df['league_id'] = df['league_id'].astype(str)
            df = df.sort_values(by=['league_id', 'team_id', 'time_val'])

            # Calculate cumulative points
            df['cumulative_points'] = df.groupby(['league_id', 'team_id'])['fantasy_points'].cumsum()
            return df
            
        else:
            st.error(f"❌ Error fetching team data: {response.status_code}")
            logger.error(f"API Error: {response.status_code} - {response.text}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ An error occurred while fetching data: {e}")
        logger.error(f"Data fetching exception: {e}", exc_info=True)
        return pd.DataFrame()

def create_sample_race_data() -> pd.DataFrame:
    """Creates sample race data when API data isn't available."""
    teams = ["Team A", "Team B", "Team C", "Team D", "Team E", "Team F"]
    weeks = range(1, 15)  # 14 weeks
    
    data = []
    np.random.seed(42)  # For reproducibility
    
    for team in teams:
        # Give each team a different scoring pattern
        if team == "Team A":
            base_points = 100  # Consistently good
            variation = 15
        elif team == "Team B":
            base_points = 80   # Weaker but steady
            variation = 10
        elif team == "Team C":
            base_points = 90   # Average with high variation
            variation = 25
        elif team == "Team D":
            base_points = 110  # Strong start, declining
            variation = 15
        elif team == "Team E":
            base_points = 70   # Weak start, improving
            variation = 20
        else:
            base_points = 95   # Average
            variation = 18
            
        # Create weekly fantasy points with some randomness and trends
        weekly_points = []
        for week in weeks:
            # Add some trends - Team D declines, Team E improves
            if team == "Team D":
                trend_factor = 1 - (week / 30)  # Gradual decline
            elif team == "Team E":
                trend_factor = 1 + (week / 20)  # Gradual improvement
            else:
                trend_factor = 1
                
            points = base_points * trend_factor + np.random.normal(0, variation)
            points = max(50, min(150, points))  # Keep within reasonable range
            weekly_points.append(points)
            
            data.append({
                'league_id': '999',  # Sample league ID
                'team_id': teams.index(team),
                'team_name': team,
                'time_val': 202300 + week,
                'week_number': str(week),
                'year': 2023,
                'week': week,
                'fantasy_points': points
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    df = df.sort_values(by=['team_id', 'time_val'])
    
    # Calculate cumulative points
    df['cumulative_points'] = df.groupby('team_id')['fantasy_points'].cumsum()
    
    return df

# --- Main Logic ---
base_url = st.session_state.get('base_url', 'http://127.0.0.1:8000/')

# Try to get real data first
race_df = get_team_weekly_scores_for_race(base_url)

# If no data, use sample data
if race_df.empty:
    st.info("📝 Using sample data for demonstration. Connect to API for real data.")
    race_df = create_sample_race_data()

if not race_df.empty:
    # --- Sidebar Controls ---
    st.sidebar.title("Visualization Options")
    
    # League selection (use unique_leagues from session state or from data)
    unique_leagues = st.session_state.get('unique_leagues', sorted(race_df['league_id'].unique()))
    selected_league = st.sidebar.selectbox(
        'Select League', 
        unique_leagues,
        format_func=lambda x: f"League {x}"
    )
    
    # Animation speed control
    animation_speed = st.sidebar.slider(
        "Animation Speed", 
        min_value=200, 
        max_value=1500, 
        value=800, 
        step=100,
        help="Control how fast the animation plays (milliseconds per frame)"
    )
    
    # Customize bar colors
    bar_color = st.sidebar.color_picker("Bar Color", "#FF4B4B")
    
    st.sidebar.divider()
    st.sidebar.subheader("📊 Data Sources")
    st.sidebar.text("SportsWorldCentral API")

    # Filter data for the selected league
    league_race_df = race_df[race_df['league_id'] == selected_league].copy()

    if not league_race_df.empty:
        # --- Chart Preparation ---
        item_column = 'team_name'
        value_column = 'cumulative_points'
        time_column = 'time_val'

        # Ensure data completeness for the race chart
        all_times = sorted(league_race_df[time_column].unique())
        all_teams = league_race_df[item_column].unique()
        
        # Create a complete multi-index for all team-time combinations
        multi_index = pd.MultiIndex.from_product(
            [all_teams, all_times], 
            names=[item_column, time_column]
        )

        # Fill in missing values to ensure continuous animation
        league_race_df_filled = league_race_df.set_index([item_column, time_column])
        league_race_df_filled = league_race_df_filled.reindex(multi_index)
        
        # Forward fill within each team group to maintain cumulative points
        league_race_df_filled[value_column] = league_race_df_filled.groupby(level=0)[value_column].ffill().fillna(0)
        league_race_df_filled.reset_index(inplace=True)
        
        # Create nice labels for time values 
        # Convert from numeric time_val (e.g., 202301) to "Week 1" format
        time_labels = {
            time_val: f"Week {time_val % 100}" 
            for time_val in all_times
        }

        # --- Generate Race Chart ---
        try:
            num_teams = league_race_df_filled[item_column].nunique()
            raceplot = barplot(
                league_race_df_filled,
                item_column=item_column,
                value_column=value_column,
                time_column=time_column,
                top_entries=num_teams
            )

            # Customize the plot
            fig = raceplot.plot(
                item_label='Team',
                value_label='Cumulative Points',
                frame_duration=animation_speed,
                date_format=None,
                orientation='horizontal'
            )
            
            # Update the figure layout
            fig.update_layout(
                title=f'Cumulative Fantasy Points Race - League {selected_league}',
                autosize=True,
                width=800,
                height=600,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#FFFFFF"),
                margin=dict(l=0, r=0, t=50, b=0),
                xaxis=dict(title="Total Fantasy Points")
            )
            
            # Update trace colors
            for trace in fig.data:
                trace.update(marker_color=bar_color)
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

            # --- Additional Insights ---
            # Add a table showing final standings
            final_frame = league_race_df.sort_values('time_val').groupby('team_name').last().reset_index()
            final_standings = final_frame.sort_values('cumulative_points', ascending=False)[['team_name', 'cumulative_points']]
            final_standings.columns = ['Team', 'Total Fantasy Points']
            final_standings['Final Rank'] = range(1, len(final_standings) + 1)
            
            st.subheader("Final Standings")
            st.dataframe(
                final_standings[['Final Rank', 'Team', 'Total Fantasy Points']],
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Final Rank": st.column_config.NumberColumn("Rank", format="%d"),
                    "Team": st.column_config.TextColumn("Team Name"),
                    "Total Fantasy Points": st.column_config.NumberColumn("Total Points", format="%.1f")
                }
            )

        except Exception as plot_err:
            st.error(f"❌ Could not generate the race chart: {plot_err}")
            logger.error(f"Race chart generation error: {plot_err}", exc_info=True)
            
            # Show the raw data as fallback
            st.warning("⚠️ Showing data table instead of animation due to an error.")
            st.dataframe(league_race_df_filled)

    else:
        st.warning(f"⚠️ No data available for League ID: {selected_league} to generate race chart.")

else:
    st.error("❌ Could not retrieve any team scoring data for the race chart.")