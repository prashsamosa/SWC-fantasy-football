"""
Championship Titles Map page showing geographic distribution of fantasy league champions.
Visualizes where champions are located with an interactive choropleth map.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import logging
import os

logger = logging.getLogger(__name__)

# --- Page UI ---
st.header("🏆 Fantasy League Championship Map")
st.markdown(
    "Explore where fantasy football champions reside across the United States. "
    "The map highlights states with the most championship titles."
)

# --- Configuration ---
CSV_FILE_PATH = os.path.join('data', 'ffl-history.csv')

# --- Helper Functions ---
def load_championship_data(file_path: str) -> pd.DataFrame:
    """
    Loads championship data from a CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame with championship data
    """
    try:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            
            # Check if required columns exist
            required_columns = {'year', 'owner', 'city', 'state'}
            if not required_columns.issubset(df.columns):
                st.warning(f"⚠️ CSV file at '{file_path}' is missing some required columns. Creating a sample file.")
                return create_sample_csv()
                
            # Process valid data
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
            df.dropna(subset=['year', 'state'], inplace=True)
            df['state'] = df['state'].str.strip().str.upper()
            return df
        else:
            st.info("📝 Championship data file not found. Creating a sample data file.")
            return create_sample_csv()
    except Exception as e:
        st.error(f"❌ Error loading championship data: {str(e)}")
        logger.error(f"CSV loading error: {e}", exc_info=True)
        return create_sample_csv()

def create_sample_csv() -> pd.DataFrame:
    """
    Creates a sample DataFrame with championship data and saves it to CSV.
    
    Returns:
        DataFrame with sample championship data
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(CSV_FILE_PATH), exist_ok=True)
        
        # Create realistic sample data with good geographic distribution
        data = {
            'year': [2023, 2022, 2021, 2020, 2019, 2018, 2017, 2023, 2022, 2021, 2020, 2019],
            'owner': [
                'Michael Johnson', 'Emily Williams', 'David Brown', 'Sarah Miller',
                'James Wilson', 'Jennifer Taylor', 'Robert Davis', 'Lisa Garcia',
                'John Martinez', 'Patricia Moore', 'Thomas Anderson', 'Michelle Lee'
            ],
            'city': [
                'New York', 'Los Angeles', 'Chicago', 'Dallas', 
                'Phoenix', 'Philadelphia', 'Houston', 'Miami',
                'Seattle', 'Denver', 'Atlanta', 'Boston'
            ],
            'state': [
                'NY', 'CA', 'IL', 'TX', 
                'AZ', 'PA', 'TX', 'FL',
                'WA', 'CO', 'GA', 'MA'
            ]
        }
        df = pd.DataFrame(data)
        
        # Save the sample data to disk
        df.to_csv(CSV_FILE_PATH, index=False)
        
        st.info("""
            ℹ️ Created a sample championship data file with fictional winners.
            
            Replace with your actual data for production use by editing:
            `data/ffl-history.csv`
        """)
        
        return df
    except Exception as e:
        st.error(f"❌ Could not create sample data: {str(e)}")
        logger.error(f"Sample data creation error: {e}")
        
        # Return minimal working data
        return pd.DataFrame({
            'year': [2023, 2022], 
            'owner': ['Sample Owner 1', 'Sample Owner 2'],
            'city': ['Sample City', 'Sample City'],
            'state': ['NY', 'CA']
        })

# --- Main Logic ---
championship_df = load_championship_data(CSV_FILE_PATH)

