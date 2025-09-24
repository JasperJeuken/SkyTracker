"""State table queries"""
from typing import Optional
from math import radians

from skytracker.storage.table_query import TableQuery
from skytracker.models.state import State
from skytracker.storage.database_manager import DatabaseManager
from skytracker.utils.analysis import filter_states
from skytracker.utils.conversions import datetime_ago_from_time_string
from skytracker.utils.geographic import (distance_between_points, normalize_longitude_bbox,
                                         shift_longitude_into_range)
from skytracker.utils import logger, log_and_raise


class LatestBatchQuery(TableQuery[State]):
    """Query to select the latest aircraft states (with optional bounding box)"""

    allows_cache = True

    def __init__(self, limit: int = 0,
                 lat_min: Optional[float] = None, lat_max: Optional[float] = None,
                 lon_min: Optional[float] = None, lon_max: Optional[float] = None) -> None:
        """Initialize query with optional arguments

        Args:
            limit (int, optional): maximum number of states to get (0=all). Defaults to 0.
            lat_min (Optional[float], optional): minimum latitude. Defaults to None.
            lat_max (Optional[float], optional): maximum latitude. Defaults to None.
            lon_min (Optional[float], optional): minimum longitude. Defaults to None.
            lon_max (Optional[float], optional): maximum longitude. Defaults to None.
        """
        # Parse arguments
        if not isinstance(limit, int) or limit < 0:
            log_and_raise(ValueError, f'Query limit not an integer >= 0 ({limit})')
        is_not_none = [val is not None for val in (lat_min, lat_max, lon_min, lon_max)]
        if any(is_not_none) and not all(is_not_none):
            log_and_raise(ValueError, 'Not all bounding box values are specified')
        if any(is_not_none):
            if not all(isinstance(val, (int, float)) for val in (lat_min, lat_max,
                                                                 lon_min, lon_max)):
                log_and_raise(ValueError, 'Not all bounding box values are numeric')

        # Store values
        self.limit: int = limit
        self.bbox: Optional[tuple[float, float, float, float]] = None
        if any(is_not_none):
            self.bbox = (lat_min, lat_max, lon_min, lon_max)

    async def from_cache(self, states: list[State]) -> list[State]:
        """Filter a cached list of states using stored settings

        Args:
            states (list[State]): cached list of states

        Returns:
            list[State]: filtered list of states
        """
        # Require latitude and longitude fields
        states = filter_states(states, 'latitude', 'longitude')
        logger.debug(f'Retrieved {len(states)} from cache')

        # Filter bounding box
        if self.bbox is not None:
            lat_min, lat_max, lon_min, lon_max = self.bbox
            wrapped_boxes = normalize_longitude_bbox(lon_min, lon_max)
            filtered = []
            for box_min, box_max in wrapped_boxes:
                filtered.extend(state for state in states if lat_min <= state.latitude <= lat_max 
                                and box_min <= state.longitude <= box_max)
            states = filtered
            logger.debug(f'Filtered to {len(states)} by bbox ({self.bbox})')

        # Return states (limit if specified)
        if self.limit > 0:
            states = states[:self.limit]
            logger.debug(f'Filtered to {len(states)} by limit ({self.limit})')
    
        # Map states to longitude range
        for state in states:
            state.longitude = shift_longitude_into_range(state.longitude,
                                                         self.bbox[2], self.bbox[3])
        logger.info(f'Retrieved {len(states)} matching states from cache')
        return states

    async def from_server(self, table: str, db: DatabaseManager) -> list[State]:
        """Query a list of states from server database

        Args:
            table (str): name of database table
            db (DatabaseManager): database manager instance

        Returns:
            list[State]: selected list of states
        """
        # Create query to select latest batch from table
        query = f'SELECT * FROM {table} WHERE time=(SELECT MAX(time) FROM {table})'

        # Filter bounding box (normalize longitude to allow for map wrapping)
        if self.bbox is not None:
            lat_min, lat_max, lon_min, lon_max = self.bbox
            wrapped_boxes = normalize_longitude_bbox(lon_min, lon_max)
            conditions = []
            for box_min, box_max in wrapped_boxes:
                conditions.append(f'(latitude BETWEEN {lat_min} AND {lat_max}' + \
                                  f' AND longitude BETWEEN {box_min} AND {box_max})')
            query += f" AND ({' OR '.join(conditions)})"

        # Add query limit (if specified)
        if self.limit > 0:
            query += f' LIMIT {self.limit}'

        # Get states with query
        logger.debug(f'Querying server with "{query}"...')
        rows = await db.sql_query(query)
        logger.info(f'Retrieved {len(rows)} matching states from server')
        states = filter_states([self.parse_table_row(row) for row in rows], 'latitude', 'longitude')

        # Map states to longitude range
        for state in states:
            state.longitude = shift_longitude_into_range(state.longitude,
                                                         self.bbox[2], self.bbox[3])
        return states


    def parse_table_row(self, raw_entry: tuple) -> State:
        """Parse raw table data into a State

        Args:
            raw_entry (tuple): raw table data

        Returns:
            State: corresponding State
        """
        return State.from_raw(raw_entry)


