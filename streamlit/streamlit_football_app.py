import streamlit as st
import logging
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

# Set base_url from environment variable or fallback default
if 'base_url' not in st.session_state:
    st.session_state['base_url'] = os.getenv('BASE_URL', 'http://127.0.0.1:8000/')

# Configure logging
logging.basicConfig(
    filename='football_app.log',
    level=logging.INFO,
)

# Page config
st.set_page_config(page_title="Football App", page_icon=":material/sports_football:")

# Navigation pages
page_1 = st.Page("page1.py", title="Team Rosters", icon=":material/trophy:")
page_2 = st.Page("page2.py", title="Team Stats", icon=":material/star_border:")

pg = st.navigation([page_1, page_2])
pg.run()
