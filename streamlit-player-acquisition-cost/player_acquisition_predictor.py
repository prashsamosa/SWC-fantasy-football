"""
Standalone Player Acquisition Predictor application for fantasy football.
This app uses machine learning to predict optimal bids for waiver wire player acquisitions.
"""
import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional
import logging
import os
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='acquisition_predictor.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default API URL
DEFAULT_API_URL = os.getenv('ML_API_URL', "https://swc-fantasy-football.onrender.com")
API_ENDPOINT = "/predict/"

# --- UI Configuration ---
st.set_page_config(
    page_title="Fantasy Football Bid Predictor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Helper Functions ---
def predict_acquisition_cost(
    api_url: str, 
    waiver_tier: int, 
    weeks_remaining: int, 
    budget_remaining: int
) -> Optional[Dict[str, float]]:
    """Call the ML API to predict player acquisition costs"""
    try:
        request_data = {
            "waiver_value_tier": waiver_tier,
            "fantasy_regular_season_weeks_remaining": weeks_remaining,
            "league_budget_pct_remaining": budget_remaining
        }
        
        response = requests.post(
            f"{api_url}{API_ENDPOINT}",
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            logger.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error connecting to prediction API: {e}")
        logger.error(f"Prediction API error: {e}", exc_info=True)
        return None

def create_bullet_chart(pred_values: Dict[str, float], max_val: float = 100) -> go.Figure:
    """Create a bullet chart visualization for bid amounts"""
    fig = go.Figure()
    
    # Add bars for different percentiles
    fig.add_trace(go.Bar(
        y=["Recommended Bid Range"],
        x=[pred_values["winning_bid_90th_percentile"]],
        orientation='h',
        marker=dict(color='rgba(55, 128, 191, 0.7)'),
        name='90th Percentile (Aggressive)'
    ))
    
    fig.add_trace(go.Bar(
        y=["Recommended Bid Range"],
        x=[pred_values["winning_bid_50th_percentile"]],
        orientation='h',
        marker=dict(color='rgba(26, 118, 255, 0.8)'),
        name='50th Percentile (Balanced)'
    ))
    
    fig.add_trace(go.Bar(
        y=["Recommended Bid Range"],
        x=[pred_values["winning_bid_10th_percentile"]],
        orientation='h',
        marker=dict(color='rgba(0, 91, 150, 0.9)'),
        name='10th Percentile (Conservative)'
    ))

    # Update layout
    fig.update_layout(
        title="Recommended Bid Range",
        barmode='overlay',
        height=200,
        margin=dict(l=30, r=30, t=50, b=30),
        xaxis=dict(
            range=[0, max_val],
            title="FAAB Dollars ($)",
            showgrid=True
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(240,240,240,0.5)"
    )
    
    return fig

def create_bid_distribution(pred_values: Dict[str, float], total_budget: int = 100) -> go.Figure:
    """Create a normal distribution curve to visualize the bid probability distribution"""
    low = pred_values["winning_bid_10th_percentile"]
    mid = pred_values["winning_bid_50th_percentile"]
    high = pred_values["winning_bid_90th_percentile"]
    
    # Estimate mean and standard deviation
    mean = mid
    # For a normal distribution, there's approximately 2.56 standard deviations between 10th and 90th percentile
    std = (high - low) / 2.56
    
    # Generate points for the curve
    x = np.linspace(max(0, mean - 3*std), min(mean + 3*std, total_budget), 100)
    y = np.exp(-0.5 * ((x - mean) / std)**2) / (std * np.sqrt(2*np.pi))
    
    # Scale y to make the curve more visible
    y = y / y.max()
    
    # Create the distribution curve
    fig = px.line(x=x, y=y, labels={"x": "Bid Amount ($)", "y": "Probability"})
    
    # Add vertical lines for the percentiles
    fig.add_vline(x=low, line_width=2, line_dash="dash", line_color="green",
                 annotation_text="10th percentile", annotation_position="top right")
    fig.add_vline(x=mid, line_width=2, line_color="blue",
                 annotation_text="50th percentile", annotation_position="top right")
    fig.add_vline(x=high, line_width=2, line_dash="dash", line_color="red",
                 annotation_text="90th percentile", annotation_position="top right")
    
    # Update layout
    fig.update_layout(
        title="Bid Amount Probability Distribution",
        height=300,
        margin=dict(l=30, r=30, t=50, b=30),
        yaxis_title="Relative Probability",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(240,240,240,0.5)"
    )
    
    return fig

# --- Header ---
st.title("💰 Fantasy Football Bid Predictor")
st.markdown("""
This tool uses machine learning to predict optimal bid amounts for player acquisitions in fantasy football.
Enter your league and player information to get data-driven FAAB bid recommendations.
""")

# --- Sidebar Configuration ---
st.sidebar.header("Settings")
api_url = st.sidebar.text_input(
    "API URL",
    value=DEFAULT_API_URL,
    help="URL of the prediction API"
)

st.sidebar.markdown("---")

# Budget settings
total_budget = st.sidebar.number_input(
    "Total FAAB Budget ($)",
    min_value=1,
    max_value=1000,
    value=100,
    help="Total FAAB budget for your league"
)

st.sidebar.markdown("## About")
st.sidebar.info(
    """
    This application predicts optimal bid amounts for fantasy football waiver wire acquisitions.
    
    The model is trained on historical FAAB bidding data and considers:
    - Player value tier
    - Point in the season
    - Your remaining budget
    
    Use the predictions as a guide, but always consider your team needs and league dynamics.
    """
)

# --- Main Content ---
# Input form
st.subheader("Player & League Information")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Player Details")
    
    player_name = st.text_input(
        "Player Name (optional)",
        value="",
        help="For your reference only - not used in prediction"
    )
    
    waiver_tier = st.select_slider(
        "Player Value Tier",
        options=[1, 2, 3, 4, 5],
        value=3,
        help="1 = Elite (RB1/WR1), 5 = Low value (Bench stash)"
    )
    
    st.markdown("**Tier Guidelines:**")
    tier_descriptions = {
        1: "Elite (RB1/WR1/TE1/QB1) - League winners",
        2: "Strong Starters (RB2/WR2/TE2) - Weekly starters",
        3: "Rotation Players (RB3/WR3/FLEX) - Matchup dependent",
        4: "Depth (RB4/WR4) - Bye week fill-ins, upside bench",
        5: "Speculative (RB5+/WR5+) - Lottery tickets, handcuffs"
    }
    
    for tier, desc in tier_descriptions.items():
        st.markdown(f"- **Tier {tier}:** {desc}")

with col2:
    st.markdown("### League Context")
    
    weeks_remaining = st.slider(
        "Weeks Remaining in Regular Season",
        min_value=1,
        max_value=17,
        value=10,
        help="Number of weeks remaining in your fantasy football regular season"
    )
    
    budget_remaining = st.slider(
        "Budget Remaining (%)",
        min_value=1,
        max_value=100,
        value=75,
        help="Percentage of your total FAAB budget that remains available"
    )
    
    budget_dollars = int(total_budget * budget_remaining / 100)
    st.info(f"You have ${budget_dollars} remaining out of your ${total_budget} budget")
    
    # Team needs (doesn't affect prediction but useful for context)
    team_needs = st.multiselect(
        "Team Needs (optional)",
        options=["QB", "RB", "WR", "TE", "K", "DST"],
        default=[],
        help="Select positions where your team needs improvement"
    )

# Prediction button
predict_button = st.button("Get Bid Recommendations", type="primary", use_container_width=True)

if predict_button:
    # Display a spinner while making the API call
    with st.spinner("Analyzing player value and generating bid recommendations..."):
        predictions = predict_acquisition_cost(
            api_url, 
            waiver_tier, 
            weeks_remaining, 
            budget_remaining
        )
    
    if predictions:
        # Calculate max value for visualization (add 20% buffer above highest prediction)
        max_display_value = int(max(predictions.values()) * 1.2)
        if max_display_value < 10:
            max_display_value = 10
            
        # Format player name for display
        display_name = player_name if player_name else f"Tier {waiver_tier} Player"
            
        # Results section
        st.markdown(f"## Bid Recommendations for {display_name}")
        
        # Create metrics for bid amounts
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Conservative Bid (10%)",
                f"${predictions['winning_bid_10th_percentile']:.1f}",
                delta=None
            )
            
        with col2:
            st.metric(
                "Recommended Bid (50%)",
                f"${predictions['winning_bid_50th_percentile']:.1f}",
                delta=None
            )
            
        with col3:
            st.metric(
                "Aggressive Bid (90%)",
                f"${predictions['winning_bid_90th_percentile']:.1f}",
                delta=None
            )
        
        # Show bullet chart
        st.plotly_chart(
            create_bullet_chart(predictions, max_display_value),
            use_container_width=True
        )
        
        # Show probability distribution
        st.plotly_chart(
            create_bid_distribution(predictions, total_budget),
            use_container_width=True
        )
        
        # Recommendations and insights
        st.subheader("Analysis & Recommendations")
        
        # Calculate some values for insights
        bid_range = predictions["winning_bid_90th_percentile"] - predictions["winning_bid_10th_percentile"]
        mid_bid = predictions["winning_bid_50th_percentile"]
        high_bid = predictions["winning_bid_90th_percentile"]
        remaining_dollars = budget_dollars
        
        # Create columns for different types of insights
        insight_cols = st.columns(2)
        
        with insight_cols[0]:
            st.markdown("### Bid Strategy")
            
            # Different advice based on tier and season point
            if waiver_tier <= 2 and weeks_remaining >= 10:
                st.info("🔍 **Early Season Elite Player**: Worth aggressive bidding as they can impact your entire season.")
            elif waiver_tier <= 2 and weeks_remaining < 5:
                st.info("🚀 **Late Season Elite Player**: Consider going all-in if they address a critical need.")
            elif waiver_tier >= 4 and weeks_remaining < 5:
                st.info("⚠️ **Late Season Speculation**: Conservative bidding recommended unless desperate at position.")
            else:
                st.info("⚖️ **Balanced Approach**: Use the 50th percentile bid as your primary target.")
                
            # Budget percentage context
            pct_of_remaining = mid_bid / remaining_dollars * 100
            if pct_of_remaining > 40:
                st.warning(f"⚠️ The recommended bid is {pct_of_remaining:.1f}% of your remaining budget!")
            elif pct_of_remaining > 20:
                st.info(f"📊 The recommended bid is {pct_of_remaining:.1f}% of your remaining budget.")
                
        with insight_cols[1]:
            st.markdown("### Bid Confidence")
            
            # Confidence level based on range
            if bid_range < mid_bid * 0.3:
                st.success("🎯 **High Confidence**: Narrow prediction range suggests a consistent market value.")
            elif bid_range > mid_bid * 0.8:
                st.warning("📈 **Low Confidence**: Wide prediction range indicates uncertainty in player value.")
            else:
                st.info("📊 **Moderate Confidence**: Some variability expected in bidding.")
                
            # Advice about overbidding
            if waiver_tier >= 3:
                extra_dollar = int(mid_bid) + 1
                st.info(f"💡 For this tier of player, consider bidding ${extra_dollar} (odd number) to break ties.")
        
        # Advanced bidding strategy
        with st.expander("Advanced Bidding Strategy"):
            st.markdown("""
            ### Situational Bidding Adjustments
            
            1. **League Dynamics**
                - Aggressive leagues: Add 10-20% to the recommended bid
                - Conservative leagues: Stay closer to the 10th percentile bid
                
            2. **Position Scarcity**
                - Top-tier TEs and QBs often require premium bids due to positional scarcity
                - RBs typically command higher bids than WRs due to fewer viable options
                
            3. **Team Composition**
                - If filling a starting spot: More aggressive bidding justified
                - If adding depth: More conservative approach recommended
                
            4. **Season Point**
                - Early season: Balance being aggressive with preserving budget
                - Mid-season: More informed bidding as team needs are clearer
                - Late season: Consider more aggressive bids if contending
                
            5. **Bid Psychology**
                - Use non-round numbers (e.g., $13 instead of $10)
                - Bid slightly above expected value tiers ($11 instead of $10)
            """)
        
        # Comparison to total budget
        st.subheader("Budget Context")
        budget_data = pd.DataFrame({
            "Category": ["Conservative", "Recommended", "Aggressive"],
            "Bid Amount": [
                predictions["winning_bid_10th_percentile"],
                predictions["winning_bid_50th_percentile"],
                predictions["winning_bid_90th_percentile"]
            ],
            "Percentage of Remaining Budget": [
                predictions["winning_bid_10th_percentile"] / budget_dollars * 100,
                predictions["winning_bid_50th_percentile"] / budget_dollars * 100,
                predictions["winning_bid_90th_percentile"] / budget_dollars * 100
            ]
        })
        
        # Format budget data
        budget_data["Bid Amount"] = budget_data["Bid Amount"].apply(lambda x: f"${x:.2f}")
        budget_data["Percentage of Remaining Budget"] = budget_data["Percentage of Remaining Budget"].apply(lambda x: f"{x:.1f}%")
        
        st.table(budget_data)

else:
    # Display sample prediction or information when the app first loads
    st.info("👆 Enter player and league information, then click 'Get Bid Recommendations'")
    
    # Show an example of what the output will look like
    with st.expander("See example output"):
        st.image("https://i.ibb.co/H4qC0Q1/bid-predictor-example.png", 
                caption="Example prediction output")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center">
        <p>Powered by machine learning trained on historical fantasy football bidding data</p>
        <p>© 2025 SWC Fantasy Football Analytics</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Allow users to provide feedback
with st.expander("Provide feedback on this tool"):
    feedback_rating = st.slider("Rate this tool", 1, 5, 3)
    feedback_text = st.text_area("Your feedback (optional)")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")
        logger.info(f"User feedback: Rating {feedback_rating}, Text: {feedback_text}")