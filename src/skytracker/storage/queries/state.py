"""State table queries"""
from typing import Optional
from math import radians

from skytracker.storage.table_query import TableQuery
from skytracker.models.state import State
from skytracker.storage.database_manager import DatabaseManager
from skytracker.utils.analysis import filter_states
from skytracker.utils.geographic import distance_between_points


class LatestBatchQuery(TableQuery):
    """Query to select the latest aircraft states (with optional bounding box)"""

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
            raise ValueError(f'Query limit must be an integer larger than 0, got "{limit}".')
        is_not_none = [val is not None for val in (lat_min, lat_max, lon_min, lon_max)]
        if any(is_not_none) and not all(is_not_none):
            raise ValueError('All bounding box values must be specified')
        if any(is_not_none):
            if not all(isinstance(val, (int, float)) for val in (lat_min, lat_max,
                                                                 lon_min, lon_max)):
                raise ValueError('All bounding box values must be numeric')
            if not (-90 <= lat_min <= 90) or not (-90 <= lat_max <= 90) or lat_min >= lat_max:
                raise ValueError('Latitude must be a float (or integer) between -90 and 90 ' + \
                                 f'degrees, got "{lat_min}" and "{lat_max}".')
            if not (-180 <= lon_min <= 180) or not (-180 <= lon_max <= 180) or lon_min >= lon_max:
                raise ValueError('Longitude must be a float (or integer) between -180 and 180 ' + \
                                 f'degrees, got "{lon_min}" and "{lon_max}".')

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

        # Filter bounding box
        if self.bbox is not None:
            lat_min, lat_max, lon_min, lon_max = self.bbox
            states = [state for state in states if lat_min <= state.latitude <= lat_max and \
                                                   lon_min <= state.longitude <= lon_max]
        
        # Return states (limit if specified)
        if self.limit > 0:
            return states[:self.limit]
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

        # Filter bounding box
        if self.bbox is not None:
            lat_min, lat_max, lon_min, lon_max = self.bbox
            query += f' AND latitude BETWEEN {lat_min} AND {lat_max}' + \
                     f' AND longitude BETWEEN {lon_min} AND {lon_max}'
        
        # Add query limit (if specified)
        if self.limit > 0:
            query += f' LIMIT {self.limit}'
        
        # Return query result
        return await db.sql_query(query)


class NearbyQuery(TableQuery):
    """Query to select aircraft within a radius from a specified point"""

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
            raise ValueError(f'Query limit must be an integer larger than 0, got "{limit}".')
        if not isinstance(radius, (int, float)) or radius <= 0:
            raise ValueError(f'Radius must be a float (or integer) larger than 0, got "{radius}".')
        if not isinstance(lat, (int, float)) or lat < -90 or lat > 90:
            raise ValueError('Latitude must be a float (or integer) between -90 and 90 ' + \
                             f'degrees, got "{lat}".')
        if not isinstance(lon, (int, float)) or lon < -180 or lon > 180:
            raise ValueError('Longitude must be a float (or integer) between -180 and 180 ' + \
                             f'degrees, got "{lon}".')
        
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

        # Filter radius
        states = [state for state in states if distance_between_points(state.latitude,
                                                                       state.longitude,
                                                                       *self.point) <= self.radius]
        
        # Returns states (limit if specified)
        if self.limit > 0:
            return states[:self.limit]
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
        return await db.sql_query(query)
