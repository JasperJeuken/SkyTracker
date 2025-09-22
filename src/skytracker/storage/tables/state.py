"""Aircraft state table manager"""
from typing import Optional

from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.table_manager import TableManager
from skytracker.storage.cache import Cache
from skytracker.models.state import State
from skytracker.storage.queries.state import NearbyQuery, LatestBatchQuery, TrackQuery
from skytracker.utils import logger, log_and_raise


class StateTableManager(TableManager[State]):
    """Async aircraft state table manager"""

    TABLE_NAME = 'aircraft_states'
    """str: name of aircraft state table"""

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
            logger.debug(f'Table "{self.TABLE_NAME}" exists')
            return

        # Fields for state table
        fields = [
            'time UInt32 NOT NULL',
            'icao24 FixedString(6) NOT NULL',
            'callsign Nullable(FixedString(8))',
            'origin_country String NOT NULL',
            'time_position Nullable(UInt32)',
            'last_contact UInt32 NOT NULL',
            'longitude Nullable(Float64)',
            'latitude Nullable(Float64)',
            'baro_altitude Nullable(Float64)',
            'on_ground Bool NOT NULL',
            'velocity Nullable(Float64)',
            'true_track Nullable(Float64)',
            'vertical_rate Nullable(Float64)',
            'sensors Array(UInt32)',
            'geo_altitude Nullable(Float64)',
            'squawk Nullable(String)',
            'spi Bool NOT NULL',
            'position_source UInt8 NOT NULL',
            'category UInt8 NOT NULL'
        ]

        # Create table
        logger.info(f'Table "{self.TABLE_NAME}" does not exist, creating...')
        await self._database.create_table(self.TABLE_NAME, fields,
                                          'ENGINE MergeTree',
                                          'ORDER BY (icao24, time)',
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
        rows = [list(state.to_json().values()) for state in states]
        columns = State.FIELDS
        logger.debug(f'Inserting {len(states)} into database...')
        await self._database.insert(self.TABLE_NAME, rows, columns)

    async def insert_state(self, state: State) -> None:
        """Insert a state in the table

        Args:
            state (State): state to insert
        """
        await self.insert_states([state])

    async def get_track(self, icao24: str, duration: str, limit: int = 0) -> list[State]:
        """Get the state history of a specific aircraft

        Args:
            icao24 (str): aircraft ICAO 24-bit address (hex)
            duration (str): duration of track (i.e. "5h20m" or "10m20s")
            limit (int): maximum number of states to get (latest first, 0=all)

        Returns:
            list[State]: list of aircraft states
        """
        query = TrackQuery(icao24, duration, limit)
        return await self._run_query(query, self.TABLE_NAME)

    async def get_last_state(self, icao24: str) -> Optional[State]:
        """Get the last known state of a specific aircraft

        Args:
            icao24 (str): aircraft ICAO 24-bit address (hex)

        Returns:
            Optional[State]: last known aircraft state, or None if not found
        """
        result = await self.get_track(icao24, '365d', limit=1)
        if len(result) == 0:
            return None
        return result[0]

    async def get_latest_batch(self, limit: int = 0,
                               lat_min: Optional[float] = None, lat_max: Optional[float] = None,
                               lon_min: Optional[float] = None, lon_max: Optional[float] = None) \
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
        query = LatestBatchQuery(limit, lat_min, lat_max, lon_min, lon_max)
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
