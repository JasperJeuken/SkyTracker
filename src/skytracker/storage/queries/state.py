"""State table queries"""
from datetime import datetime, timezone

from skytracker.storage.table_query import TableQuery
from skytracker.models.state import (State, StateAircraft, StateAirline, StateAirport, StateFlight,
                                     StateGeography, StateTransponder)
from skytracker.models import unflatten_model
from skytracker.storage.database_manager import DatabaseManager
from skytracker.utils.conversions import datetime_ago_from_time_string
from skytracker.utils.geographic import (distance_between_points, normalize_longitude_bbox,
                                         shift_longitude_into_range)
from skytracker.utils import logger, log_and_raise


class LatestBatchQuery(TableQuery[State]):
    """Query to select the latest aircraft states (with optional bounding box)"""

    allows_cache = True

    def __init__(self, limit: int = 0,
                 lat_min: float | None = None, lat_max: float | None = None,
                 lon_min: float | None = None, lon_max: float | None = None,
                 fields: list[str] = None) -> None:
        """Initialize query with optional arguments

        Args:
            limit (int, optional): maximum number of states to get (0=all). Defaults to 0.
            lat_min (float, optional): minimum latitude. Defaults to None.
            lat_max (float, optional): maximum latitude. Defaults to None.
            lon_min (float, optional): minimum longitude. Defaults to None.
            lon_max (float, optional): maximum longitude. Defaults to None.
            fields (list[str], optional): names of fields in flattened table. Defaults to None.
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
        self.bbox: tuple[float, float, float, float] | None = None
        if any(is_not_none):
            self.bbox = (lat_min, lat_max, lon_min, lon_max)
        self.fields: list[str] = fields if fields is not None else []

    async def from_cache(self, states: list[State]) -> list[State]:
        """Filter a cached list of states using stored settings

        Args:
            states (list[State]): cached list of states

        Returns:
            list[State]: filtered list of states
        """
        logger.debug(f'Retrieved {len(states)} from cache')

        # Filter bounding box
        if self.bbox is not None:
            lat_min, lat_max, lon_min, lon_max = self.bbox
            wrapped_boxes = normalize_longitude_bbox(lon_min, lon_max)
            filtered = []
            for box_min, box_max in wrapped_boxes:
                filtered.extend(state for state in states \
                                if lat_min <= state.geography.position[0] <= lat_max 
                                and box_min <= state.geography.position[1] <= box_max)
            states = filtered
            logger.debug(f'Filtered to {len(states)} by bbox ({self.bbox})')

        # Return states (limit if specified)
        if self.limit > 0:
            states = states[:self.limit]
            logger.debug(f'Filtered to {len(states)} by limit ({self.limit})')
    
        # Map states to longitude range
        if self.bbox is not None:
            for state in states:
                longitude = shift_longitude_into_range(state.geography.position[1],
                                                       self.bbox[2], self.bbox[3])
                state.geography.position = (state.geography.position[0], longitude)
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
                conditions.append(f'(geography__position.1 BETWEEN {lat_min} AND {lat_max}' + \
                                  f' AND geography__position.2 BETWEEN {box_min} AND {box_max})')
            query += f" AND ({' OR '.join(conditions)})"

        # Add query limit (if specified)
        if self.limit > 0:
            query += f' LIMIT {self.limit}'

        # Get states with query
        logger.debug(f'Querying server with "{query}"...')
        rows = await db.sql_query(query)
        logger.info(f'Retrieved {len(rows)} matching states from server')
        states = [self.parse_table_row(row) for row in rows]

        # Map states to longitude range
        if self.bbox is not None:
            for state in states:
                longitude = shift_longitude_into_range(state.geography.position[1],
                                                       self.bbox[2], self.bbox[3])
                state.geography.position = (state.geography.position[0], longitude)
        return states

    def parse_table_row(self, raw_entry: tuple) -> State:
        """Parse raw table data into a State

        Args:
            raw_entry (tuple): raw table data

        Returns:
            State: corresponding State
        """
        unflattened = unflatten_model(dict(zip(self.fields, raw_entry)), State)
        return State.model_validate(unflattened)


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
        logger.debug(f'Retrieved {len(states)} from cache')

        # Filter radius
        states = [state for state in states if distance_between_points(state.geography.position[0],
                                                                       state.geography.position[1],
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
        query = f'SELECT flight__icao, geography__position, geography__heading FROM {table} ' + \
                f'WHERE time=(SELECT MAX(time) FROM {table})'

        # Filter radius
        query += ' AND greatCircleDistance(geography__position.2, geography__position.1, ' + \
                 f'{self.point[1]}, {self.point[0]}) <= {self.radius * 1e3}'

        # Add limit (if specified)
        if self.limit > 0:
            query += f' LIMIT {self.limit}'

        # Return query result
        logger.debug(f'Querying database with "{query}"...')
        rows = await db.sql_query(query)
        logger.info(f'Retrieved {len(rows)} matching states from server')
        return [self.parse_table_row(row) for row in rows]

    def parse_table_row(self, raw_entry: tuple) -> State:
        """Parse raw table data into a State

        Args:
            raw_entry (tuple): raw table data

        Returns:
            State: corresponding State
        """
        return State(
            time=datetime.fromtimestamp(0, tz=timezone.utc),
            data_source=1,
            status=1,
            aircraft=StateAircraft(
                iata=None,
                icao=None,
                icao24=None,
                registration=None
            ),
            airline=StateAirline(
                iata=None,
                icao=None
            ),
            airport=StateAirport(
                arrival_iata=None,
                arrival_icao=None,
                departure_iata=None,
                departure_icao=None
            ),
            flight=StateFlight(
                iata=None,
                icao=raw_entry[0],
                number=None
            ),
            geography=StateGeography(
                position=raw_entry[1],
                geo_altitude=None,
                baro_altitude=None,
                heading=raw_entry[2],
                speed_horizontal=None,
                speed_vertical=None,
                is_on_ground=False
            ),
            transponder=StateTransponder(
                squawk=None,
                squawk_time=None
            )            
        )


class TrackQuery(TableQuery[State]):
    """Query to select track history of an aircraft"""

    allows_cache = False

    def __init__(self, callsign: str, duration: str, limit: int = 0) -> None:
        """Initialize query with parameters

        Args:
            callsign (str): aircraft callsign (ICAO)
            duration (str): track duration
            limit (int, optional): maximum number of states to get (0=all). Defaults to 0 (all).
        """
        # Parse arguments
        if not isinstance(limit, int) or limit < 0:
            log_and_raise(ValueError, f'Query limit not an integer >= 0 ({limit})')
        if not isinstance(callsign, str):
            log_and_raise(ValueError, f'Callsign not a string ({callsign})')
        if not isinstance(duration, str):
            log_and_raise(ValueError, f'Duration not a string ({duration})')
        
        # Store values
        self.callsign: str = callsign
        self.limit: int = limit
        start = datetime_ago_from_time_string(duration)
        self.start_timestamp: datetime = datetime(start.year, start.month, start.day,
                                                  start.hour, start.minute, start.second)
    
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
        query = 'SELECT time, flight__icao, geography__position, geography__baro_altitude, ' + \
            f"geography__heading FROM {table} WHERE flight__icao='{self.callsign}'"

        # Filter by duration
        query += f" AND time >= '{self.start_timestamp}'::DateTime('UTC')"

        # Order by descending time
        query += ' ORDER BY time DESC'

        # Add limit (if specified)
        if self.limit > 0:
            query += f' LIMIT {self.limit}'

        # Return query result
        logger.debug(f'Querying server with "{query}"...')
        rows = await db.sql_query(query)
        logger.info(f'Retrieved {len(rows)} matching states from server')
        return [self.parse_table_row(row) for row in rows]

    def parse_table_row(self, raw_entry: tuple) -> State:
        """Parse raw table data into a State

        Args:
            raw_entry (tuple): raw table data

        Returns:
            State: corresponding State
        """
        return State(
            time=raw_entry[0],
            data_source=1,
            status=1,
            aircraft=StateAircraft(
                iata=None,
                icao=None,
                icao24=None,
                registration=None
            ),
            airline=StateAirline(
                iata=None,
                icao=None
            ),
            airport=StateAirport(
                arrival_iata=None,
                arrival_icao=None,
                departure_iata=None,
                departure_icao=None
            ),
            flight=StateFlight(
                iata=None,
                icao=raw_entry[1],
                number=None
            ),
            geography=StateGeography(
                position=raw_entry[2],
                geo_altitude=None,
                baro_altitude=raw_entry[3],
                heading=raw_entry[4],
                speed_horizontal=None,
                speed_vertical=None,
                is_on_ground=False
            ),
            transponder=StateTransponder(
                squawk=None,
                squawk_time=None
            )            
        )
