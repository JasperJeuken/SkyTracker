"""Aviation Edge API models"""
from typing import Annotated, List, Iterator

from pydantic import BaseModel, RootModel, Field


class AviationEdgeAircraft(BaseModel):
    """Aviation Edge API aircraft data"""

    iataCode: Annotated[str, Field(description='Aircraft IATA code')]
    """str: aircraft IATA code"""
    icaoCode: Annotated[str, Field(description='Aircraft ICAO code')]
    """str: aircraft ICAO code"""
    icao24: Annotated[str, Field(description='Aircraft ICAO 24-bit address (hex)')]
    """str: aircraft ICAO 24-bit address (hex)"""
    regNumber: Annotated[str, Field(description='Aircraft registration number')]
    """str: aircraft registration number"""


class AviationEdgeAirline(BaseModel):
    """Aviation Edge API airline data"""

    iataCode: Annotated[str, Field(description='Airline IATA code')]
    """str: airline IATA code"""
    icaoCode: Annotated[str, Field(description='Airline ICAO code')]
    """str: airline ICAO code"""


class AviationEdgeAirport(BaseModel):
    """Aviation Edge API airport data"""

    iataCode: Annotated[str, Field(description='Airport IATA code')]
    """str: airport IATA code"""
    icaoCode: Annotated[str, Field(description='Airport ICAO code')]
    """str: airport ICAO code"""


class AviationEdgeFlight(BaseModel):
    """Aviation Edge API flight data"""

    iataNumber: Annotated[str, Field(description='Flight IATA number')]
    """str: flight IATA number"""
    icaoNumber: Annotated[str, Field(description='Flight ICAO number')]
    """str: flight ICAO number"""
    number: Annotated[str, Field(description='Flight number')]
    """str: flight number"""


class AviationEdgeGeography(BaseModel):
    """Aviation Edge API geography data"""

    altitude: Annotated[float, Field(description='Aircraft altitude [m]')]
    """float: aircraft altitude [m]"""
    direction: Annotated[float, Field(description='Aircraft heading [deg]')]
    """float: aircraft heading [deg]"""
    latitude: Annotated[float, Field(description='Aircraft latitude [deg]')]
    """float: aircraft latitude [deg]"""
    longitude: Annotated[float, Field(description='Aircraft longitude [deg]')]
    """float: aircraft longitude [deg]"""


class AviationEdgeSpeed(BaseModel):
    """Aviation Edge API speed data"""

    horizontal: Annotated[float, Field(description='Aircraft horizontal speed [km/h]')]
    """float: aircraft horizontal speed [km/h]"""
    isGround: Annotated[bool, Field(description='Whether aircraft is on ground')]
    """bool: whether aircraft is on ground"""
    vspeed: Annotated[float, Field(description='Aircraft vertical speed [km/h]')]
    """float: aircraft vertical speed"""


class AviationEdgeSystem(BaseModel):
    """Aviation Edge API system data"""

    squawk: Annotated[str | None, Field(description='Aircraft squawk code')]
    """str | None: aircraft squawk code"""
    updated: Annotated[int, Field(description='Aircraft squawk code update time (Unix)')]
    """int: aircraft squawk code update time (Unix)"""


class AviationEdgeState(BaseModel):
    """Aviation Edge API response data"""

    aircraft: Annotated[AviationEdgeAircraft, Field(description='Aircraft data')]
    """AviationEdgeAircraft: aircraft data"""
    airline: Annotated[AviationEdgeAirline, Field(description='Airline data')]
    """AviationEdgeAirline: airline data"""
    arrival: Annotated[AviationEdgeAirport, Field(description='Arrival airport data')]
    """AviationEdgeAirport: arrival airport data"""
    departure: Annotated[AviationEdgeAirport, Field(description='Departure airport data')]
    """AviationEdgeAirport: departure airport data"""
    geography: Annotated[AviationEdgeGeography, Field(description='Aircraft geography data')]
    """AviationEdgeGeography: aircraft geography data"""
    speed: Annotated[AviationEdgeSpeed, Field(description='Aircraft speed data')]
    """AviationEdgeSpeed: aircraft speed data"""
    status: Annotated[str, Field(description='Aircraft status')]
    """str: aircraft status"""
    system: Annotated[AviationEdgeSystem, Field(description='Aircraft system data')]
    """AviationEdgeSystem: aircraft system data"""


class AviationEdgeResponse(RootModel):
    """Aviation Edge API response data"""

    root: Annotated[List[AviationEdgeState], Field(description='Aircraft states')]
    """List[AviationEdgeState]"""

    def __iter__(self) -> Iterator:
        """Get state iterator
        
        Returns:
            Iterator: state iterator
        """
        return iter(self.root)
    
    def __len__(self) -> int:
        """Get number of states
        
        Returns:
            int: number of states
        """
        return len(self.root)
    
    def __getitem__(self, index: int) -> AviationEdgeState:
        """Get a state from the state list

        Args:
            index (int): index of state to get

        Returns:
            AviationEdgeState: indexed state
        """
        return self.root[index]
