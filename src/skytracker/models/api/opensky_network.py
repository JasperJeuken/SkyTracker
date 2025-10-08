"""OpenSky Network API models"""
from datetime import datetime, timezone
from typing import List, Annotated, Any, Literal, get_args

from pydantic import BaseModel, Field, model_validator

from skytracker.models.api import APIResponse, APIType
from skytracker.models.state import (State, StateStatus, StateAircraft, StateAirline, StateAirport,
                                     StateDataSource, StateFlight, StateGeography, StateTransponder)


StateFields = Literal['icao24', 'callsign', 'origin_country', 'time_position', 'last_contact',
                      'longitude', 'latitude', 'baro_altitude', 'on_ground', 'velocity',
                      'true_track', 'vertical_rate', 'sensors', 'geo_altitude', 'squawk', 'spi',
                      'position_source', 'category']


class OpenSkyNetworkState(BaseModel):
    """OpenSky Network API state data"""

    icao24: Annotated[str, Field(description='Aircraft ICAO 24-bit address (hex)')]
    """str: aircraft ICAO 24-bit address (hex)"""
    callsign: Annotated[str | None, Field(description='Aircraft callsign')]
    """str | None: aircraft callsign"""
    origin_country: Annotated[str, Field(description='Aircraft origin country')]
    """str: aircraft origin country"""
    time_position: Annotated[int | None, Field(description='Last position update timestamp (Unix)')]
    """int | None: last position update timestamp (Unix)"""
    last_contact: Annotated[int | None, Field(description='Last transponder timestamp (Unix)')]
    """int | None: last transponder timestamp (Unix)"""
    longitude: Annotated[float | None, Field(description='Aircraft longitude [deg]')]
    """float | None: aircraft longitude [deg]"""
    latitude: Annotated[float | None, Field(description='Aircraft latitude [deg]')]
    """float | None: aircraft latitude [deg]"""
    baro_altitude: Annotated[float | None, Field(description='Aircraft barometric altitude [m]')]
    """float | None: barometric altitude [m]"""
    on_ground: Annotated[bool, Field(description='Whether aircraft is on ground')]
    """bool: whether aircraft is on ground"""
    velocity: Annotated[float | None, Field(description='Aircraft velocity [m/s]')]
    """float | None: aircraft velocity [m/s]"""
    true_track: Annotated[float | None, Field(description='Aircraft true track [deg]')]
    """float | None: aircraft true track [deg]"""
    vertical_rate: Annotated[float | None, Field(description='Aircraft vertical rate [m/s]')]
    """float | None: aircraft vertical rate [m/s]"""
    sensors: Annotated[List[int] | None, Field(description='IDs of receivers which captured state')]
    """List[int] | None: IDs of receivers which captured state"""
    geo_altitude: Annotated[float | None, Field(description='Aircraft geometric altitude [m]')]
    """float | None: aircraft barometric altitude [m]"""
    squawk: Annotated[str | None, Field(description='Transponder squawk code')]
    """str | None: transponder squawk code"""
    spi: Annotated[bool, Field(description='Special purpose indicator')]
    """bool: special purpose indicator"""
    position_source: Annotated[int, Field(description='Origin of the state position')]
    """int: origin of the state position"""
    category: Annotated[int, Field(0, description='Aircraft category')]
    """int: aircraft category"""

    @model_validator(mode='before')
    def parse_from_list(cls, values: Any) -> dict[StateFields, Any]:
        """Parse a list of values into a OpenSky Network API state

        Args:
            values (list[Any]): list of values

        Returns:
            dict[StateFields, Any]: OpenSky Network API state entries
        """
        # Return values if not a list
        if not isinstance(values, list):
            return values
        
        # Match values to names
        names = get_args(StateFields)
        if len(values) == len(names) - 1:
            values.append(0)  # temporary workaround: aircraft database offline
        if len(values) != len(names):
            raise ValueError('Values provided to OpenSky Network API state not valid ' + \
                                f'(expected len={len(names)}, got len={len(values)})')
        return dict(zip(names, values))


class OpenSkyNetworkResponse(BaseModel, APIResponse):
    """OpenSky Network API response data"""

    time: Annotated[int, Field(description='response timestamp (Unix)')]
    """int: response timestamp (Unix)"""
    states: Annotated[List[OpenSkyNetworkState], Field(description='Aircraft states')]
    """List[OpenSkyNetworkState]: aircraft states"""

    def to_states(self) -> list[State]:
        """Convert Aviation Edge API response to list of aircraft states

        Returns:
            list[State]: list of aircraft states
        """
        return [State(
            time=datetime.fromtimestamp(self.time, tz=timezone.utc),
            data_source=StateDataSource.OPENSKY_NETWORK,
            status=StateStatus.UNKNOWN,
            aircraft=StateAircraft(
                iata=None,
                icao=None,
                icao24=entry.icao24.upper(),
                registration=entry.callsign.strip() \
                    if entry.callsign is not None and len(entry.callsign.strip()) else None
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
                icao=entry.callsign.strip() \
                    if entry.callsign is not None and len(entry.callsign.strip()) else '',
                number=None
            ),
            geography=StateGeography(
                position=(entry.latitude, entry.longitude) \
                    if entry.latitude is not None and entry.longitude is not None else (0., 0.),
                geo_altitude=entry.geo_altitude,
                baro_altitude=entry.baro_altitude,
                heading=entry.true_track,
                speed_horizontal=entry.velocity,
                speed_vertical=entry.vertical_rate,
                is_on_ground=entry.on_ground
            ),
            transponder=StateTransponder(
                squawk=entry.squawk,
                squawk_time=datetime.fromtimestamp(entry.last_contact) \
                    if entry.last_contact is not None else None
            )
        ) for entry in self.states]
