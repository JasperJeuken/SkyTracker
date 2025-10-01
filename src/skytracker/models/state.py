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

    time: Annotated[datetime, Field(description='Data timestamp')]
    """datetime: data timestamp"""
    data_source: Annotated[StateDataSource, Field(description='Source of state data')]
    """APIType: source of state data"""

    aircraft_iata: Annotated[str, Field(description='Aircraft IATA code')]
    """str: aircraft IATA code (max. 4 characters)"""
    aircraft_icao: Annotated[str, Field(description='Aircraft ICAO code')]
    """str: aircraft ICAO code (max. 4 characters)"""
    aircraft_icao24: Annotated[str, Field(description='Aircraft ICAO 24-bit address (hex)')]
    """str: aircraft ICAO 24-bit address (hex) (6 characters)"""
    aircraft_registration: Annotated[str, Field(description='Aircraft registration')]
    """str: aircraft registration (max. 8 characters)"""

    airline_iata: Annotated[str, Field(description='Airline IATA code')]
    """str: airline IATA code (2 characters)"""
    airline_icao: Annotated[str, Field(description='Airline ICAO code')]
    """str: airline ICAO code (3 characters)"""

    arrival_iata: Annotated[str, Field(description='Arrival airport IATA code')]
    """str: arrival airport IATA code (3 characters)"""
    arrival_icao: Annotated[str, Field(description='Arrival airport ICAO code')]
    """str: arrival airport ICAO code (4 characters)"""

    departure_iata: Annotated[str, Field(description='Departure airport IATA code')]
    """str: departure airport IATA code (3 characters)"""
    departure_icao: Annotated[str, Field(description='Departure airport ICAO code')]
    """str: departure airport ICAO code (4 characters)"""

    flight_iata: Annotated[str, Field(description='Flight IATA code')]
    """str: flight IATA code"""
    flight_icao: Annotated[str, Field(description='Flight ICAO code')]
    """str: flight ICAO code"""
    flight_number: Annotated[str, Field(description='Flight number')]
    """str: flight number"""

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

    status: Annotated[StateStatus, Field(description='Aircraft status')]
    """StateStatus: aircraft status"""
    squawk: Annotated[int | None, Field(description='Squawk code')]
    """int | None: squawk code (can be None)"""
    squawk_time: Annotated[datetime | None, Field(description='Squawk code update time')]
    """datetime | None: squawk update time"""

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

    def values(self) -> list[Any]:
        """Get the values in the state as a list

        Returns:
            list[Any]: list of state values
        """
        return [
            self.time,
            self.data_source.value,
            self.aircraft_iata[:4],
            self.aircraft_icao[:4],
            self.aircraft_icao24[:6],
            self.aircraft_registration[:10],
            self.airline_iata[:3],
            self.airline_icao[:3],
            self.arrival_iata[:3],
            self.arrival_icao[:4],
            self.departure_iata[:3],
            self.departure_icao[:4],
            self.flight_iata[:7],
            self.flight_icao[:8],
            self.flight_number[:4],
            self.position,
            self.geo_altitude,
            self.baro_altitude,
            self.heading,
            self.speed_horizontal,
            self.speed_vertical,
            self.is_on_ground,
            self.status.value,
            self.squawk,
            self.squawk_time
        ]


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
