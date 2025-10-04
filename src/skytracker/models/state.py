"""State models"""
from datetime import datetime
from enum import IntEnum
from typing import Any, Annotated

from pydantic import BaseModel, Field, field_validator, field_serializer

from skytracker.utils import log_and_raise


class StateDataSource(IntEnum):
    """State data source"""

    OPENSKY_NETWORK: int = 1
    """int: OpenSky Network API"""
    AVIATION_EDGE: int = 2
    """int: Aviation Edge API"""

    @classmethod
    def from_string(cls, value: str) -> int:
        """Get data source from a string

        Args:
            value (str): string to parse

        Returns:
            int: data source
        """
        if value.lower() in ('opensky', 'opensky-network', 'opensky_network', 'opensky network'):
            return cls.OPENSKY_NETWORK
        if value.lower() in ('aviation-edge', 'aviation_edge', 'aviation edge'):
            return cls.AVIATION_EDGE
        log_and_raise(ValueError, f'Unknown data source: {value}')


class StateStatus(IntEnum):
    """State status"""

    UNKNOWN: int = 1
    """int: unknown"""
    EN_ROUTE: int = 2
    """int: en-route"""
    LANDED: int = 3
    """int: landed"""
    STARTED: int = 4
    """int: started"""

    @classmethod
    def from_string(cls, value: str) -> int:
        """Get state status from a string

        Args:
            value (str): string to parse

        Returns:
            int: state status
        """
        if value.lower() in ('', 'unknown'):
            return cls.UNKNOWN
        if value.lower() in ('en-route', 'enroute', 'en_route'):
            return cls.EN_ROUTE
        if value.lower() == 'landed':
            return cls.LANDED
        if value.lower() == 'started':
            return cls.STARTED
        log_and_raise(ValueError, f'Unknown state status: {value}')


class StateAircraft(BaseModel):
    """State aircraft data"""

    iata: Annotated[str | None, Field(description='Aircraft type IATA code')]
    """str | None: aircraft type IATA code (max. 4 characters)"""
    icao: Annotated[str | None, Field(description='Aircraft type ICAO code')]
    """str | None: aircraft type ICAO code (max. 4 characters)"""
    icao24: Annotated[str | None, Field(description='Aircraft ICAO 24-bit address (hex)')]
    """str | None: aircraft ICAO 24-bit address (hex) (6 characters)"""
    registration: Annotated[str | None, Field(description='Aircraft registration')]
    """str | None: aircraft registration (max. 8 characters)"""


class StateAirline(BaseModel):
    """State airline data"""

    iata: Annotated[str | None, Field(description='Airline IATA code')]
    """str | None: airline IATA code (2 characters)"""
    icao: Annotated[str | None, Field(description='Airline ICAO code')]
    """str | None: airline ICAO code (3 characters)"""


class StateAirport(BaseModel):
    """State airport data"""

    arrival_iata: Annotated[str | None, Field(description='Arrival airport IATA code')]
    """str | None: arrival airport IATA code (3 characters)"""
    arrival_icao: Annotated[str | None, Field(description='Arrival airport ICAO code')]
    """str | None: arrival airport ICAO code (4 characters)"""
    departure_iata: Annotated[str | None, Field(description='Departure airport IATA code')]
    """str | None: departure airport IATA code (3 characters)"""
    departure_icao: Annotated[str | None, Field(description='Departure airport ICAO code')]
    """str | None: departure airport ICAO code (4 characters)"""


class StateFlight(BaseModel):
    """State flight data"""

    iata: Annotated[str | None, Field(description='Flight IATA code')]
    """str | None: flight IATA code"""
    icao: Annotated[str, Field(description='Flight ICAO code')]
    """str: flight ICAO code"""
    number: Annotated[int | None, Field(description='Flight number')]
    """str | None: flight number"""

class StateGeography(BaseModel):
    """State geography data"""

    position: Annotated[tuple[float, float], Field(description='Latitude/longitude position [deg]')]
    """tuple[float, float]: latitude/longitude position [deg]"""
    geo_altitude: Annotated[float | None, Field(description='Geometric altitude [m]')]
    """float | None: geometric altitude [m]"""
    baro_altitude: Annotated[float | None, Field(description='Barometric altitude [m]')]
    """float | None: barometric altitude [m]"""
    heading: Annotated[float | None, Field(description='Heading [deg]')]
    """float | None: heading [deg]"""
    speed_horizontal: Annotated[float | None, Field(description='Horizontal speed [m/s]')]
    """float | None: horizontal speed [m/s]"""
    speed_vertical: Annotated[float | None, Field(description='Vertical speed [m/s]')]
    """float | None: vertical speed [m/s]"""
    is_on_ground: Annotated[bool, Field(description='Whether aircraft is on ground')]
    """bool: whether aircraft is on ground"""


