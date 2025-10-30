"""Aviation Edge API interface"""
from datetime import datetime
from typing import TypeVar, Type

import requests
from pydantic import ValidationError, BaseModel

from skytracker.models.api import API
from skytracker.models.api.aviation_edge import (AviationEdgeFlightTrackingResponse,
                                                 AviationEdgeAirlineDatabase,
                                                 AviationEdgeAirportDatabase,
                                                 AviationEdgeAirplaneDatabase)
from skytracker.models.state import State
from skytracker.models.airport import Airport
from skytracker.models.airline import Airline
from skytracker.models.aircraft import Aircraft
from skytracker.utils import log_and_raise, logger
from skytracker.settings import Settings


ModelType = TypeVar('ModelType', bound=BaseModel)


class AviationEdgeAPI(API):
    """Aviation Edge API"""

    RATE_LIMIT: int = 10
    """int: rate limit in seconds"""

    def __init__(self, settings: Settings) -> None:
        """Initialize API by storing API key

        Args:
            settings (Settings): settings with Aviation Edge API credentials
        """
        self._api_key: str = settings.aviation_edge_api_key
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
    
    def _get_data(self, endpoint: str, model: Type[ModelType],
                  arguments: list[str] = None) -> ModelType:
        """Get data from an endpoint with an expected response

        Args:
            endpoint (str): endpoint to get data from
            model (Type[ModelType]): expected response model
            arguments (list[str], optional): additional query arguments. Defaults to None.

        Raises:
            ValueError: if response does not match model
            
        Returns:
            ModelType: data response
        """
        # Assemble endpoint with arguments
        if arguments is None:
            arguments = []
        arguments += [f'key={self._api_key}']
        endpoint += '?' + '&'.join(arguments)

        # Retrieve data and parse response
        data = self._get_json(endpoint)
        try:
            response = model.model_validate(data)
        except ValidationError as err:
            log_and_raise(ValueError, f'Response does not match expected model', err)
        return response

    def get_states(self) -> list[State]:
        """Get list of aircraft states from Aviation Edge API

        Returns:
            list[State]: list of aircraft states
        """
        response = self._get_data('flights', AviationEdgeFlightTrackingResponse)
        return response.to_states()

    def get_airport_database(self) -> list[Airport]:
        """Get list of airports from Aviation Edge database

        Returns:
            list[Airport]: list of airports
        """
        response = self._get_data('airportDatabase', AviationEdgeAirportDatabase)
        return response.to_airports()

    def get_airline_database(self) -> list[Airline]:
        """Get list of airlines from Aviation edge database

        Returns:
            list[Airline]: list of airlines
        """
        response = self._get_data('airlineDatabase', AviationEdgeAirlineDatabase)
        return response.to_airlines()

    def get_aircraft_database(self) -> list[Aircraft]:
        """Get list of aircraft from Aviation edge database

        Returns:
            list[Aircraft]: list of aircraft
        """
        response = self._get_data('airplaneDatabase', AviationEdgeAirplaneDatabase)
        return response.to_aircraft()
