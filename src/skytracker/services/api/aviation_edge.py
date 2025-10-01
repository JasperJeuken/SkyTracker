"""Aviation Edge API interface"""
from datetime import datetime

import requests
from pydantic import ValidationError

from skytracker.models.api import API
from skytracker.models.api.aviation_edge import AviationEdgeFlightTrackingResponse
from skytracker.models.state import State
from skytracker.utils import log_and_raise, logger


class AviationEdgeAPI(API):
    """Aviation Edge API"""

    RATE_LIMIT: int = 10
    """int: rate limit in seconds"""

    def __init__(self, api_key: str) -> None:
        """Initialize API by storing API key

        Args:
            api_key (str): Aviation Edge API key
        """
        self._api_key: str = api_key
        self._last_request: datetime = datetime.fromtimestamp(0)
        self._base_url: str = 'https://aviation-edge.com/v2/public'
    
    def _get_json(self, endpoint: str, timeout: int = 10) -> dict:
        """Get JSON data from an API endpoint

        Args:
            endpoint (str): endpoint to get
            timeout (int, optional): request timeout in seconds. Defaults to 10 seconds.

        Returns:
            dict: received JSON data
        """
        # Check rate limiting
        if (datetime.now() - self._last_request).seconds < self.RATE_LIMIT:
            log_and_raise(ValueError, 'Too many Aviation Edge requests (wait at least 10 seconds)')
        
        # Set up request
        url = f'{self._base_url}/{endpoint}'

        # Perform request
        try:
            logger.debug(f'Requesting Aviation Edge data ({url})...')
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
        except requests.Timeout as exc:
            log_and_raise(TimeoutError, 'Could not get Aviation Edge data (timeout)', exc)
        except requests.ConnectionError as exc:
            log_and_raise(RuntimeError, 'Could not get Aviation Edge data (connection error)', exc)
        except requests.HTTPError as exc:
            log_and_raise(RuntimeError, 'Could not get Aviation edge data ' + \
                          f'(HTML error {response.status_code})', exc)
        
        # Parse response
        self._last_request = datetime.now()
        logger.debug(f'Received Aviation Edge data ({len(response.content)} bytes)')
        return response.json()

    def get_states(self) -> list[State]:
        """Get list of aircraft states from Aviation Edge API

        Returns:
            list[State]: list of aircraft states
        """
        # Retrieve data
        arguments = [f'key={self._api_key}']
        endpoint = 'flights'
        if len(arguments) > 0:
            endpoint += '?' + '&'.join(arguments)
        logger.debug('Requesting Aviation Edge states...')
        data = self._get_json(endpoint)

        # Parse data
        try:
            response = AviationEdgeFlightTrackingResponse.model_validate(data)
        except ValidationError as err:
            log_and_raise(ValueError, f'Expected Aviation Edge data not present', err)
        logger.debug(f'Received {len(response)} Aviation Edge states.')
        return response.to_states()