class NearbyQuery(TableQuery[State]):
    """Query to select aircraft within a radius from a specified point"""

    allows_cache = True

    def __init__(self, lat: float, lon: float, radius: float = 50., limit: int = 0) -> None:
        """Initialize query with parameters

        Args:
            lat (float): latitude of point
            lon (float): longitude of point
            radius (float, optional): radius from specified points [km]. Defaults to 50.0 km.
            limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).
        """
        # Parse arguments
        if not isinstance(limit, int) or limit < 0:
            log_and_raise(ValueError, f'Query limit not an integer >= 0 ({limit})')
        if not isinstance(radius, (int, float)) or radius <= 0:
            log_and_raise(ValueError, f'Radius not a float larger than 0 ({radius})')
        if not isinstance(lat, (int, float)) or lat < -90 or lat > 90:
            log_and_raise(ValueError, f'Latitude not a float between -90 and 90 ({lat})')
        if not isinstance(lon, (int, float)) or lon < -180 or lon > 180:
            log_and_raise(ValueError, f'Longitude not a float between -180 and 180 ({lon})')

        # Store values
        self.limit: int = limit
        self.point: tuple[float, float] = (lat, lon)
        self.radius: float = radius

    async def from_cache(self, states: list[State]) -> list[State]:
        """Filter a cached list of states using stored settings

        Args:
            states (list[State]): cached list of states

        Returns:
            list[State]: filtered list of states
        """
        # Require latitude and longitude fields
        states = filter_states(states, 'latitude', 'longitude')
        logger.debug(f'Retrieved {len(states)} from cache')

        # Filter radius
        states = [state for state in states if distance_between_points(state.latitude,
                                                                       state.longitude,
                                                                       *self.point) <= self.radius]
        logger.debug(f'Filtered to {len(states)} by radius ({self.radius} km)')

        # Returns states (limit if specified)
        if self.limit > 0:
            states = states[:self.limit]
            logger.debug(f'Filtered to {len(states)} by limit ({self.limit})')
        
        logger.info(f'Retrieved {len(states)} matching states from cache')
        return states

    async def from_server(self, table: str, db: DatabaseManager) -> list[State]:
        """Query a list of states from server database

        Args:
            table (str): name of database table
            db (DatabaseManager): database manager instance

        Returns:
            list[State]: selected list of states
        """
        # Create query to select latest batch from table
        query = f'SELECT * FROM {table} WHERE time=(SELECT MAX(time) FROM {table})'

        # Filter radius
        lat_rad, lon_rad = radians(self.point[0]), radians(self.point[1])
        earth_radius = 6371.
        query += f' AND {earth_radius} * ACOS(SIN(RADIANS(latitude)) * SIN({lat_rad}) ' + \
                 f'+ COS(RADIANS(latitude)) * COS({lat_rad}) * COS(RADIANS(longitude) ' + \
                 f'- {lon_rad})) <= {self.radius}'

        # Add limit (if specified)
        if self.limit > 0:
            query += f' LIMIT {self.limit}'

        # Return query result
        logger.debug(f'Querying database with "{query}"...')
        rows = await db.sql_query(query)
        logger.info(f'Retrieved {len(rows)} matching states from server')
        return filter_states([self.parse_table_row(row) for row in rows], 'latitude', 'longitude')

    def parse_table_row(self, raw_entry: tuple) -> State:
        """Parse raw table data into a State

        Args:
            raw_entry (tuple): raw table data

        Returns:
            State: corresponding State
        """
        return State.from_raw(raw_entry)


class TrackQuery(TableQuery[State]):
    """Query to select track history of an aircraft"""

    allows_cache = False

    def __init__(self, icao24: str, duration: str, limit: int = 0) -> None:
        """Initialize query with parameters

        Args:
            icao24 (str): aircraft ICAO 24-bit address (hex code)
            duration (str): track duration
            limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).
        """
        # Parse arguments
        if not isinstance(limit, int) or limit < 0:
            log_and_raise(ValueError, f'Query limit not an integer >= 0 ({limit})')
        if not isinstance(icao24, str) or len(icao24) != 6:
            log_and_raise(ValueError, f'ICAO code not a 6-character string ({icao24})')
        if not isinstance(duration, str):
            log_and_raise(ValueError, f'Duration not a string ({duration})')
        
        # Store values
        self.icao24: str = icao24
        self.start_timestamp: int = int(datetime_ago_from_time_string(duration).timestamp())
        self.limit: int = limit
    
    async def from_cache(self, _) -> None:
        """Filter a cached list of states

        Raises:
            ValueError: track query does not support cache
        """
        raise ValueError('Track query cannot use cache')
    
    async def from_server(self, table: str, db: DatabaseManager) -> list[State]:
        """Query a list of states from server database

        Args:
            table (str): name of database table
            db (DatabaseManager): database manager instance

        Returns:
            list[State]: selected list of states
        """
        # Create query to select specific aircraft history (time descending)
        query = f"SELECT * FROM {table} WHERE icao24='{self.icao24}'"

        # Filter by duration
        query += f' AND time >= {self.start_timestamp}'

        # Order by descending time
        query += ' ORDER BY time DESC'

        # Add limit (if specified)
        if self.limit > 0:
            query += f' LIMIT {self.limit}'

        # Return query result
        logger.debug(f'Querying server with "{query}"...')
        rows = await db.sql_query(query)
        logger.info(f'Retrieved {len(rows)} matching states from server')
        return filter_states([self.parse_table_row(row) for row in rows], 'latitude', 'longitude')

    def parse_table_row(self, raw_entry: tuple) -> State:
        """Parse raw table data into a State

        Args:
            raw_entry (tuple): raw table data

        Returns:
            State: corresponding State
        """
        return State.from_raw(raw_entry)
