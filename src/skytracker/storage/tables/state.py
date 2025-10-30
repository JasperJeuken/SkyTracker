"""Aircraft state table manager"""
from typing import Any

from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.table_manager import TableManager
from skytracker.storage.cache import Cache
from skytracker.models.state import State, MapState
from skytracker.models import flatten_model
from skytracker.storage.queries.state import (NearbyQuery, LatestBatchQuery, TrackQuery,
                                              LatestBatchMapQuery)
from skytracker.utils import logger
from skytracker.utils.analysis import search_object_list


class StateTableManager(TableManager[State]):
    """Async aircraft state table manager"""

    TABLE_NAME = 'state'
    """str: name of aircraft state table"""
    TABLE_FIELDS: dict[str, str] = {
        'time': "DateTime('UTC')",
        'data_source': "Enum('OPENSKY_NETWORK', 'AVIATION_EDGE')",
        'status': "Enum('UNKNOWN', 'EN_ROUTE', 'LANDED', 'STARTED')",
        'aircraft__iata': 'Nullable(FixedString(4))',
        'aircraft__icao': 'Nullable(FixedString(4))',
        'aircraft__icao24': 'Nullable(FixedString(6))',
        'aircraft__registration': 'Nullable(FixedString(10))',
        'airline__iata': 'Nullable(FixedString(3))',
        'airline__icao': 'Nullable(FixedString(3))',
        'airport__arrival_iata': 'Nullable(FixedString(3))',
        'airport__arrival_icao': 'Nullable(FixedString(4))',
        'airport__departure_iata': 'Nullable(FixedString(3))',
        'airport__departure_icao': 'Nullable(FixedString(4))',
        'flight__iata': 'Nullable(FixedString(7))',
        'flight__icao': 'FixedString(8)',
        'flight__number': 'Nullable(UInt16)',
        'geography__position': 'Point',
        'geography__geo_altitude': 'Nullable(FLOAT)',
        'geography__baro_altitude': 'Nullable(FLOAT)',
        'geography__heading': 'Nullable(FLOAT)',
        'geography__speed_horizontal': 'Nullable(FLOAT)',
        'geography__speed_vertical': 'Nullable(FLOAT)',
        'geography__is_on_ground': 'BOOLEAN',
        'transponder__squawk': 'Nullable(UInt16)',
        'transponder__squawk_time': "Nullable(DateTime('UTC'))"
    }
    """dict[str, str]: column_name - column_type pairs"""
    TABLE_KEYS: tuple[str] = ('flight__icao', 'time')
    """tuple[str]: keys used in database table"""

    def __init__(self, database: DatabaseManager) -> None:
        """Initialize table manager by storing database manager

        Args:
            database (DatabaseManager): ClickHouse database manager
        """
        super().__init__(database, Cache[State]())

    async def ensure_exists(self) -> None:
        """Ensure aircraft state table exists"""
        # Skip if table already exists
        if await self.exists():
            logger.info(f'Table "{self.TABLE_NAME}" exists')
            return

        # Create table
        fields = [f'{name} {data_type}' for name, data_type in self.TABLE_FIELDS.items()] 
        logger.info(f'Table "{self.TABLE_NAME}" does not exist, creating...')
        await self._database.create_table(self.TABLE_NAME, fields,
                                          'ENGINE MergeTree',
                                          f'ORDER BY ({", ".join(self.TABLE_KEYS)})',
                                          'SETTINGS index_granularity=8192')

    async def exists(self) -> bool:
        """Check if the aircraft state table exists

        Returns:
            bool: whether the aircraft state table exists
        """
        return await self._database.table_exists(self.TABLE_NAME)

    async def insert_states(self, states: list[State]) -> None:
        """Insert a list of states in the table

        Args:
            states (list[State]): list of states to insert
        """
        logger.debug(f'Setting cache with {len(states)}...')
        await self._cache.set(states)

        # Get columns and values
        flattened = [flatten_model(state) for state in states]
        rows = [list(flat.values()) for flat in flattened]
        columns = list(flattened[0].keys())

        # Insert into table
        logger.debug(f'Inserting {len(states)} states into database...')
        await self._database.insert(self.TABLE_NAME, rows, columns)

    async def insert_state(self, state: State) -> None:
        """Insert a state in the table

        Args:
            state (State): state to insert
        """
        await self.insert_states([state])

    async def get_track(self, callsign: str, duration: str, limit: int = 0) -> list[State]:
        """Get the state history of a specific aircraft

        Args:
            callsign (str): aircraft callsign (ICAO)
            duration (str): duration of track (i.e. "5h20m" or "10m20s")
            limit (int): maximum number of states to get (latest first, 0=all)

        Returns:
            list[State]: list of aircraft states
        """
        query = TrackQuery(callsign, duration, limit)
        return await self._run_query(query, self.TABLE_NAME)

    async def get_last_state(self, callsign: str) -> State | None:
        """Get the last known state of a specific aircraft

        Args:
            callsign (str): aircraft callsign (ICAO)

        Returns:
            State | None: last known aircraft state, or None if not found
        """
        states = await self.get_latest_batch()
        for state in states:
            if state.flight.icao == callsign:
                return state
        return None

    async def get_latest_batch(self, limit: int = 0,
                               lat_min: float | None = None, lat_max: float | None = None,
                               lon_min: float | None = None, lon_max: float | None = None) \
                                -> list[State]:
        """Get the latest batch of states in the table

        Args:
            limit (int, optional):  maximum number of states to get (0=all). Defaults to 0 (all).
            lat_min (float, optional): minimum latitude
            lat_max (float, optional): maximmum latitude
            lon_min (float, optional): minimum longitude
            lon_max (float, optional): maximum longitude

        Returns:
            list[State]: list of aircraft states in last batch
        """
        query = LatestBatchQuery(limit, lat_min, lat_max, lon_min, lon_max,
                                 self.TABLE_FIELDS.keys())
        return await self._run_query(query, self.TABLE_NAME)
    
    async def get_latest_batch_map(self, limit: int = 0,
                               lat_min: float | None = None, lat_max: float | None = None,
                               lon_min: float | None = None, lon_max: float | None = None) \
                               -> list[MapState]:
        """Get the latest batch of states in the table as simple map states

        Args:
            limit (int, optional):  maximum number of states to get (0=all). Defaults to 0 (all).
            lat_min (float, optional): minimum latitude
            lat_max (float, optional): maximmum latitude
            lon_min (float, optional): minimum longitude
            lon_max (float, optional): maximum longitude

        Returns:
            list[MapState]: list of simple map states in last batch
        """
        query = LatestBatchMapQuery(limit, lat_min, lat_max, lon_min, lon_max)
        return await self._run_query(query, self.TABLE_NAME)

    async def get_nearby(self, lat: float, lon: float,
                         radius: float = 50., limit: int = 0) -> list[State]:
        """Get aircraft states in range of a specific point

        Args:
            lat (float): point latitude
            lon (float): point longitude
            radius (float, optional): radius around point [km]. Defaults to 50.0 km.
            limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).

        Returns:
            list[State]: list of aircraft states near point
        """
        query = NearbyQuery(lat, lon, radius, limit)
        return await self._run_query(query, self.TABLE_NAME)

    async def count(self) -> int:
        """Get the number of states stored in the table

        Returns:
            int: number of states stored in table
        """
        query = f'SELECT COUNT(*) FROM {self.TABLE_NAME}'
        logger.debug(f'Requesting row count with "{query}"')
        return await self._database.sql_query(query)[0][0]
    
    async def search_state(self, fields: dict[str, Any], limit: int = 0) -> list[State]:
        """Search for states matching specific information

        Args:
            fields (dict[str, Any]): field-value pairs to search for
            limit (int, optional): maximum number of states to retrieve (0=all). Defaults to 0.

        Returns:
            list[State]: list of states matching fields
        """
        batch = await self.get_latest_batch()
        return search_object_list(batch, fields, limit)
