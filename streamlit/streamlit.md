# Streamlit App Documentation

## Pages Using API Data

### page1.py (Team Rosters)
- Makes direct API calls to fetch team data: 
  ```python
  team_api_response = swc.call_api_endpoint(base_url, swc.LIST_TEAMS_ENDPOINT)
  ```
- Stores data in session state for other pages to use

### page2.py (TD Stats)
- Uses data loaded by page1 from session state: 
  ```python
  flat_team_df = st.session_state['flat_team_df_ordered'].copy()
  ```
- Does not make direct API calls itself
- Actually uses random generated data for visualization (not real TD data)

### page3_scoring_boxplot.py (Scoring Dist.)
- Makes direct API calls: 
  ```python
  response = swc.call_api_endpoint(base_url, API_ENDPOINT)
  ```
- Falls back to sample data if API fails

### page4_cumulative_points_race.py (Points Race)
- Makes direct API calls: 
  ```python
  response = swc.call_api_endpoint(base_url, API_ENDPOINT)
  ```
- Uses sample data as fallback when API data is unavailable

## Pages Using CSV Files

### page5_titles_map.py (Championships)
- The only page using CSV data directly: 
  ```python
  load_championship_data(CSV_FILE_PATH)
  ```
- Loads from `data/ffl-history.csv`
- Creates a sample CSV if the file doesn't exist

## Summary
- **Direct API Calls**: pages 1, 3, 4
- **Indirect API Data** (from session state): page 2
- **Direct CSV Files**: page 5 only