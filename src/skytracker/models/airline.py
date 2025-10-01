"""Airline endpoint models"""
from typing import Annotated, Any
from enum import IntEnum

from pydantic import BaseModel, Field, field_validator, field_serializer

from skytracker.utils import log_and_raise


class AirlineStatus(IntEnum):
    """Airline status"""

    MERGED: int = 1
    """int: merged with another airline"""
    HISTORICAL: int = 2
    """int: historical airline"""
    DISABLED: int = 3
    """int: disabled airline"""
    NOT_READY: int = 4
    """int: airline not ready"""
    UNKNOWN: int = 5
    """int: unknown status"""
    START_UP: int = 6
    """int: start-up airline"""
    RESTARTING: int = 7
    """int: restarting airline"""
    ACTIVE: int = 8
    """int: active airline"""
    RENAMED: int = 9
    """int: renamed airline"""

    @classmethod
    def from_string(cls, value: str) -> int:
        """Get airline status from a string

        Args:
            value (str): string to parse

        Returns:
            int: airline status
        """
        match value.lower():
            case 'merged':
                return cls.MERGED
            case 'historical' | 'historical/administration':
                return cls.HISTORICAL
            case 'disabled':
                return cls.DISABLED
            case 'not_ready':
                return cls.NOT_READY
            case 'unknown' | '':
                return cls.UNKNOWN
            case 'start_up':
                return cls.START_UP
            case 'restarting':
                return cls.RESTARTING
            case 'active':
                return cls.ACTIVE
            case 'renamed':
                return cls.RENAMED
            case _:
                log_and_raise(ValueError, f'Unknown airline status: {value}')


class AirlineType(IntEnum):
    """Airline type"""

    SCHEDULED: int = 0
    """int: airline with regular scheduled flights"""
    CHARTER: int = 1
    """int: airline with (often contracted) non-scheduled flights"""
    CARGO: int = 2
    """int: airline transporting freight"""
    VIRTUAL: int = 3
    """int: airline that does not operate aircraft directly"""
    LEISURE: int = 4
    """int: airline targets primarily holiday destinations"""
    GOVERNMENT: int = 5
    """int: airline owned by government"""
    PRIVATE: int = 6
    """int: non-commercial operator"""
    MANUFACTURER: int = 7
    """int: aircraft manufacturer"""
    SUPPLIER: int = 8
    """int: company supplying aviation services"""
    DIVISION: int = 9
    """int: subdivision of larger airline"""

    @classmethod
    def from_string(cls, value: str) -> int:
        """Get airline type from a string

        Args:
            value (str): string to parse

        Returns:
            int: airline type
        """
        match value.lower():
            case 'scheduled':
                return cls.SCHEDULED
            case 'charter':
                return cls.CHARTER
            case 'cargo':
                return cls.CARGO
            case 'virtual':
                return cls.VIRTUAL
            case 'leisure':
                return cls.LEISURE
            case 'government':
                return cls.GOVERNMENT
            case 'private':
                return cls.PRIVATE
            case 'manufacturer':
                return cls.MANUFACTURER
            case 'supplier':
                return cls.SUPPLIER
            case 'division':
                return cls.DIVISION
            case _:
                log_and_raise(ValueError, f'Unknown airline status: {value}')


class Airline(BaseModel):
    """Airline data"""

    iata: Annotated[str, Field(description='Airline IATA code')]
    """str: airline IATA code"""
    icao: Annotated[str, Field(description='Airline ICAO code')]
    """str: airline ICAO code"""
    name: Annotated[str, Field(description='Airline name')]
    """str: airline name"""
    callsign: Annotated[str, Field(description='Airline callsign')]
    """str: airline callsign"""
    founding: Annotated[int, Field(description='Airline founding year')]
    """int: airline founding year"""
    fleet_age: Annotated[float, Field(description='Airline fleet age [year]')]
    """float: airline fleet age [year]"""
    fleet_size: Annotated[int, Field(description='Airline fleet size [aircraft]')]
    """int: airline fleet size [aircraft]"""
    status: Annotated[AirlineStatus, Field(description='Airline status')]
    """AirlineStatus: airline status"""
    types: Annotated[list[AirlineType], Field(description='Airline type')]
    """list[AirlineType]: airline types"""
    country_iso2: Annotated[str, Field(description='Country ISO 3166-1 alpha-2 code')]
    """str: country ISO 3166-1 alpha-2 code"""
    hub_icao: Annotated[str | None, Field(description='Airline hub airport ICAO code')]
    """str | None: airline hub airport ICAO code"""

    @field_validator('status', mode='before')
    @classmethod
    def parse_airline_status(cls, value: Any) -> AirlineStatus:
        """Parse airline status value

        Args:
            value (Any): airline status value

        Returns:
            StateDataSource: parsed airline status
        """
        if isinstance(value, str):
            return AirlineStatus.from_string(value)
        return value
    
    @field_validator('types', mode='before')
    @classmethod
    def parse_airline_types(cls, value: Any) -> list[AirlineType]:
        """Parse airline types value

        Args:
            value (Any): airline types value

        Returns:
            list[AirlineType]: parsed airline types
        """
        if isinstance(value, str):
            return [AirlineType.from_string(part.strip()) for part in value.split(',') \
                    if len(part.strip())]
        if isinstance(value, list):
            return [AirlineType.from_string(elem) for elem in value if elem is not None]
        return value
    
    @field_serializer('status')
    @classmethod
    def serialize_airline_status(cls, airline_status: AirlineStatus) -> str:
        """Serialize airline status

        Args:
            airline_status (AirlineStatus): airline status

        Returns:
            str: airline status name
        """
        return airline_status.name
    
    @field_serializer('types')
    @classmethod
    def serialize_airline_types(cls, airline_types: list[AirlineType]) -> list[str]:
        """Serialize airline types

        Args:
            airline_types (list[AirlineType]): airline types

        Returns:
            list[str]: airline type names
        """
        return [airline_type.name for airline_type in airline_types]