class StateTransponder(BaseModel):
    """State transponder data"""

    squawk: Annotated[int | None, Field(description='Squawk code')]
    """int | None: squawk code (can be None)"""
    squawk_time: Annotated[datetime | None, Field(description='Squawk code update time')]
    """datetime | None: squawk update time"""


class State(BaseModel):
    """Aircraft state data"""

    time: Annotated[datetime, Field(description='Data timestamp')]
    """datetime: data timestamp"""
    data_source: Annotated[StateDataSource, Field(description='Source of state data')]
    """APIType: source of state data"""
    status: Annotated[StateStatus, Field(description='Aircraft status')]
    """StateStatus: aircraft status"""

    aircraft: Annotated[StateAircraft, Field(description='State aircraft data')]
    """StateAircraft: state aircraft data"""
    airline: Annotated[StateAirline, Field(description='State airline data')]
    """StateAirline: state airline data"""
    airport: Annotated[StateAirport, Field(description='State airport data')]
    """StateAirport: state airport data"""
    flight: Annotated[StateFlight, Field(description='State flight data')]
    """StateFlight: state flight data"""
    geography: Annotated[StateGeography, Field(description='State geography data')]
    """StatePosition: state geography data"""
    transponder: Annotated[StateTransponder, Field(description='State transponder data')]
    """StateTransponder: state transponder data"""

    @field_validator('data_source', mode='before')
    @classmethod
    def parse_data_source(cls, value: Any) -> StateDataSource:
        """If data source provided as string, parse

        Args:
            value (Any): data source value

        Returns:
            StateDataSource: parsed data source
        """
        if isinstance(value, str):
            return StateDataSource.from_string(value)
        if isinstance(value, int) and value == 0:
            return StateDataSource.AVIATION_EDGE
        return value

    @field_validator('status', mode='before')
    @classmethod
    def parse_status(cls, value: Any) -> StateStatus:
        """If status provided as string, parse

        Args:
            value (Any): status value

        Returns:
            StateStatus: parsed status
        """
        if isinstance(value, str):
            return StateStatus.from_string(value)
        if isinstance(value, int) and value == 0:
            return StateStatus.UNKNOWN
        return value

    @field_serializer('data_source')
    @classmethod
    def serialize_data_source(cls, data_source: StateDataSource) -> str:
        """Serialize state data source

        Args:
            data_source (StateDataSource): state data source

        Returns:
            str: state data source name
        """
        return data_source.name

    @field_serializer('status')
    @classmethod
    def serialize_status(cls, status: StateStatus) -> str:
        """Serialize state status

        Args:
            data_source (StateStatus): state status

        Returns:
            str: state status name
        """
        return status.name


class SimpleMapState(BaseModel):
    """Simple map state with position and heading"""

    callsign: Annotated[str, Field(description='Aircraft callsign')]
    """str: aircraft callsign"""
    position: Annotated[tuple[float, float], Field(description='Latitude/longitude position [deg]')]
    """tuple[float, float]: latitude/longitude position [deg]"""
    heading: Annotated[float | None, Field(description='Heading [deg]')]
    """float | None: heading [deg]"""


class DetailedMapState(BaseModel):
    """Detailed map state with time, position, heading, and altitude"""

    time: Annotated[datetime, Field(description='State timestamp')]
    """datetime: state timestamp"""
    callsign: Annotated[str, Field(description='Aircraft callsign')]
    """str: aircraft callsign"""
    position: Annotated[tuple[float, float], Field(description='Latitude/longitude position [deg]')]
    """tuple[float, float]: latitude/longitude position [deg]"""
    heading: Annotated[float | None, Field(description='Heading [deg]')]
    """float | None: heading [deg]"""
    altitude: Annotated[float | None, Field(description='Barometric altitude [m]')]
    """float | None: barometric altitude [m]"""
