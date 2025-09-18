"""Aircraft state table manager"""
from typing import Optional

from skytracker.storage.database_manager import DatabaseManager
from skytracker.storage.table_manager import TableManager
from skytracker.storage.cache import Cache
from skytracker.models.state import State
from skytracker.storage.table_query import TableQuery
from skytracker.storage.queries.state import NearbyQuery, LatestBatchQuery


class StateTableManager(TableManager):
    """Async aircraft state table manager"""

    TABLE_NAME = 'aircraft_states'
    """str: name of aircraft state table"""

    def __init__(self, database: DatabaseManager) -> None:
        """Initialize table manager by storing database manager

        Args:
            database (DatabaseManager): ClickHouse database manager
        """
        self._database: DatabaseManager = database
        self._cache: Cache[State] = Cache[State]()

    async def ensure_exists(self) -> None:
        """Ensure aircraft state table exists"""
        # Skip if table already exists
        if await self.exists():
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
        await self._cache.set(states)
        rows = [list(state.to_json().values()) for state in states]
        columns = State.FIELDS
        await self._database.insert(self.TABLE_NAME, rows, columns)

    async def insert_state(self, state: State) -> None:
        """Insert a state in the table

        Args:
            state (State): state to insert
        """
        await self.insert_states([state])

    # async def sql_query(self, sql_query: str) -> list[State]:
    #     """Select rows from the aircraft state table with an SQL query

    #     Args:
    #         sql_query (str): SQL query

    #     Returns:
    #         list[State]: list of matching states (if any)
    #     """
    #     if not isinstance(sql_query, str) or len(sql_query) < 1:
    #         raise ValueError(f'Invalid SQL query: "{sql_query}"')
    #     if not sql_query.endswith(';'):
    #         sql_query += ';'
    #     rows = await self._database.query(sql_query)
    #     return [State.from_raw(row) for row in rows]
    
    async def _run_query(self, query: TableQuery) -> list[State]:
        """Run a table query

        Args:
            query (TableQuery): table query to run

        Returns:
            list[State]: queried list of states
        """
        if not await self._cache.empty():
            return await query.from_cache(await self._cache.get())
        rows = await query.from_server(self.TABLE_NAME, self._database)
        return [State.from_raw(row) for row in rows]

    async def get_aircraft_history(self, icao24: str, limit: int = 0) -> list[State]:
        """Get the state history of a specific aircraft

        Args:
            icao24 (str): aircraft ICAO 24-bit address (hex)
            limit (int): maximum number of states to get (latest first, 0=all)

        Returns:
            list[State]: list of aircraft states
        """
        # Catch incorrect arguments
        if not isinstance(icao24, str) or len(icao24) != 6:
            raise ValueError(f'ICAO 24-bit address must be a 6-character string, got "{icao24}"')
        if not isinstance(limit, int) or limit < 0:
            raise ValueError(f'Query limit must be an integer larger than 0, got "{limit}"')
        
        # Run select query
        query = f"SELECT * FROM {self.TABLE_NAME} WHERE icao24='{icao24}' ORDER BY time DESC"
        if limit > 0:
            query += f' LIMIT {limit}'
        result = await self.sql_query(query)
        return result
    
    async def get_last_aircraft_state(self, icao24: str) -> Optional[State]:
        """Get the last known state of a specific aircraft

        Args:
            icao24 (str): aircraft ICAO 24-bit address (hex)

        Returns:
            Optional[State]: last known aircraft state, or None if not found
        """
        result = await self.get_aircraft_history(icao24, limit=1)
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
        return await self._run_query(query)
    
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
        return await self._run_query(query)

    # def _get_default_batch_query(self) -> str:
    #     """Get the default SQL query which selects the latest batch from the table

    #     Returns:
    #         str: default SQL query which selects latest batch
    #     """
    #     return f'SELECT * FROM {self.TABLE_NAME} WHERE time=(SELECT MAX(time) ' + \
    #            f'FROM {self.TABLE_NAME})'
    
    # async def _get_latest_batch_cache(self, limit: int = 0,
    #                                   min_lat: Optional[float] = None, 
    #                                   max_lat: Optional[float] = None,
    #                                   min_lon: Optional[float] = None, 
    #                                   max_lon: Optional[float] = None) -> list[State]:
    #     """Get the latest batch of states from the local cache

    #     Args:
    #         limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).
    #         min_lat (float, optional): minimum latitude. Defaults to None.
    #         max_lat (float, optional): maximum latitude. Defaults to None.
    #         min_lon (float, optional): minimum longitude. Defaults to None.
    #         max_lon (float, optional): maximum longitude. Defaults to None.

    #     Returns:
    #         list[State]: filtered list of aircraft states from cache
    #     """
    #     # Get states from cache
    #     states = filter_states(await self._cache.get(), 'latitude', 'longitude')
        
    #     # Filter bounding box
    #     if all(val is not None for val in (min_lat, max_lat, min_lon, max_lon)):
    #         states = [state for state in states if min_lat <= state.latitude <= max_lat and \
    #                                                min_lon <= state.longitude <= max_lon]
        
    #     # Return states (limit if specified)
    #     if limit > 0:
    #         return states[:limit]
    #     return states
    
    # async def _get_latest_batch_server(self, limit: int = 0,
    #                                    min_lat: Optional[float] = None, 
    #                                    max_lat: Optional[float] = None,
    #                                    min_lon: Optional[float] = None, 
    #                                    max_lon: Optional[float] = None) -> list[State]:
    #     """Get the latest batch of states from the ClickHouse server

    #     Args:
    #         limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).
    #         min_lat (float, optional): minimum latitude. Defaults to None.
    #         max_lat (float, optional): maximum latitude. Defaults to None.
    #         min_lon (float, optional): minimum longitude. Defaults to None.
    #         max_lon (float, optional): maximum longitude. Defaults to None.

    #     Returns:
    #         list[State]: filtered list of aircraft states from server
    #     """
    #     # Create default query
    #     query = self._get_default_batch_query()
        
    #     # Add bounding box condition if specified
    #     if all(val is not None for val in (min_lat, max_lat, min_lon, max_lon)):
    #         query += f' AND latitude BETWEEN {min_lat} AND {max_lat}' + \
    #                  f' AND longitude BETWEEN {min_lon} AND {max_lon}'
        
    #     # Add limit if specified
    #     if limit:
    #         query += f' LIMIT {limit}'
        
    #     # Run query and return results
    #     return await self.query(query)
    
    # async def get_latest_batch(self, limit: int = 0,
    #                            min_lat: Optional[float] = None, max_lat: Optional[float] = None,
    #                            min_lon: Optional[float] = None, max_lon: Optional[float] = None) \
    #                             -> list[State]:
    #     """Get the latest batch of states in the table

    #     Args:
    #         limit (int, optional):  maximum number of states to get (0=all). Defaults to 0 (all).
    #         min_lat (float, optional): minimum latitude
    #         max_lat (float, optional): maximmum latitude
    #         min_lon (float, optional): minimum longitude
    #         max_lon (float, optional): maximum longitude

    #     Returns:
    #         list[State]: list of aircraft states in last batch
    #     """
    #     # Catch incorrect arguments
    #     if not isinstance(limit, int) or limit < 0:
    #         raise ValueError(f'Query limit must be an integer larger than 0, got "{limit}"')
    #     is_not_none = [val is not None for val in (min_lat, max_lat, min_lon, max_lon)]

    #     if any(is_not_none) and not all(is_not_none):
    #         raise ValueError('All bounding box values must be numeric')
        
    #     # Use cached data if available
    #     if not await self._cache.empty():
    #         return await self._get_latest_batch_cache(limit, min_lat, max_lat, min_lon, max_lon)
        
    #     # Use server data otherwise
    #     return await self._get_latest_batch_server(limit, min_lat, max_lat, min_lon, max_lon)
    
    # async def _get_in_radius_cache(self, lat: float, lon: float,
    #                                radius: float = 50., limit: int = 0) -> list[State]:
    #     """Get aircraft states in range of a specific point from local cache

    #     Args:
    #         lat (float): point latitude
    #         lon (float): point longitude
    #         radius (float, optional): radius around point [km]. Defaults to 50.0 [km].
    #         limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).

    #     Returns:
    #         list[State]: list of aircraft states near point from cache
    #     """
    #     # Get states from cache
    #     states = filter_states(await self._cache.get(), 'latitude', 'longitude')
        
    #     # Filter radius
    #     states = [state for state in states if distance_between_points(state.latitude,
    #                                                                    state.longitude,
    #                                                                    lat, lon) <= radius]

    #     # Return states (limit if specified)
    #     if limit > 0:
    #         return states[:limit]
    #     return states

    # async def _get_in_radius_server(self, lat: float, lon: float,
    #                                 radius: float = 50., limit: int = 0) -> list[State]:
    #     """Get aircraft states in range of a specific point from ClickHouse server

    #     Args:
    #         lat (float): point latitude
    #         lon (float): point longitude
    #         radius (float, optional): radius around point [km]. Defaults to 50.0 [km].
    #         limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).

    #     Returns:
    #         list[State]: list of aircraft states near point from server
    #     """
    #     # Create default query
    #     query = self._get_default_batch_query()
        
    #     # Add radius search
    #     lat_rad, lon_rad = radians(lat), radians(lon)
    #     earth_radius = 6371.
    #     query += f' AND {earth_radius} * ACOS(SIN(RADIANS(latitude)) * SIN({lat_rad}) + ' + \
    #              f'COS(RADIANS(latitude)) * COS({lat_rad}) * COS(RADIANS(longitude) - ' + \
    #              f'{lon_rad})) <= {radius}'
        
    #     # Add limit if specified
    #     if limit:
    #         query += f' LIMIT {limit}'
        
    #     # Run query and return results
    #     return await self.query(query)

    # async def get_in_radius(self, lat: float, lon: float,
    #                         radius: float = 50., limit: int = 0) -> list[State]:
    #     """Get aircraft states in range of a specific point

    #     Args:
    #         lat (float): point latitude
    #         lon (float): point longitude
    #         radius (float, optional): radius around point [km]. Defaults to 50.0 km.
    #         limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).

    #     Returns:
    #         list[State]: list of aircraft states near point
    #     """
    #     # Catch incorrect arguments
    #     if not isinstance(limit, int) or limit < 0:
    #         raise ValueError(f'Query limit must be an integer larger than 0, got "{limit}"')
    #     if not isinstance(radius, (int, float)) or radius <= 0:
    #         raise ValueError(f'Radius must be a float (or integer) larger than 0, got {radius}')

    #     # Use cached data if available
    #     if not await self._cache.empty():
    #         return await self._get_in_radius_cache(lat, lon, radius, limit)
        
    #     # Use server data otherwise
    #     return await self._get_in_radius_server(lat, lon, radius, limit)

    async def count(self) -> int:
        """Get the number of states stored in the table

        Returns:
            int: number of states stored in table
        """
        result = await self.sql_query(f'SELECT COUNT(*) FROM {self.TABLE_NAME}')
        return result[0][0]
