"""
API client for interacting with the Fantasy Football backend.
Provides functions to make API calls and handle responses.
"""
import logging
import httpx
from typing import Dict, Any, Optional

# API Endpoints
LIST_TEAMS_ENDPOINT = "/v0/teams/"

logger = logging.getLogger(__name__)

def call_api_endpoint(
    base_url: str,
    api_endpoint: str, 
    api_params: Optional[Dict[str, Any]] = None,
    timeout: int = 10
) -> httpx.Response:
    """
    Makes an API request to the specified endpoint.
    
    Args:
        base_url: Base URL of the API
        api_endpoint: API endpoint to call
        api_params: Optional query parameters
        timeout: Request timeout in seconds
        
    Returns:
        httpx.Response object containing the API response
        
    Note:
        Returns a 500 status code response object on error
    """
    try:
        logger.debug(f"Calling API: {base_url}{api_endpoint}")
        with httpx.Client(base_url=base_url, timeout=timeout) as client: 
            response = client.get(api_endpoint, params=api_params)
            response.raise_for_status()
            logger.debug(f"API call successful: {response.status_code}")
            return response
            
    except httpx.TimeoutException:
        logger.error(f"Request timed out: {base_url}{api_endpoint}")
        return httpx.Response(status_code=504, content=b"Request timed out")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e}")
        return e.response
        
    except Exception as e:
        logger.error(f"API call failed: {str(e)}", exc_info=True)
        return httpx.Response(status_code=500, content=str(e).encode())