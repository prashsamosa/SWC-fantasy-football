"""
Main entry point for the SWC Fantasy Football Streamlit application.
This app provides interactive visualizations for fantasy football data.
"""
import streamlit as st
import logging
from dotenv import load_dotenv
import os

# --- Configuration ---
# Load environment variables
load_dotenv()

# Initialize session state with API base URL
if 'base_url' not in st.session_state:
    st.session_state['base_url'] = os.getenv('BASE_URL', 'http://127.0.0.1:8000/')
    # Log the base URL to help with debugging
    print(f"Using API base URL: {st.session_state['base_url']}")

# Configure logging - increase to DEBUG level to get more information
logging.basicConfig(
    filename='football_app.log',
    level=logging.DEBUG,  # Changed from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- UI Configuration ---
st.set_page_config(
    page_title="SWC Fantasy Football",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Multi-page Navigation Setup ---
try:
    # Define pages with appropriate icons
    page_rosters = st.Page("page1.py", title="Team Rosters", icon="👥")
    page_stats = st.Page("page2.py", title="TD Stats", icon="📊")
    page_boxplots = st.Page("page3_scoring_boxplot.py", title="Scoring Dist.", icon="📈")
    page_race = st.Page("page4_cumulative_points_race.py", title="Points Race", icon="🏎️")
    page_map = st.Page("page5_titles_map.py", title="Championships", icon="🏆")

    # Create navigation with all pages
    pg = st.navigation([page_rosters, page_stats, page_boxplots, page_race, page_map])
    
    # Add global exception handling for data loading
    try:
        pg.run()
    except Exception as data_error:
        st.error("❌ An unexpected error occurred while loading data.")
        st.error(data_error)
        logger.error(f"Data loading error: {data_error}", exc_info=True)

except FileNotFoundError as e:
    st.error("❌ A page file was not found. Please ensure all page files exist.")
    st.error(e)
    logger.error(f"Page file not found: {e}")
except Exception as e:
    st.error("❌ An unexpected error occurred during app setup.")
    st.error(e)
    logger.error(f"App setup error: {e}", exc_info=True)