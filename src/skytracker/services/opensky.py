"""OpenSky API interface"""
import json
import time
import asyncio
from typing import Optional, Union, Literal
from datetime import datetime

import requests

from skytracker.models.state import State
from skytracker.storage import Storage
from skytracker.utils import logger, log_and_raise
from skytracker.settings import settings


class OpenskyAPI:
    """OpenSky API object"""

    def __init__(self, client_id: str, client_secret: str) -> None:
        """Initialize API by getting access token
        
        Args:
            client_id (str): OpenSky Network API client ID
            client_secret (str): OpenSky Network API client secret
        """
        self._credentials: dict[Literal['client_id', 'client_secret'], str] = {
            'client_id': client_id,
            'client_secret': client_secret
        }
        self._access_token: str = self._get_access_token()
        self._last_access_token: datetime = datetime.now()
        self._last_request: datetime = datetime.fromtimestamp(0)
        self._base_url: str = 'https://opensky-network.org/api'

    def _get_access_token(self) -> str:
        """Request an API access token

        Raises:
            TimeoutError: if request times out
            RuntimeError: if connection error or non-OK HTML response code

        Returns:
            str: received access token
        """
        # Generate post request
        token_url = 'https://auth.opensky-network.org/auth/realms/' + \
            'opensky-network/protocol/openid-connect/token'
        data = {
            'grant_type': 'client_credentials',
            **self._credentials
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # Obtain the access token
        try:
            logger.debug('Requesting new OpenSky access token...')
            response = requests.post(token_url, data=data, headers=headers, timeout=5)
            response.raise_for_status()
        except requests.Timeout as exc:
            log_and_raise(TimeoutError, 'Could not get OpenSky access token (timeout)', exc)
        except requests.ConnectionError as exc:
            log_and_raise(RuntimeError,
                          'Could not get OpenSky access token (connection error)', exc)
        except requests.HTTPError as exc:
            log_and_raise(RuntimeError,
                          f'Could not get OpenSky access token (HTML error {response.status_code})',
                          exc)

        # Parse response
        access_token = response.json()['access_token']
        logger.debug(f'Received new OpenSky access token ({len(access_token)} chars).')
        return access_token

    def _update_access_token(self) -> None:
        """Update the internal API access token"""
        self._access_token = self._get_access_token()

    def _get_json(self, endpoint: str) -> dict:
        """Get JSON data from an API endpoint

        Args:
            endpoint (str): endpoint to get

        Raises:
            TimeoutError: if request times out
            RuntimeError: if connection error or non-OK HTML response code

        Returns:
            dict: received JSON data
        """
        # Check rate limiting
        if (datetime.now() - self._last_request).seconds < 10:
            log_and_raise(ValueError, 'Too many OpenSky requests (wait at least 10 seconds)')

        # Check if access token should be updated
        if (datetime.now() - self._last_access_token).seconds > 20 * 60:
            logger.debug('OpenSky access token is older than 20 minutes, updating...')
            self._update_access_token()
            self._last_access_token = datetime.now()

        # Set up request
        url = f'{self._base_url}/{endpoint}'
        headers = {'Authorization': f'Bearer {self._access_token}'}

        # Perform request
        try:
            logger.debug(f'Requesting OpenSky data ({url})...')
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.Timeout as exc:
            log_and_raise(TimeoutError, 'Could not get OpenSky data (timeout)', exc)
        except requests.ConnectionError as exc:
            log_and_raise(RuntimeError, 'Could not get OpenSky data (connection error)', exc)
        except requests.HTTPError as exc:
            if int(response.status_code) == 429:
                log_and_raise(RuntimeError,
                              f'Daily OpenSky limit exceeded (HTML error {response.status_code})',
                              exc)
            log_and_raise(RuntimeError,
                          f'Could not get OpenSky data (HTML error {response.status_code})', exc)

        # Parse response
        self._last_request = datetime.now()
        logger.debug(f'Received OpenSky data ({len(response.content)} bytes)')
        return response.json()

    def get_states(self, time: Optional[datetime] = None,
                   icao24: Optional[Union[str, list[str]]] = None,
                   bbox: Optional[tuple[float, float, float, float]] = None) -> list[State]:
        """Get aircraft states

        Args:
            time (Optional[datetime], optional): time to receive states from. Defaults to None.
            icao24 (Optional[Union[str, list[str]]], optional): one or more ICAO24 codes of
                aircraft to retrieve. Defaults to None.
            bbox (Optional[tuple[float, float, float, float]], optional): area to receive flights
                in (WGS-84: lat0, lon0, lat1, lon1). Defaults to None.

        Returns:
            list[State]: list of states received
        """
        arguments = []

        # Add timestamp
        if time is not None:
            if not isinstance(time, datetime):
                log_and_raise(TypeError, f'Specified time not of correct type ({type(time)})')
            unix_timestamp = int(time.timestamp())
            arguments.append(f'time={unix_timestamp}')

        # Add ICAO24 codes
        if icao24 is not None:
            if isinstance(icao24, str):
                icao24 = [icao24]
            elif not isinstance(icao24, list):
                log_and_raise(TypeError,
                              f'Specified ICAO24 list not of correct type ({type(icao24)})')
            for code in icao24:
                if not isinstance(code, str):
                    log_and_raise(TypeError,
                                  f'Specified ICAO24 code not of correct type ({type(code)})')
                arguments.append(f'icao24={code}')

        # Add bounding box
        if bbox is not None:
            if not isinstance(bbox, tuple) or len(bbox) != 4 or \
                any(not isinstance(v, (int, float)) for v in bbox):
                log_and_raise(TypeError, f'Bounding box not of correct type ({type(bbox)})')
            arguments.append(f'lamin={bbox[0]}')
            arguments.append(f'lomin={bbox[1]}')
            arguments.append(f'lamax={bbox[2]}')
            arguments.append(f'lomax={bbox[3]}')

        # Retrieve data
        endpoint = 'states/all'
        if len(arguments) > 0:
            endpoint += '?' + '&'.join(arguments)
        logger.debug(f'Requesting OpenSky states from "{endpoint}"...')
        data = self._get_json(endpoint)
        if 'states' not in data or 'time' not in data:
            log_and_raise(ValueError, f'Expected OpenSky data not present ({data.keys()})')

        # Parse to state list
        logger.debug(f'Received {len(data['states'])} OpenSky states (time={data['time']}).')
        return [State.from_raw([data['time']] + state + [0]) for state in data['states']]


async def opensky_service(storage: Storage, repeat: int = 90) -> None:
    """Service which periodically collects aircraft states and writes it to the state table

    Args:
        storage (Storage): database storage instance
        repeat (int, optional): period with which to collect states [sec]. Defaults to 90 sec.
    """
    logger.debug('Starting OpenSky service...')

    # Start OpenSky API
    api = OpenskyAPI(settings.opensky_client_id, settings.opensky_client_secret)

    # Start acquisition loop
    running = True
    while running:
        start_time = time.time()

        # Try to collect states and write to database
        try:
            states = api.get_states()
            await storage['state'].insert_states(states)
            logger.info(f'Inserted {len(states)} OpenSky states into database.')

        # Catch any exceptions
        except Exception as exc:
            logger.error(f'OpenSky collection error occurred: "{exc}"')

        # Repeat
        finally:
            elapsed_time = time.time() - start_time
            await asyncio.sleep(max(0, repeat - elapsed_time))
