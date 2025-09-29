"""State models"""
from datetime import datetime
from enum import IntEnum

from pydantic import BaseModel

from skytracker.utils import log_and_raise


class StateDataSource(IntEnum):
    """Source of state data"""

    OPENSKY_NETWORK: int = 1
    """int: OpenSky Network API"""
    AVIATION_EDGE: int = 2
    """int: Aviation Edge API"""


class StateStatus(IntEnum):
    """State status"""

    EMPTY: int = 1
    """int: no given state"""
    UNKNOWN: int = 2
    """int: unknown"""
    EN_ROUTE: int = 3
    """int: en-route"""
    LANDED: int = 4
    """int: landed"""
    STARTED: int = 5
    """int: started"""

    @classmethod
    def from_string(cls, value: str) -> int:
        """Get state status from a string

        Args:
            value (str): string to parse

        Returns:
            int: state status
        """
        if not len(value):
            return cls.EMPTY
        if value.lower() == 'unknown':
            return cls.UNKNOWN
        if value.lower() in ('en-route', 'enroute'):
            return cls.EN_ROUTE
        if value.lower() == 'landed':
            return cls.LANDED
        if value.lower() == 'started':
            return cls.STARTED
        log_and_raise(ValueError, f'Unknown state status: {value}')


class State(BaseModel):
    """Aircraft state data"""

    time: datetime
    """datetime: data timestamp"""
    data_source: StateDataSource
    """StateDataSource: source of state data"""

    aircraft_iata: str
    """str: aircraft IATA code (max. 4 characters)"""
    aircraft_icao: str
    """str: aircraft ICAO code (max. 4 characters)"""
    aircraft_icao24: str
    """str: aircraft ICAO 24-bit address (hex) (6 characters)"""
    aircraft_registration: str
    """str: aircraft registration (max. 8 characters)"""

    airline_iata: str
    """str: airline IATA code (2 characters)"""
    airline_icao: str
    """str: airline ICAO code (3 characters)"""

    arrival_iata: str
    """str: arrival airport IATA code (3 characters)"""
    arrival_icao: str
    """str: arrival airport ICAO code (4 characters)"""

    departure_iata: str
    """str: departure airport IATA code (3 characters)"""
    departure_icao: str
    """str: departure airport ICAO code (4 characters)"""

    position: tuple[float, float] | None
    """tuple[float, float] | None: latitude/longitude position [deg]"""
    geo_altitude: float | None
    """float | None: geometric altitude [m]"""
    baro_altitude: float | None
    """float | None: barometric altitude [m]"""
    heading: float | None
    """float | None: heading [deg]"""
    speed_horizontal: float | None
    """float | None: horizontal speed [m/s]"""
    speed_vertical: float | None
    """float | None: vertical speed [m/s]"""
    is_on_ground: bool
    """bool: whether aircraft is on ground"""

    status: StateStatus
    """StateStatus: aircraft status"""
    squawk: int | None
    """int | None: squawk code (can be None)"""
    squawk_time: datetime | None
    """datetime | None: squawk update time (Unix timestamp)"""
