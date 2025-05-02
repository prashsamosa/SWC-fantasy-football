"""
Team Scoring Distribution page showing box plots of weekly fantasy scores.
Visualizes the range, median, and distribution of scores for all teams.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import logging
import simple_api_client as swc

logger = logging.getLogger(__name__)

# --- Page UI ---
st.header("📊 Team Scoring Distribution")
st.markdown(
    "Analyze the distribution of weekly fantasy points for each team. "
    "This visualization helps you understand consistency and scoring potential."
)

# --- Configuration ---
API_ENDPOINT = swc.LIST_TEAMS_ENDPOINT
PLOTLY_DEFAULT_LAYOUT_KWARGS = dict(
    height=600,
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    font=dict(color="#FFFFFF"),
    margin=dict(l=0, r=0, t=50, b=0),
)

# --- Helper Functions ---
def get_team_weekly_scores(base_url: str) -> pd.DataFrame:
    """
    Fetches team data including weekly scores and returns a DataFrame.
    
    Args:
        base_url: Base URL of the API
        
    Returns:
        DataFrame of weekly scores by team
    """
    all_scores = []
    try:
        with st.spinner("Loading score data..."):
            response = swc.call_api_endpoint(base_url, API_ENDPOINT)
        
        if response.status_code == 200:
            teams_data = response.json()
            for team in teams_data:
                team_id = team.get('team_id')
                team_name = team.get('team_name')
                league_id = team.get('league_id')
                weekly_scores = team.get('weekly_scores', [])
                
                if not weekly_scores:
                    continue
                    
                for score in weekly_scores:
                    all_scores.append({
                        'league_id': league_id,
                        'team_id': team_id,
                        'team_name': team_name,
                        'week_number': score.get('week_number'),
                        'fantasy_points': score.get('fantasy_points')
                    })
            return pd.DataFrame(all_scores)
        else:
            st.error(f"❌ Error fetching team data: {response.status_code}")
            logger.error(f"API Error: {response.status_code} - {response.text}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ An error occurred while fetching data: {str(e)}")
        logger.error(f"Data fetching exception: {e}", exc_info=True)
        return pd.DataFrame()

# --- Main Logic ---
base_url = st.session_state.get('base_url', 'http://127.0.0.1:8000/')
scores_df = get_team_weekly_scores(base_url)

if not scores_df.empty:
    # Ensure correct data types
    scores_df['fantasy_points'] = pd.to_numeric(scores_df['fantasy_points'], errors='coerce')
    scores_df.dropna(subset=['fantasy_points'], inplace=True)
    scores_df['league_id'] = scores_df['league_id'].astype(str)

    # --- Sidebar Controls ---
    st.sidebar.title("Visualization Options")
    
    # League selection
    unique_leagues = st.session_state.get('unique_leagues', sorted(scores_df['league_id'].unique()))
    selected_league = st.sidebar.selectbox(
        'Select League', 
        ['All'] + unique_leagues,
        format_func=lambda x: "All Leagues" if x == "All" else f"League {x}"
    )
    
    # Color scheme selection
    color_scheme = st.sidebar.selectbox(
        'Color Scheme',
        ['Blues to Reds', 'Greens', 'Purples', 'Rainbow'],
        help="Select the color palette for the box plots"
    )
    
    # Box plot options
    show_outliers = st.sidebar.checkbox("Show Outliers", value=False)
    
    st.sidebar.divider()
    st.sidebar.subheader("📊 Data Sources")
    st.sidebar.text("SportsWorldCentral API")

    # Filter by league if selected
    if selected_league != 'All':
        scores_df = scores_df[scores_df['league_id'] == selected_league]

    if not scores_df.empty:
        # --- Chart Generation ---
        # Calculate medians for coloring
        team_medians = (
            scores_df.groupby("team_name")["fantasy_points"].median().sort_values()
        )
        teams = team_medians.index

        # Choose color palette based on selection
        if color_scheme == 'Blues to Reds':
            plotly_colors = [
                'rgb(13, 71, 161)', 'rgb(25, 118, 210)', 'rgb(66, 165, 245)', 'rgb(129, 212, 250)',
                'rgb(178, 235, 242)', 'rgb(255, 236, 179)', 'rgb(255, 224, 178)', 
                'rgb(255, 183, 77)', 'rgb(255, 152, 0)', 'rgb(244, 67, 54)'
            ]
        elif color_scheme == 'Greens':
            plotly_colors = [
                'rgb(0, 77, 64)', 'rgb(0, 105, 92)', 'rgb(0, 137, 123)', 
                'rgb(0, 150, 136)', 'rgb(38, 166, 154)', 'rgb(77, 182, 172)',
                'rgb(128, 203, 196)', 'rgb(178, 223, 138)', 'rgb(200, 230, 201)'
            ]
        elif color_scheme == 'Purples':
            plotly_colors = [
                'rgb(74, 20, 140)', 'rgb(106, 27, 154)', 'rgb(123, 31, 162)', 
                'rgb(156, 39, 176)', 'rgb(186, 104, 200)', 'rgb(206, 147, 216)',
                'rgb(225, 190, 231)', 'rgb(243, 229, 245)'
            ]
        else:  # Rainbow
            plotly_colors = [
                'rgb(128, 0, 128)', 'rgb(75, 0, 130)', 'rgb(0, 0, 255)', 
                'rgb(0, 255, 0)', 'rgb(255, 255, 0)', 'rgb(255, 127, 0)', 'rgb(255, 0, 0)'
            ]
        
        # Map each team to a color based on its median value
        min_median = team_medians.min()
        max_median = team_medians.max() if team_medians.max() > min_median else min_median + 1  # Avoid division by zero
        
        def get_color_index(median):
            # Get normalized position (0 to 1)
            normalized = (median - min_median) / (max_median - min_median)
            # Map to color index (0 to len(plotly_colors)-1)
            index = int(normalized * (len(plotly_colors) - 1))
            # Ensure index is within bounds
            return max(0, min(len(plotly_colors) - 1, index))
        
        # Create figure and add traces
        fig = go.Figure()
        
        # Add team box plots
        for team, median in zip(teams, team_medians):
            color_index = get_color_index(median)
            team_data = scores_df[scores_df["team_name"] == team]["fantasy_points"]
            
            # Only add if we have data
            if not team_data.empty:
                fig.add_trace(
                    go.Box(
                        x=team_data,
                        name=team,
                        orientation="h",
                        line_color=plotly_colors[color_index],
                        boxpoints='outliers' if show_outliers else False,
                        fillcolor="rgba(0, 0, 0, 0)",  # Transparent fill
                    )
                )

        # Add a legend explaining the color scale
        fig.add_annotation(
            x=0.02,
            y=1.05,
            xref="paper",
            yref="paper",
            text="Colors indicate median score (darker = higher)",
            showarrow=False,
            font=dict(size=12)
        )

        # Update layout
        title_text = "Weekly Fantasy Scoring Distribution"
        if selected_league != 'All':
            title_text += f" (League {selected_league})"
            
        fig.update_layout(
            **PLOTLY_DEFAULT_LAYOUT_KWARGS,
            title_text=title_text,
            xaxis_title_text="Weekly Fantasy Points Scored",
            xaxis_showgrid=True,
            xaxis_tickvals=list(range(0, int(scores_df['fantasy_points'].max()) + 20, 20)),
            xaxis_zeroline=False,
            yaxis_title_text="Team Name",
            yaxis_showgrid=False,
            showlegend=False,
        )
        
        # Show plot with hover info
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # --- Stats & Insights ---
        col1, col2 = st.columns(2)
        
        with col1:
            # Show team with highest median
            highest_median_team = team_medians.idxmax()
            highest_median_value = team_medians.max()
            st.metric("Team with Highest Median Score", highest_median_team, f"{highest_median_value:.1f} pts")
            
            # Show team with lowest median
            lowest_median_team = team_medians.idxmin()
            lowest_median_value = team_medians.min()
            st.metric("Team with Lowest Median Score", lowest_median_team, f"{lowest_median_value:.1f} pts")
        
        with col2:
            # Show team with highest max
            team_maxes = scores_df.groupby("team_name")["fantasy_points"].max()
            highest_max_team = team_maxes.idxmax()
            highest_max_value = team_maxes.max()
            st.metric("Team with Highest Single-Week Score", highest_max_team, f"{highest_max_value:.1f} pts")
            
            # Show most consistent team (lowest standard deviation)
            team_stds = scores_df.groupby("team_name")["fantasy_points"].std()
            most_consistent_team = team_stds.idxmin()
            most_consistent_value = team_stds.min()
            st.metric("Most Consistent Team", most_consistent_team, f"±{most_consistent_value:.1f} pts")

        # --- Explanation ---
        with st.expander("📝 How to Read Box Plots", expanded=False):
            st.markdown(
                """
                **How to Read the Box Plot:**
                
                Each team has a boxplot showing the distribution of their weekly fantasy points:
                
                - **Left Box Edge:** 25th Percentile (Q1) - 25% of scores are lower
                - **Vertical Line Inside Box:** Median (50th Percentile) - Half the scores are lower, half are higher
                - **Right Box Edge:** 75th Percentile (Q3) - 75% of scores are lower
                - **Whiskers (Horizontal Lines):** Extend to the minimum and maximum values within 1.5 times the interquartile range
                - **Dots (Optional):** Outliers falling outside the whiskers
                
                **Interpretation:**
                - **Wider box** = More variability in scoring
                - **Box positioned further right** = Higher typical scores
                - **Longer whiskers** = Occasional very high or low scores
                """
            )
            
            st.image("https://miro.medium.com/max/600/1*2c21SkzJMf3frPXPAR_gZA.png", caption="Box Plot Explained")
    else:
        st.warning(f"⚠️ No scoring data found for League ID: {selected_league}")

else:
    st.warning("⚠️ Could not retrieve any team scoring data from the API.")
    
    # Show sample visualization
    st.info("Showing sample visualization")
    
    # Create sample data
    import numpy as np
    
    teams = ["Team A", "Team B", "Team C", "Team D"]
    sample_data = {
        "Team A": np.random.normal(100, 15, 10),
        "Team B": np.random.normal(90, 20, 10),
        "Team C": np.random.normal(110, 10, 10), 
        "Team D": np.random.normal(95, 25, 10)
    }
    
    # Create figure
    fig = go.Figure()
    for team, points in sample_data.items():
        fig.add_trace(go.Box(x=points, name=team, orientation="h"))
        
    fig.update_layout(
        title="Sample Weekly Fantasy Scoring Distribution",
        xaxis_title="Weekly Fantasy Points",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF")
    )
    
    st.plotly_chart(fig, use_container_width=True)