"""OpenSky API interface"""
import json
import time
import asyncio
from typing import Optional, Union
from datetime import datetime

import requests

from skytracker.models.state import State
from skytracker.storage import Storage


class OpenskyAPI:
    """OpenSky API object"""

    def __init__(self, credentials_file: str = 'credentials.json') -> None:
        """Initialize API by getting access token

        Args:
            credentials_file (str, optional): file with API credentials.
                Defaults to 'credentials.json'.
        """
        self._credentials_file: str = credentials_file
        self._access_token: str = self._get_access_token(self._credentials_file)
        self._last_access_token: datetime = datetime.now()
        self._last_request: datetime = datetime.fromtimestamp(0)
        self._base_url: str = 'https://opensky-network.org/api'

    def _get_access_token(self, credentials_file: str) -> str:
        """Request an API access token

        Args:
            credentials_file (str): file with API credentials

        Raises:
            TimeoutError: if request times out
            RuntimeError: if connection error or non-OK HTML response code

        Returns:
            str: received access token
        """
        # Read credentials
        with open(credentials_file, 'r', encoding='utf-8') as file:
            credentials = json.load(file)
        client_id = credentials['clientId']
        client_secret = credentials['clientSecret']

        # Generate post request
        token_url = 'https://auth.opensky-network.org/auth/realms/' + \
            'opensky-network/protocol/openid-connect/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        # Obtain the access token
        try:
            response = requests.post(token_url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.Timeout as exc:
            raise TimeoutError('Could not get access token (timeout)') from exc
        except requests.ConnectionError as exc:
            raise RuntimeError('Could not get access token (connection error)') from exc
        except requests.HTTPError as exc:
            raise RuntimeError(f'Could not get access token (err. {response.status_code})') from exc
        access_token = response.json()['access_token']
        return access_token

    def _update_access_token(self) -> None:
        """Update the internal API access token"""
        self._access_token = self._get_access_token(self._credentials_file)

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
            raise ValueError('Request too quickly after last request (wait at least 10 seconds)')

        # Check if access token should be updated
        if (datetime.now() - self._last_access_token).seconds > 20 * 60:
            self._update_access_token()
            self._last_access_token = datetime.now()

        # Set up request
        url = f'{self._base_url}/{endpoint}'
        headers = {'Authorization': f'Bearer {self._access_token}'}

        # Perform request
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.Timeout as exc:
            raise TimeoutError('Could not get data (timeout)') from exc
        except requests.ConnectionError as exc:
            raise RuntimeError('Could not get data (connection error)') from exc
        except requests.HTTPError as exc:
            if int(response.status_code) == 429:
                raise RuntimeError(f'Daily limit exceeded (error {response.status_code})') from exc
            raise RuntimeError(f'Could not get data (error {response.status_code})') from exc
        self._last_request = datetime.now()
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
                raise TypeError('Specified time must be datetime object')
            unix_timestamp = int(time.timestamp())
            arguments.append(f'time={unix_timestamp}')

        # Add ICAO24 codes
        if icao24 is not None:
            if isinstance(icao24, str):
                icao24 = [icao24]
            elif not isinstance(icao24, list):
                raise TypeError('Specified ICAO24 code must be string or list of strings')
            for code in icao24:
                if not isinstance(code, str):
                    raise TypeError('Specified ICAO24 code must be string or list of strings')
                arguments.append(f'icao24={code}')

        # Add bounding box
        if bbox is not None:
            if not isinstance(bbox, tuple) or len(bbox) != 4 or \
                any(not isinstance(v, (int, float)) for v in bbox):
                raise TypeError('Bounding box must be tuple of 4 numbers')
            arguments.append(f'lamin={bbox[0]}')
            arguments.append(f'lomin={bbox[1]}')
            arguments.append(f'lamax={bbox[2]}')
            arguments.append(f'lomax={bbox[3]}')

        # Retrieve data
        endpoint = 'states/all'
        if len(arguments) > 0:
            endpoint += '?' + '&'.join(arguments)
        data = self._get_json(endpoint)
        if 'states' not in data or 'time' not in data:
            raise ValueError('Expected keys not present')

        # Parse to state list
        return [State.from_raw([data['time']] + state + [0]) for state in data['states']]


async def collect_service(storage: Storage, repeat: int = 90,
                          credentials_file: str = 'credentials.json') -> None:
    """Service which periodically collects aircraft states and writes it to the state table

    Args:
        storage (Storage): database storage instance
        repeat (int, optional): period with which to collect states [sec]. Defaults to 90 sec.
        credentials_file (str, optional): path to credentials file for OpenSky API.
            Defaults to 'credentials.json'
    """
    # Start OpenSky API
    api = OpenskyAPI(credentials_file)

    # Start acquisition loop
    running = True
    while running:
        start_time = time.time()
        time_str = f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]'

        # Try to collect states and write to database
        try:
            states = api.get_states()
            await storage['state'].insert_states(states)
            print(f'{time_str} inserted {len(states)} states into database...')

        # Catch any exceptions
        except Exception as exc:
            print(f'{time_str} exception occured:')
            print(exc)

        # Repeat
        finally:
            elapsed_time = time.time() - start_time
            await asyncio.sleep(max(0, repeat - elapsed_time))