if not championship_df.empty:
    # --- Sidebar Controls ---
    st.sidebar.title("Visualization Options")
    
    # Year range filter
    years = sorted(championship_df['year'].unique(), reverse=True)
    if len(years) > 1:
        year_min, year_max = min(years), max(years)
        selected_years = st.sidebar.slider(
            'Year Range', 
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max)
        )
        
        # Filter by selected years
        year_filtered_df = championship_df[
            (championship_df['year'] >= selected_years[0]) & 
            (championship_df['year'] <= selected_years[1])
        ]
    else:
        year_filtered_df = championship_df
    
    # State filter
    unique_states = sorted(year_filtered_df['state'].unique())
    selected_states = st.sidebar.multiselect(
        'Filter by State', 
        unique_states,
        default=unique_states
    )
    
    # Color scheme selection
    color_scheme = st.sidebar.selectbox(
        'Map Color Scheme',
        ['Reds', 'Blues', 'Greens', 'Purples', 'Oranges'],
        index=0
    )
    
    st.sidebar.divider()
    st.sidebar.subheader("📊 Data Sources")
    st.sidebar.text("Local CSV File (data/ffl-history.csv)")

    # Apply state filter
    if selected_states:
        filtered_championship_df = year_filtered_df[year_filtered_df['state'].isin(selected_states)]
    else:
        filtered_championship_df = year_filtered_df.copy()
        selected_states = unique_states  # Default to all states

    if not filtered_championship_df.empty:
        # --- Calculate Trophy Counts ---
        trophy_count_df = filtered_championship_df.groupby('state', as_index=False)['year'].count()
        trophy_count_df.columns = ['state_code', 'trophy_count']
        
        # Add states with 0 trophies for complete map coverage
        all_states_df = pd.DataFrame({'state_code': selected_states})
        trophy_count_df = pd.merge(all_states_df, trophy_count_df, on='state_code', how='left').fillna(0)
        trophy_count_df['trophy_count'] = trophy_count_df['trophy_count'].astype(int)

        # --- Generate Map ---
        if not trophy_count_df.empty:
            fig = go.Figure(data=go.Choropleth(
                locations=trophy_count_df['state_code'],
                z=trophy_count_df['trophy_count'],
                locationmode='USA-states',
                colorscale=color_scheme,
                colorbar_title="Championships",
                colorbar_ticksuffix="",
                zmin=0,
                hovertemplate='<b>%{location}</b><br>Championships: %{z}<extra></extra>'
            ))

            fig.update_layout(
                title=f'Fantasy Football Championships by State ({selected_years[0]}-{selected_years[1]})',
                geo=dict(
                    scope='usa',
                    showlakes=True,
                    lakecolor='rgba(0,105,148,0.3)',
                    bgcolor='rgba(0,0,0,0)'
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, b=0, t=30)
            )
            
            # Display the map
            st.plotly_chart(fig, use_container_width=True)
            
            # Add legend explaining the map
            col1, col2 = st.columns([1, 1])
            with col1:
                total_championships = trophy_count_df['trophy_count'].sum()
                states_with_champs = (trophy_count_df['trophy_count'] > 0).sum()
                st.metric("Total Championships", total_championships)
                
            with col2:
                top_state = trophy_count_df.loc[trophy_count_df['trophy_count'].idxmax()]
                if top_state['trophy_count'] > 0:
                    st.metric(
                        "Top State", 
                        top_state['state_code'], 
                        f"{top_state['trophy_count']} championships"
                    )
                else:
                    st.metric("Top State", "None", "0 championships")
        else:
            st.warning("⚠️ No trophy data available for the selected states.")

        # --- Championship History Table ---
        st.subheader("Championship History")
        
        # Add search box
        search_term = st.text_input("🔍 Search by Owner Name or City", "")
        
        # Apply search filter if provided
        display_df = filtered_championship_df
        if search_term:
            search_term = search_term.lower()
            display_df = display_df[
                display_df['owner'].str.lower().str.contains(search_term) |
                display_df['city'].str.lower().str.contains(search_term)
            ]
        
        # Display filtered results
        if not display_df.empty:
            # Sort by year (descending)
            display_df = display_df[['year', 'owner', 'city', 'state']].sort_values(by="year", ascending=False)
            
            # Format the dataframe for display
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "year": st.column_config.NumberColumn("Year", format="%d"),
                    "owner": st.column_config.TextColumn("Champion"),
                    "city": st.column_config.TextColumn("City"),
                    "state": st.column_config.TextColumn("State")
                }
            )
        else:
            st.info("No results match your search criteria.")

    else:
        st.warning("⚠️ No championship data matches the selected filters.")

else:
    st.error("❌ Could not load championship data. Please check the logs for more details.")