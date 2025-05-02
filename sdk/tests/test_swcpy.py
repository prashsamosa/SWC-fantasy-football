import pytest
from swcpy import SWCClient 
from swcpy import SWCConfig
from swcpy.schemas import League, Team, Player, Performance
from io import BytesIO 
import pyarrow.parquet as pq 
import pandas as pd 
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
 
def test_health_check(): 
    """Tests health check from SDK"""
    # Using environment variable instead of hardcoded URL
    config = SWCConfig(backoff=False)
    client = SWCClient(config)    
    response = client.get_health_check()
    assert response.status_code == 200
    assert response.json() == {"message": "API health check successful"}

def test_list_leagues(): 
    """Tests get leagues from SDK"""
    # Using environment variable instead of hardcoded URL
    config = SWCConfig(backoff=False)
    client = SWCClient(config)    
    leagues_response = client.list_leagues()
    # Assert the endpoint returned a list object
    assert isinstance(leagues_response, list)
    # Assert each item in the list is an instance of Pydantic League object
    for league in leagues_response:
        assert isinstance(league, League)
    # Assert that 5 League objects are returned
    assert len(leagues_response) == 5

def test_bulk_player_file_parquet(): 
    """Tests bulk player download through SDK - Parquet"""
    # Using environment variable instead of hardcoded URL
    config = SWCConfig(bulk_file_format="parquet") 
    client = SWCClient(config)    

    player_file_parquet = client.get_bulk_player_file()

    # Assert the file has the correct number of records (including header)
    player_table = pq.read_table(BytesIO(player_file_parquet)) 
    player_df = player_table.to_pandas()
    assert len(player_df) == 1018